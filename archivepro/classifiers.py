"""
classifiers.py
موتورهای دسته‌بندی برای هر تب: عکس، گرافیک/وکتور، صوت، نرم‌افزار
"""

import os
import re
from pathlib import Path
from datetime import datetime

from utils import (
    IMAGE_TAXONOMY, GRAPHIC_TAXONOMY, DOCUMENT_KEYWORDS, SCREENSHOT_HINTS,
    SOFTWARE_BRAND_MAP, VECTOR_EXTS, to_shamsi, clean_audio_text,
    resolve_singer_name, sanitize_filename,
    WINDOWS_SOFTWARE_EXTS, ANDROID_SOFTWARE_EXTS, IOS_SOFTWARE_EXTS,
    MAC_SOFTWARE_EXTS, LINUX_SOFTWARE_EXTS,
)

try:
    import exifread
except ImportError:
    exifread = None

try:
    import pytesseract
    from PIL import Image
except ImportError:
    pytesseract = None
    Image = None

try:
    import mutagen
except ImportError:
    mutagen = None


# ---------------------------------------------------------------------------
# Images classifier
# ---------------------------------------------------------------------------
class ImageClassifier:
    """mode: 'family' | 'work' | 'combined'"""

    def __init__(self, mode="combined", use_ocr=True, detect_screenshot=True):
        self.mode = mode
        self.use_ocr = use_ocr
        self.detect_screenshot = detect_screenshot

    def _read_exif_datetime(self, path):
        if exifread is None:
            return None
        try:
            with open(path, "rb") as f:
                tags = exifread.process_file(f, details=False, stop_tag="EXIF DateTimeOriginal")
            dt_tag = tags.get("EXIF DateTimeOriginal") or tags.get("Image DateTime")
            if dt_tag:
                return datetime.strptime(str(dt_tag), "%Y:%m:%d %H:%M:%S")
        except Exception:
            pass
        return None

    def _read_exif_location_name(self, path):
        # Offline: we only report GPS presence, no reverse geocoding (privacy / no internet).
        if exifread is None:
            return None
        try:
            with open(path, "rb") as f:
                tags = exifread.process_file(f, details=False)
            if "GPS GPSLatitude" in tags:
                return "GPS_Location"
        except Exception:
            pass
        return None

    def _is_screenshot(self, path: Path):
        name = path.stem.lower()
        return any(h in name for h in SCREENSHOT_HINTS)

    def _ocr_text(self, path):
        if not self.use_ocr or pytesseract is None or Image is None:
            return ""
        try:
            img = Image.open(path)
            return pytesseract.image_to_string(img)[:2000]
        except Exception:
            return ""

    def _content_category_from_text(self, text, filename_hint=""):
        haystack = (text + " " + filename_hint).lower()
        for doc_cat, kws in DOCUMENT_KEYWORDS.items():
            if any(k.lower() in haystack for k in kws):
                return ("اسناد", doc_cat)
        for cat, kws in IMAGE_TAXONOMY.items():
            if any(k.lower() in haystack for k in kws):
                return (cat, "")
        return ("سایر", "")

    def classify_family(self, path: Path):
        dt = self._read_exif_datetime(path)
        if dt is None:
            dt = datetime.fromtimestamp(path.stat().st_mtime)
        shamsi = to_shamsi(dt)
        location = self._read_exif_location_name(path) or "Unknown_Location"
        return ("خانوادگی", f"{shamsi}/{location}")

    def classify_work(self, path: Path):
        if self.detect_screenshot and self._is_screenshot(path):
            return ("کاری", "اسکرین‌شات")
        text = self._ocr_text(path)
        cat, sub = self._content_category_from_text(text, path.stem)
        return ("کاری", f"{cat}/{sub}" if sub else cat)

    def classify(self, path: Path):
        """Returns (main_category, sub_path_string)"""
        if self.mode == "family":
            return self.classify_family(path)
        if self.mode == "work":
            return self.classify_work(path)
        # combined: prefer family if EXIF date/gps exists, else content
        has_exif = self._read_exif_datetime(path) is not None or self._read_exif_location_name(path) is not None
        if has_exif:
            return self.classify_family(path)
        return self.classify_work(path)


