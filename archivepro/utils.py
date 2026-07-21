"""
utils.py
توابع کمکی مشترک: هش فایل، پاک‌سازی نام‌ها، نگاشت خواننده‌ها، پسوندها، کلیدواژه‌ها
"""

import re
import hashlib
from pathlib import Path

try:
    import jdatetime
except ImportError:
    jdatetime = None


# ---------------------------------------------------------------------------
# Hashing / duplicate detection
# ---------------------------------------------------------------------------
def calculate_hash(path, block_size=65536):
    hasher = hashlib.sha256()
    try:
        with open(path, "rb") as f:
            while True:
                chunk = f.read(block_size)
                if not chunk:
                    break
                hasher.update(chunk)
        return hasher.hexdigest()
    except Exception:
        return ""


# ---------------------------------------------------------------------------
# Filename sanitizing (Windows-safe)
# ---------------------------------------------------------------------------
INVALID_WIN_CHARS = r'<>:"/\|?*'


def sanitize_filename(name: str, max_len: int = 80) -> str:
    if not name:
        return "Unknown"
    name = name.strip()
    for ch in INVALID_WIN_CHARS:
        name = name.replace(ch, "")
    name = re.sub(r"\s+", " ", name).strip(" .")
    if len(name) > max_len:
        name = name[:max_len].strip()
    return name or "Unknown"


def normalize_arabic_chars(text: str) -> str:
    """Normalize Arabic-vs-Persian look-alike letters (ي->ی , ك->ک)."""
    if not text:
        return text
    return text.replace("ي", "ی").replace("ك", "ک")


# ---------------------------------------------------------------------------
# Persian (Shamsi) date conversion
# ---------------------------------------------------------------------------
def to_shamsi(dt) -> str:
    """dt: datetime.datetime -> 'YYYY-MM' shamsi string"""
    if jdatetime is None or dt is None:
        return "Unknown_Date"
    try:
        j = jdatetime.date.fromgregorian(date=dt.date())
        return f"{j.year}-{j.month:02d}"
    except Exception:
        return "Unknown_Date"


# ---------------------------------------------------------------------------
# Track-number / junk cleaning for audio titles & filenames
# ---------------------------------------------------------------------------
TRACK_NUM_PATTERNS = [
    r"^\s*\(?\d{1,3}\)?[\s._\-]+",          # 01 - , 001_ , 1)
    r"^\s*track\s*\d{1,3}[\s._\-]*",         # Track 01
    r"^\s*[A-Za-z]\d{1,3}[\s._\-]+",         # A01 -
    r"^\s*[۰-۹]{1,3}[\s._\-]+",              # Persian digits
]

AD_PATTERNS = [
    r"\(?www\.[^\s)]+\)?",
    r"\(?[a-zA-Z0-9\-]+\.(com|ir|net|org|info)\)?",
    r"\[[^\]]*(download|dl|music)[^\]]*\]",
]


def clean_audio_text(text: str) -> str:
    if not text:
        return ""
    t = text
    for pat in TRACK_NUM_PATTERNS:
        t = re.sub(pat, "", t, flags=re.IGNORECASE)
    for pat in AD_PATTERNS:
        t = re.sub(pat, "", t, flags=re.IGNORECASE)
    t = normalize_arabic_chars(t)
    t = re.sub(r"[_]+", " ", t)
    t = re.sub(r"\s+", " ", t).strip(" -_.")
    return sanitize_filename(t)


# Standard mapping of well-known Iranian singers (Latin tag name -> Persian name)
# Extend as needed.
SINGER_MAP_FA = {
    "ebi": "ابی", "dariush": "داریوش", "googoosh": "گوگوش", "moein": "معین",
    "mohsen chavoshi": "محسن چاوشی", "mohsen yeganeh": "محسن یگانه",
    "hamid hiraad": "حمید هیراد", "sirvan khosravi": "سیروان خسروی",
    "ehsan khajeamiri": "احسان خواجه امیری", "ehsan khaje amiri": "احسان خواجه امیری",
    "shadmehr aghili": "شادمهر عقیلی", "reza sadeghi": "رضا صادقی",
    "benyamin bahadori": "بنیامین بهادری", "benyamin": "بنیامین بهادری",
    "mohsen ebrahimzadeh": "محسن ابراهیم‌زاده", "amir tataloo": "امیر تتلو",
    "hayedeh": "هایده", "vigen": "ویگن", "shajarian": "شجریان",
}


