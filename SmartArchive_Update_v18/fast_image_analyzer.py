"""Fast, offline-first image checks for obvious content before expensive Gemma Vision."""

import re
from pathlib import Path

try:
    import cv2
except ImportError:
    cv2 = None

try:
    import pytesseract
except ImportError:
    pytesseract = None


class FastImageAnalyzer:
    """Detect obvious faces and document-like images quickly without a large AI model."""

    DOCUMENT_KEYWORDS = {
        "payment": ["payment", "transfer", "deposit", "پرداخت", "واریز", "انتقال", "کارت به کارت", "رسید"],
        "invoice": ["invoice", "receipt", "فاکتور", "صورتحساب", "مبلغ", "قیمت"],
        "contract": ["contract", "agreement", "قرارداد", "توافق", "تعهد"],
        "letter": ["letter", "subject", "نامه", "احتراماً", "با سلام"],
        "report": ["report", "summary", "گزارش", "نتیجه", "تحلیل"],
        "id": ["passport", "national id", "کارت ملی", "شناسنامه", "پاسپورت"],
    }

    def __init__(self, use_ocr=True):
        self.use_ocr = bool(use_ocr)
        self.face_detector = None
        if cv2 is not None:
            try:
                cascade = Path(cv2.data.haarcascades) / "haarcascade_frontalface_default.xml"
                detector = cv2.CascadeClassifier(str(cascade))
                if not detector.empty():
                    self.face_detector = detector
            except Exception:
                pass

    @staticmethod
    def _unknown(reason="Fast analysis: no confident result"):
        return {
            "category": "unclassified",
            "subcategory": "other",
            "confidence": 0.0,
            "reason": reason,
        }

    def _detect_face(self, image_path):
        if cv2 is None or self.face_detector is None:
            return None
        try:
            image = cv2.imread(str(image_path))
            if image is None:
                return None
            # Downscale very large images for a quick check.
            height, width = image.shape[:2]
            if max(height, width) > 1200:
                scale = 1200 / max(height, width)
                image = cv2.resize(image, (int(width * scale), int(height * scale)))
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            faces = self.face_detector.detectMultiScale(gray, scaleFactor=1.15, minNeighbors=5, minSize=(40, 40))
            if len(faces) > 0:
                return {
                    "category": "people",
                    "subcategory": "other",
                    "confidence": 0.8,
                    "reason": "Fast content: face detected",
                }
        except Exception:
            pass
        return None

    @staticmethod
    def _payment_recipient(text):
        """Extract a recipient only when OCR explicitly labels it; otherwise use نامشخص."""
        patterns = [
            r"(?:به نام|گیرنده|واریز به|انتقال به)\s*[:\-]?\s*([آ-یA-Za-z][آ-یA-Za-z\s]{2,45})",
        ]
        for pattern in patterns:
            match = re.search(pattern, text, flags=re.IGNORECASE)
            if match:
                candidate = " ".join(match.group(1).split()).strip(" .:-")
                if candidate:
                    return candidate[:80]
        return "نامشخص"

    def _detect_document_text(self, image_path):
        if not self.use_ocr or pytesseract is None:
            return None
        try:
            text = pytesseract.image_to_string(str(image_path), timeout=8).casefold()
            if not text.strip():
                return None
            for subtype, keywords in self.DOCUMENT_KEYWORDS.items():
                if any(keyword.casefold() in text for keyword in keywords):
                    result = {
                        "category": "documents",
                        "subcategory": subtype,
                        "confidence": 0.75,
                        "reason": f"Fast content: OCR document ({subtype})",
                    }
                    if subtype == "payment":
                        result["recipient"] = self._payment_recipient(text)
                    return result
            # A text-heavy image is more likely a poster/design than a photograph.
            if len(text.replace(" ", "")) > 80:
                return {
                    "category": "art_texture",
                    "subcategory": "art",
                    "confidence": 0.55,
                    "reason": "Fast content: text-heavy image",
                }
        except Exception:
            pass
        return None

    def analyze(self, image_path):
        image_path = Path(image_path)
        result = self._detect_face(image_path)
        if result:
            return result
        result = self._detect_document_text(image_path)
        if result:
            return result
        return self._unknown()
