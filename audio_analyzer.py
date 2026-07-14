import re
from pathlib import Path
try:
    from mutagen import File as MutagenFile
except ImportError:
    MutagenFile = None

class AudioAnalyzer:
    # نقشه جامع خوانندگان برای فارسی‌سازی و ادغام پوشه‌ها
    SINGER_MAP = {
        "farzad farzin": ("فرزاد فرزین", "Farzad Farzin"),
        "ehsan khajeh amiri": ("احسان خواجه امیری", "Ehsan Khajeh Amiri"),
        "behnam bani": ("بهنام بانی", "Behnam Bani"),
        "shadmehr": ("شادمهر عقیلی", "Shadmehr Aghili"),
        "dariush": ("داریوش", "Dariush"),
        "ebi": ("ابی", "Ebi"),
        "moein": ("معین", "Moein"),
        "hayedeh": ("هایده", "Hayedeh"),
        "mahasti": ("مهستی", "Mahasti"),
        "googoosh": ("گوگوش", "Googoosh"),
        "siavash ghomayshi": ("سیاوش قمیشی", "Siavash Ghomayshi"),
        "homayoun shajarian": ("همایون شجریان", "Homayoun Shajarian"),
        "mohsen yeganeh": ("محسن یگانه", "Mohsen Yeganeh"),
        "mohsen chavoshi": ("محسن چاوشی", "Mohsen Chavoshi"),
        "reza sadeghi": ("رضا صادقی", "Reza Sadeghi"),
        "hamid hiraad": ("حمید هیراد", "Hamid Hiraad"),
    }

    AMBIENT_KEYWORDS = {"باران": ["rain", "باران"], "دریا": ["sea", "ocean"], "جنگل": ["forest", "jungle"]}

    @classmethod
    def get_preferred_name(cls, artist, pref="persian"):
        if not artist: return ""
        al = artist.lower().strip()
        for k, (p, e) in cls.SINGER_MAP.items():
            if k in al: return p if pref == "persian" else e
        return artist

    @classmethod
    def get_all_variants(cls, artist):
        if not artist: return []
        al = artist.lower().strip()
        for k, (p, e) in cls.SINGER_MAP.items():
            if k in al: return [p, e, k, p.replace(" ", "_"), e.replace(" ", "_")]
        return [artist]

    @staticmethod
    def _clean(text):
        if not text: return ""
        # حذف تهاجمی اعداد و علائم ابتدایی (01, 002, 1., 2-)
        text = re.sub(r"^[0-9٠-٩\s._-]+", "", str(text))
        return re.sub(r'[<>:"/\\|?*]+', "_", text.strip())[:80]

    @classmethod
    def analyze(cls, path):
        path = Path(path)
        meta = {"kind": "music", "artist": "", "album": "", "title": path.stem, "year": "", "source": "none"}
        if MutagenFile:
            try:
                audio = MutagenFile(path, easy=True)
                if audio and audio.tags:
                    meta["artist"] = audio.tags.get("artist", [""])[0]
                    meta["album"] = audio.tags.get("album", [""])[0]
                    meta["title"] = audio.tags.get("title", [""])[0] or path.stem
                    d = audio.tags.get("date", [""])[0]
                    if d: meta["year"] = str(d)[:4]
                    meta["source"] = "metadata"
            except: pass

        # حل مشکل صدای باران: اگر تگ داشت، حتماً موسیقی است
        if meta["artist"] or meta["album"]: return meta

        # چک کردن کلمات محیطی فقط در صورت نبود تگ
        name = path.stem.lower()
        for sub, keys in cls.AMBIENT_KEYWORDS.items():
            if any(k in name for k in keys):
                meta["kind"] = "ambient"; meta["subtype"] = sub
                return meta
        return meta

    @classmethod
    def destination_filename(cls, path, meta, pref="persian"):
        if meta.get("kind") == "ambient": return path.name
        title = cls._clean(meta["title"])
        artist = cls._clean(cls.get_preferred_name(meta["artist"], pref))
        if title and artist: return f"{title} - {artist}{path.suffix.lower()}"
        return f"{cls._clean(path.stem)}{path.suffix.lower()}"