def normalize_singer_key(name: str) -> str:
    if not name:
        return ""
    key = name.lower().strip()
    key = normalize_arabic_chars(key)
    key = re.sub(r"[_]+", " ", key)
    key = re.sub(r"\s+", " ", key)
    return key


def resolve_singer_name(artist_raw: str, want_persian: bool) -> str:
    """Return a single, consistent folder name for the artist."""
    key = normalize_singer_key(artist_raw)
    if want_persian and key in SINGER_MAP_FA:
        return SINGER_MAP_FA[key]
    return sanitize_filename(clean_audio_text(artist_raw) or "Unknown_Artist")


# ---------------------------------------------------------------------------
# Extension maps
# ---------------------------------------------------------------------------
IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".webp", ".ico", ".raw", ".heic"}

VECTOR_EXTS = {
    ".cdr": "CorelDRAW", ".ai": "Illustrator", ".psd": "Photoshop", ".eps": "EPS",
    ".svg": "SVG", ".fig": "Figma", ".sketch": "Sketch", ".afdesign": "Affinity",
}

ARCHITECTURE_EXTS = {
    ".dwg": "AutoCAD", ".dxf": "AutoCAD", ".skp": "SketchUp", ".rvt": "Revit",
    ".ifc": "Interchange", ".step": "Interchange", ".stp": "Interchange",
}

THREE_D_EXTS = {
    ".blend": "Blender", ".max": "3ds_Max", ".3ds": "3ds_Max", ".c4d": "Cinema4D",
    ".ma": "Maya", ".mb": "Maya", ".fbx": "Exchange", ".obj": "Exchange",
    ".dae": "Exchange", ".gltf": "Exchange", ".glb": "Exchange",
    ".stl": "3D_Print", ".3mf": "3D_Print", ".vrm": "VR_AR", ".x3d": "VR_AR",
}

AUDIO_EXTS = {".mp3", ".wav", ".flac", ".aac", ".ogg", ".m4a", ".wma", ".opus", ".aiff", ".mid", ".midi"}

VIDEO_EXTS = {".mp4", ".avi", ".mkv", ".mov", ".wmv", ".flv", ".webm", ".mpeg", ".mpg", ".3gp", ".m4v", ".ts"}

DOCUMENT_EXTS = {
    ".pdf": "PDF", ".txt": "Text", ".rtf": "Text", ".md": "Text", ".log": "Text",
    ".csv": "Data", ".json": "Data", ".xml": "Data", ".yml": "Data",
    ".html": "Web", ".htm": "Web", ".css": "Web", ".js": "Web",
    ".py": "Code", ".cpp": "Code", ".c": "Code", ".java": "Code", ".php": "Code",
    ".sql": "Code", ".ipynb": "Code",
}

OFFICE_EXTS = {
    ".doc": "Word", ".docx": "Word", ".xls": "Excel", ".xlsx": "Excel",
    ".ppt": "PowerPoint", ".pptx": "PowerPoint",
    ".odt": "OpenDocument", ".ods": "OpenDocument", ".odp": "OpenDocument",
}

ARCHIVE_EXTS = {".zip": "Zip", ".rar": "Rar", ".7z": "7zip", ".tar": "Tar",
                ".gz": "Tar", ".bz2": "Tar", ".xz": "Tar", ".iso": "Iso"}

DATABASE_EXTS = {".sql": "SQL", ".db": "SQLite", ".sqlite": "SQLite",
                  ".mdb": "Access", ".accdb": "Access"}

GAME_EXTS = {".unity": "Unity", ".uproject": "Unreal", ".godot": "Godot",
             ".sav": "Save", ".rom": "ROM"}

WINDOWS_SOFTWARE_EXTS = {".exe", ".msi", ".bat", ".cmd", ".ps1"}
ANDROID_SOFTWARE_EXTS = {".apk"}
IOS_SOFTWARE_EXTS = {".ipa"}
MAC_SOFTWARE_EXTS = {".dmg", ".pkg", ".app"}
LINUX_SOFTWARE_EXTS = {".deb", ".rpm", ".run", ".appimage", ".sh", ".bin"}


