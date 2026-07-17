"""Small helpers for screenshot detection and privacy-preserving EXIF location/date routing."""

from datetime import datetime
from pathlib import Path
import re

try:
    from PIL import Image
except ImportError:
    Image = None


class PhotoAnalyzer:
    SCREENSHOT_WORDS = ["screenshot", "screen shot", "screen_shot", "اسکرین", "نماگرفت"]

    @staticmethod
    def _decode_exif_value(value):
        if isinstance(value, bytes):
            for encoding in ("utf-8", "utf-16le", "latin-1"):
                try:
                    return value.decode(encoding, errors="ignore").strip("\x00 ")
                except Exception:
                    pass
            return ""
        return str(value or "").strip()

    @staticmethod
    def _safe_location(value):
        value = re.sub(r"https?://\S+|www\.\S+", "", str(value or ""), flags=re.IGNORECASE)
        value = re.sub(r'[<>:"/\\|?*]+', "_", value)
        value = re.sub(r"\s+", " ", value).strip(" ._")
        # Do not treat generic camera comments or long descriptions as a location.
        if not value or len(value) > 80:
            return ""
        return value

    @classmethod
    def is_screenshot(cls, path):
        name = Path(path).stem.casefold()
        return any(word in name for word in cls.SCREENSHOT_WORDS)

    @classmethod
    def exif_info(cls, path):
        """Return date taken and location name only if an EXIF textual location already exists.

        No GPS coordinates are sent to an online service.
        """
        fallback_date = datetime.fromtimestamp(Path(path).stat().st_mtime)
        result = {"taken_at": fallback_date, "location": ""}
        if Image is None:
            return result
        try:
            with Image.open(path) as image:
                exif = image.getexif()
                if not exif:
                    return result

                date_text = exif.get(36867) or exif.get(306)  # DateTimeOriginal / DateTime
                if date_text:
                    try:
                        result["taken_at"] = datetime.strptime(str(date_text), "%Y:%m:%d %H:%M:%S")
                    except ValueError:
                        pass

                # Only GPSAreaInformation is used as a location label. Coordinates are never reverse-geocoded.
                candidates = []
                try:
                    gps = exif.get_ifd(34853)
                    candidates.append(gps.get(28))  # GPSAreaInformation
                except Exception:
                    pass

                for value in candidates:
                    location = cls._safe_location(cls._decode_exif_value(value))
                    if location:
                        result["location"] = location
                        break
        except Exception:
            pass
        return result
