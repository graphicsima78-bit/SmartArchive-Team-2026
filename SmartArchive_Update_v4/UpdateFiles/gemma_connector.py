import base64
import re
import threading
from pathlib import Path

import requests


class GemmaConnector:
    """ارتباط امن با مدل محلی Gemma Vision در Ollama."""

    SYSTEM_PROMPT = (
        "You are an image classifier. Respond with ONLY ONE WORD from: "
        "person, animal, landscape, plant, food, building, vehicle, object, logo, art, texture, other. "
        "No explanation."
    )

    CATEGORY_DETAILS = {
        "person": ("people", "other"),
        "animal": ("animals", "other"),
        "landscape": ("landscape", "other"),
        "plant": ("plant", "other"),
        "food": ("food", "other"),
        "building": ("building", "other"),
        "vehicle": ("vehicle", "other"),
        "object": ("objects", "other"),
        "logo": ("objects", "logo"),
        "art": ("art_texture", "art"),
        "texture": ("art_texture", "texture"),
        "other": ("images", "other"),
    }

    CATEGORY_ALIASES = {
        "people": "person",
        "human": "person",
        "animals": "animal",
        "plants": "plant",
        "objects": "object",
        "buildings": "building",
        "vehicles": "vehicle",
        "scenery": "landscape",
    }

    PERSIAN_MAPPING = {
        "people": "انسان",
        "animals": "حیوان",
        "landscape": "منظره",
        "plant": "گیاه",
        "food": "غذا",
        "building": "ساختمان",
        "vehicle": "خودرو",
        "objects": "اشیاء",
        "art_texture": "هنر و تکسچر",
        "images": "سایر",
    }

    def __init__(
        self,
        model="gemma3:4b-vision",
        base_url="http://127.0.0.1:11434",
        timeout=180,
    ):
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self._lock = threading.Lock()

    @staticmethod
    def _image_to_base64(image_path: Path) -> str:
        if not image_path.is_file():
            raise FileNotFoundError(f"Image file was not found: {image_path}")
        with image_path.open("rb") as file:
            return base64.b64encode(file.read()).decode("utf-8")

    @classmethod
    def _extract_category(cls, content: str):
        """خروجی کوتاه یا توضیحی مدل را به یکی از دسته‌های مجاز تبدیل می‌کند."""
        normalized = (content or "").strip().lower()
        single_word = re.sub(r"[^a-z]", "", normalized)

        if single_word in cls.CATEGORY_ALIASES:
            return cls.CATEGORY_ALIASES[single_word]
        if single_word in cls.CATEGORY_DETAILS:
            return single_word

        for label in list(cls.CATEGORY_DETAILS) + list(cls.CATEGORY_ALIASES):
            if re.search(rf"\b{re.escape(label)}\b", normalized):
                return cls.CATEGORY_ALIASES.get(label, label)
        return None

    @staticmethod
    def _fallback_by_filename(image_path: Path) -> dict:
        """اگر مدل در دسترس نبود، تنها بر اساس نام فایل یک حدس کم‌اطمینان می‌زند."""
        lower_name = image_path.name.lower()
        keyword_map = {
            "people": ["person", "people", "human", "face", "portrait", "انسان", "مرد", "زن", "بچه"],
            "animals": ["cat", "dog", "animal", "bird", "horse", "حیوان", "گربه", "سگ", "پرنده"],
            "landscape": ["mountain", "beach", "landscape", "sky", "nature", "منظره", "کوه", "دریا", "جنگل"],
            "plant": ["plant", "flower", "tree", "گیاه", "گل", "درخت"],
            "food": ["food", "meal", "pizza", "burger", "ghaza", "غذا", "خوراک"],
            "building": ["building", "house", "arch", "architecture", "ساختمان", "خانه", "مسجد"],
            "vehicle": ["car", "vehicle", "auto", "ماشین", "خودرو"],
            "objects": ["logo", "لوگو"],
        }
        for category, keywords in keyword_map.items():
            if any(keyword in lower_name for keyword in keywords):
                subcategory = "logo" if category == "objects" and any(k in lower_name for k in ["logo", "لوگو"]) else "other"
                return {
                    "category": category,
                    "subcategory": subcategory,
                    "confidence": 0.5,
                    "reason": "filename fallback",
                }
        return {
            "category": "images",
            "subcategory": "other",
            "confidence": 0.0,
            "reason": "filename fallback: unknown",
        }

    def analyze_image(self, image_path) -> dict:
        """تصویر را با Gemma Vision تحلیل و نتیجهٔ مناسب ArchiveWorker را برمی‌گرداند."""
        image_path = Path(image_path)
        try:
            payload = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": self.SYSTEM_PROMPT},
                    {
                        "role": "user",
                        "content": "Classify this image.",
                        "images": [self._image_to_base64(image_path)],
                    },
                ],
                "stream": False,
                "options": {"temperature": 0, "num_predict": 20},
            }
            with self._lock:
                response = requests.post(
                    f"{self.base_url}/api/chat",
                    json=payload,
                    timeout=self.timeout,
                )
            if not response.ok:
                raise RuntimeError(f"Ollama returned HTTP {response.status_code}: {response.text[:400]}")

            raw_content = response.json().get("message", {}).get("content", "")
            detected = self._extract_category(raw_content)
            if detected is None:
                return {
                    "category": "images",
                    "subcategory": "other",
                    "confidence": 0.3,
                    "reason": f"Gemma Vision: unrecognized response: {raw_content!r}",
                }

            category, subcategory = self.CATEGORY_DETAILS[detected]
            return {
                "category": category,
                "subcategory": subcategory,
                "confidence": 0.9 if detected != "other" else 0.3,
                "reason": f"Gemma Vision: {detected}",
            }
        except Exception as error:
            fallback = self._fallback_by_filename(image_path)
            fallback["reason"] = f"{fallback['reason']} | Gemma error: {type(error).__name__}: {error}"
            return fallback

    def classify_image(self, image_path: str) -> tuple:
        result = self.analyze_image(image_path)
        category = result.get("category", "images")
        return self.PERSIAN_MAPPING.get(category, "سایر"), result.get("subcategory", "")