# ---------------------------------------------------------------------------
# Image content taxonomy (keyword-based fallback, Persian standard categories)
# ---------------------------------------------------------------------------
IMAGE_TAXONOMY = {
    "انسان": ["person", "people", "man", "woman", "child", "portrait", "human"],
    "حیوان": ["cat", "dog", "horse", "lion", "tiger", "bird", "fish", "animal"],
    "منظره": ["sea", "ocean", "beach", "mountain", "river", "lake", "forest", "desert", "sunset", "landscape"],
    "گیاه": ["flower", "rose", "tulip", "tree", "plant", "leaf"],
    "غذا": ["food", "meal", "pizza", "pasta", "burger", "kebab", "cake", "dessert"],
    "ساختمان": ["building", "house", "church", "mosque", "temple", "architecture", "skyscraper"],
    "خودرو": ["car", "automobile", "motorcycle", "truck", "vehicle", "airplane", "boat"],
    "اشیاء": ["object", "logo", "plate", "cup", "bowl", "glass", "furniture", "tool", "electronics"],
}

# Vector / graphic content taxonomy (world-standard asset library categories, Persian labels)
GRAPHIC_TAXONOMY = {
    "عناصر_رابط_کاربری": ["button", "form", "input", "menu", "card", "component", "ui", "ux"],
    "آیکون‌ها": ["icon", "pictogram", "glyph"],
    "اشکال_و_علائم": ["arrow", "symbol", "frame", "marker", "speech bubble", "cloud"],
    "تزئینات_و_آرایه‌ها": ["ornament", "arabesque", "tezhib", "border", "corner", "decorative frame"],
    "الگو_و_بافت": ["pattern", "seamless", "texture", "gradient"],
    "تصویرسازی": ["character", "illustration", "abstract", "nature scene"],
    "برندینگ": ["logo", "brand", "monogram"],
    "اینفوگرافیک": ["chart", "diagram", "infographic", "data icon"],
}

DOCUMENT_KEYWORDS = {
    "فاکتور": ["invoice", "فاکتور", "رسید", "receipt"],
    "قرارداد": ["contract", "قرارداد", "agreement"],
    "نامه": ["letter", "نامه"],
    "مدارک": ["certificate", "مدرک", "id card", "passport"],
    "گزارش": ["report", "گزارش"],
}

SCREENSHOT_HINTS = ["screenshot", "screen shot", "capture", "اسکرین", "screen_shot"]


# ---------------------------------------------------------------------------
# Software brand -> category mapping (world-standard, English category names)
# ---------------------------------------------------------------------------
SOFTWARE_BRAND_MAP = {
    # 2D design
    "photoshop": "2D_Design/Photo_Editing", "adobe photoshop": "2D_Design/Photo_Editing",
    "illustrator": "2D_Design/Vector", "coreldraw": "2D_Design/Vector",
    "figma": "2D_Design/UI_UX", "sketch": "2D_Design/UI_UX", "adobe xd": "2D_Design/UI_UX",
    # 3D design
    "blender": "3D_Design", "3ds max": "3D_Design", "autodesk 3ds max": "3D_Design",
    "maya": "3D_Design", "cinema 4d": "3D_Design", "vray": "3D_Design/Rendering",
    "corona renderer": "3D_Design/Rendering",
    # Architecture / CAD
    "autocad": "Architecture_CAD", "revit": "Architecture_CAD", "archicad": "Architecture_CAD",
    "rhino": "Architecture_CAD", "sketchup": "Architecture_CAD", "lumion": "Architecture_CAD",
    "enscape": "Architecture_CAD",
    # Microsoft / Office
    "microsoft office": "Microsoft_Office", "office": "Microsoft_Office",
    "visio": "Microsoft_Office", "project": "Microsoft_Office", "teams": "Microsoft_Office",
    "power bi": "Microsoft_Office",
    # Development
    "visual studio": "Development", "pycharm": "Development", "vscode": "Development",
    "android studio": "Development",
    # Media
    "premiere": "Media/Video", "after effects": "Media/Video", "davinci resolve": "Media/Video",
    "audacity": "Media/Audio", "fl studio": "Media/Audio",
    # Utilities
    "winrar": "Utilities/Compression", "7zip": "Utilities/Compression",
    "acronis": "Utilities/Backup", "adobe acrobat": "Utilities/PDF_Tools",
    # Security
    "kaspersky": "Security", "avast": "Security", "nod32": "Security",
    # Games
    "steam": "Games", "epic games": "Games",
}
