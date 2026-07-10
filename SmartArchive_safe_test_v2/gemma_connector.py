import base64
import re
import threading
from pathlib import Path

import requests


class GemmaConnector:
    """ارتباط امن و قابل‌بررسی با مدل محلی Gemma در Ollama."""

    SYSTEM_PROMPT = (
        "You are an image classifier. Respond with ONLY ONE WORD from: "
        "person, animal, landscape, food, building, vehicle, object, logo, other. "
        "No explanation."
    )

    CATEGORY_MAPPING = {
        "person": "people",
        "animal": "animals",
        "landscape": "landscape",
        "food": "food",
        "building": "building",
        "vehicle": "vehicle",
        "object": "objects",
        "logo": "objects",
        "other": "images",
    }

    PERSIAN_MAPPING = {
        "people": "انسان",
        "animals": "حیوان",
        "landscape": "منظره",
        "food": "غذا",
        "building": "ساختمان",
        "vehicle": "خودرو",
        "objects": "اشیاء",
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

    def _image_to_base64(self, image_path: Path) -> str:
        if not image_path.is_file():
            raise FileNotFoundError(f"Image file was not found: {image_path}")

        with image_path.open("rb") as file:
            return base64.b64encode(file.read()).decode("utf-8")

    @classmethod
    def _extract_category(cls, content: str):
        """خروجی مدل را حتی اگر نقطه یا توضیح کوتاه داشته باشد، به دسته تبدیل می‌کند."""
        normalized = (content or "").strip().lower()
        single_word = re.sub(r"[^a-z]", "", normalized)

        if single_word in cls.CATEGORY_MAPPING:
            return single_word

        for category in cls.CATEGORY_MAPPING:
            if re.search(rf"\b{re.escape(category)}\b", normalized):
                return category

        return None

    @staticmethod
    def _fallback_by_filename(image_path: Path) -> dict:
        """Fallback بر اساس نام فایل؛ علت fallback همیشه در reason ثبت می‌شود."""
        lower_name = image_path.name.lower()

        keyword_map = {
            "people": ["person", "people", "human", "face", "portrait", "انسان", "مرد", "زن", "بچه"],
            "animals": ["cat", "dog", "animal", "bird", "horse", "حیوان", "گربه", "سگ", "پرنده"],
            "landscape": ["mountain", "beach", "landscape", "sky", "nature", "منظره", "کوه", "دریا", "جنگل"],
            "food": ["food", "meal", "pizza", "burger", "ghaza", "غذا", "خوراک"],
            "building": ["building", "house", "arch", "architecture", "ساختمان", "خانه", "مسجد"],
            "vehicle": ["car", "vehicle", "auto", "ماشین", "خودرو"],
        }

        for category, keywords in keyword_map.items():
            if any(keyword in lower_name for keyword in keywords):
                return {
                    "category": category,
                    "subcategory": "portrait" if category == "people" else "other",
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
        """تصویر را با Gemma Vision تحلیل و نتیجه را برای archiver.py برمی‌گرداند."""
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
                raise RuntimeError(
                    f"Ollama returned HTTP {response.status_code}: {response.text[:400]}"
                )

            data = response.json()
            raw_content = data.get("message", {}).get("content", "")
            category = self._extract_category(raw_content)

            if category is None:
                return {
                    "category": "images",
                    "subcategory": "other",
                    "confidence": 0.3,
                    "reason": f"Gemma Vision: unrecognized response: {raw_content!r}",
                }

            return {
                "category": self.CATEGORY_MAPPING[category],
                "subcategory": "other",
                "confidence": 0.9 if category != "other" else 0.3,
                "reason": f"Gemma Vision: {category}",
            }

        except Exception as error:
            fallback = self._fallback_by_filename(image_path)
            fallback["reason"] = (
                f"{fallback['reason']} | Gemma error: "
                f"{type(error).__name__}: {error}"
            )
            return fallback

    def classify_image(self, image_path: str) -> tuple:
        """متد سازگار با کدهای قبلی؛ دسته را به فارسی برمی‌گرداند."""
        result = self.analyze_image(image_path)
        category = result.get("category", "images")
        return self.PERSIAN_MAPPING.get(category, "سایر"), result.get("subcategory", "")