# ---------------------------------------------------------------------------
# Graphics / Vector classifier
# ---------------------------------------------------------------------------
class GraphicsClassifier:
    def __init__(self, auto_generate_preview=False, use_ocr=True):
        self.auto_generate_preview = auto_generate_preview
        self.ocr = ImageClassifier(mode="work", use_ocr=use_ocr, detect_screenshot=False)

    def find_sidecar_preview(self, path: Path):
        base = path.with_suffix("")
        for ext in (".png", ".jpg", ".jpeg", ".webp"):
            candidate = Path(str(base) + ext)
            if candidate.exists():
                return candidate
        return None

    def generate_preview(self, path: Path):
        """Best-effort local preview render. Only SVG is reliably renderable
        without external tools/network. Other vector formats (AI/EPS/CDR) require
        a dedicated renderer (e.g. Illustrator/Inkscape) which is not bundled;
        in that case no preview is produced and the file falls back to the
        'Unknown_Graphics' bucket."""
        if not self.auto_generate_preview:
            return None
        ext = path.suffix.lower()
        out_path = path.with_suffix(".png")
        if out_path.exists():
            return out_path
        if ext == ".svg":
            try:
                from PySide6.QtSvg import QSvgRenderer
                from PySide6.QtGui import QImage, QPainter
                from PySide6.QtCore import QSize
                renderer = QSvgRenderer(str(path))
                size = QSize(512, 512)
                image = QImage(size, QImage.Format_ARGB32)
                image.fill(0)
                painter = QPainter(image)
                renderer.render(painter)
                painter.end()
                image.save(str(out_path))
                return out_path
            except Exception:
                return None
        # AI / EPS / CDR / others: no offline renderer available.
        return None

    def classify(self, path: Path):
        ext = path.suffix.lower()
        software = VECTOR_EXTS.get(ext, "Other")

        preview = self.find_sidecar_preview(path)
        if preview is None:
            preview = self.generate_preview(path)

        if preview is not None:
            text = self.ocr._ocr_text(preview)
            haystack = (text + " " + path.stem).lower()
            for cat, kws in GRAPHIC_TAXONOMY.items():
                if any(k.lower() in haystack for k in kws):
                    return (software, cat, preview)
            return (software, "سایر", preview)

        return (software, "Unknown_Graphics", None)


# ---------------------------------------------------------------------------
# Audio classifier
# ---------------------------------------------------------------------------
class AudioClassifier:
    def __init__(self, persian_names=False, use_album_folder=True):
        self.persian_names = persian_names
        self.use_album_folder = use_album_folder

    def read_tags(self, path: Path):
        artist = title = album = track = ""
        if mutagen is not None:
            try:
                f = mutagen.File(str(path), easy=True)
                if f is not None:
                    artist = (f.get("artist", [""])[0]) if f.get("artist") else ""
                    title = (f.get("title", [""])[0]) if f.get("title") else ""
                    album = (f.get("album", [""])[0]) if f.get("album") else ""
                    track = (f.get("tracknumber", [""])[0]) if f.get("tracknumber") else ""
            except Exception:
                pass
        return artist, title, album, track

    def classify(self, path: Path):
        artist, title, album, track = self.read_tags(path)

        if not artist:
            # try "Artist - Title" pattern from filename
            m = re.match(r"^(.*?)[-_]{1}(.*)$", path.stem)
            if m:
                artist, title = m.group(1), m.group(2)
            else:
                artist, title = "Unknown_Artist", path.stem

        artist_clean = resolve_singer_name(artist, self.persian_names)
        title_clean = clean_audio_text(title) or clean_audio_text(path.stem)
        album_clean = sanitize_filename(clean_audio_text(album)) if album else ""

        track_num = ""
        m = re.search(r"\d{1,3}", track) if track else None
        if m:
            track_num = m.group(0).zfill(2)

        if track_num:
            filename = f"{track_num} - {artist_clean} - {title_clean}"
        else:
            filename = f"{artist_clean} - {title_clean}"

        sub_path = artist_clean
        if self.use_album_folder and album_clean:
            sub_path = f"{artist_clean}/{album_clean}"

        return sub_path, sanitize_filename(filename)


# ---------------------------------------------------------------------------
# Software classifier
# ---------------------------------------------------------------------------
class SoftwareClassifier:
    def __init__(self, online_detection=False):
        self.online_detection = online_detection  # placeholder hook, no network call performed

    def platform_for(self, ext):
        if ext in WINDOWS_SOFTWARE_EXTS:
            return "Windows"
        if ext in ANDROID_SOFTWARE_EXTS:
            return "Android"
        if ext in IOS_SOFTWARE_EXTS:
            return "iOS"
        if ext in MAC_SOFTWARE_EXTS:
            return "macOS"
        if ext in LINUX_SOFTWARE_EXTS:
            return "Linux"
        return "Other"

    def guess_app_name(self, path: Path):
        name = path.stem
        name = re.sub(r"(setup|installer|install|x64|x86|v?\d+(\.\d+)*)", " ", name, flags=re.IGNORECASE)
        name = re.sub(r"[_\-.]+", " ", name)
        name = re.sub(r"\s+", " ", name).strip()
        return name or path.stem

    def classify(self, path: Path):
        ext = path.suffix.lower()
        platform = self.platform_for(ext)
        app_name = self.guess_app_name(path)
        haystack = app_name.lower()

        category = None
        for brand, cat in SOFTWARE_BRAND_MAP.items():
            if brand in haystack:
                category = cat
                break
        if category is None:
            category = "Utilities" if platform == "Android" else "Uncategorized"

        clean_app_name = sanitize_filename(app_name.title()).replace(" ", "_") or "Unknown_App"
        return platform, category, clean_app_name
