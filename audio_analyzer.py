import re
from pathlib import Path
try:
    from mutagen import File as MutagenFile
except ImportError:
    MutagenFile = None

class AudioAnalyzer:
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
        "mohammad reza shajarian": ("محمدرضا شجریان", "محمدرضا شجریان"),
        "mohsen yeganeh": ("محسن یگانه", "Mohsen Yeganeh"),
        "mohsen chavoshi": ("محسن چاوشی", "Mohsen Chavoshi"),
        "sirvan khosravi": ("سیروان خسروی", "Sirvan Khosravi"),
        "reza sadeghi": ("رضا صادقی", "Reza Sadeghi"),
        "babak jahanbakhsh": ("بابک جهانبخش", "Babak Jahanbakhsh"),
        "farzad farzin": ("فرزاد فرزین", "Farzad Farzin"),
    }

    @classmethod
    def get_variants(cls, name):
        """برگرداندن تمام نام‌های ممکن برای یک خواننده (فارسی و انگلیسی)"""
        if not name: return []
        nl = name.lower().strip()
        for key, (per, eng) in cls.SINGER_MAP.items():
            if key in nl:
                return [per, eng, per.replace(" ", "_"), eng.replace(" ", "_")]
        return [name]

    @classmethod
    def _translate_artist(cls, name, pref="persian"):
        if not name: return ""
        nl = name.lower().strip()
        for key, (per, eng) in cls.SINGER_MAP.items():
            if key in nl:
                return per if pref == "persian" else eng
        return name

    @staticmethod
    def _clean(val):
        if not val: return ""
        val = re.sub(r"^[0-9٠-٩\s._-]+", "", str(val))
        return re.sub(r'[<>:"/\\|?*]+', "_", val.strip())[:80]

    @classmethod
    def analyze(cls, path):
        path = Path(path)
        meta = {"artist": "", "album": "", "title": path.stem, "year": ""}
        if MutagenFile:
            try:
                audio = MutagenFile(path, easy=True)
                if audio and audio.tags:
                    meta["artist"] = audio.tags.get("artist", [""])[0]
                    meta["album"] = audio.tags.get("album", [""])[0]
                    meta["title"] = audio.tags.get("title", [""])[0] or path.stem
                    # Safe Year Extraction
                    d = audio.tags.get("date", [""])[0]
                    if d: meta["year"] = str(d)[:4]
            except: pass
        return meta

    @classmethod
    def folder_parts(cls, meta, pref="persian"):
        artist = cls._clean(cls._translate_artist(meta["artist"], pref)) or "سایر_آهنگ‌ها"
        album = cls._clean(meta["album"])
        year = cls._clean(meta["year"])
        if artist == "سایر_آهنگ‌ها": return ["موسیقی_و_صوت", "سایر_آهنگ‌ها"]
        if album: return ["موسیقی_و_صوت", artist, album]
        if year: return ["موسیقی_و_صوت", artist, year]
        return ["موسیقی_و_صوت", artist]

    @classmethod
    def destination_filename(cls, path, meta, pref="persian"):
        ext = path.suffix.lower()
        title = cls._clean(meta["title"])
        artist = cls._clean(cls._translate_artist(meta["artist"], pref))
        if title and artist: return f"{title} - {artist}{ext}"
        return f"{cls._clean(path.stem)}{ext}"
