import re
from pathlib import Path
try:
    from mutagen import File as MutagenFile
except ImportError:
    MutagenFile = None

class AudioAnalyzer:
    # نقشه جامع خوانندگان (قابل گسترش)
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
        "sirvan khosravi": ("سیروان خسروی", "Sirvan Khosravi"),
        "reza sadeghi": ("رضا صادقی", "Reza Sadeghi"),
        "babak jahanbakhsh": ("بابک جهانبخش", "Babak Jahanbakhsh"),
    }

    @classmethod
    def _translate_artist(cls, name, pref="persian"):
        if not name: return ""
        name_lower = name.lower().strip()
        for key, (per, eng) in cls.SINGER_MAP.items():
            if key in name_lower:
                return per if pref == "persian" else eng
        return name

    @staticmethod
    def _clean(val):
        if not val: return ""
        # حذف اعداد ابتدایی
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
                    meta["year"] = audio.tags.get("date", [""])[0][:4]
            except: pass
        return meta

    @classmethod
    def folder_parts(cls, meta, pref="persian"):
        artist = cls._clean(cls._translate_artist(meta["artist"], pref)) or "سایر_آهنگ‌ها"
        album = cls._clean(meta["album"])
        year = cls._clean(meta["year"])
        
        if artist == "سایر_آهنگ‌ها":
            return ["موسیقی_و_صوت", "سایر_آهنگ‌ها"]
        
        if album:
            return ["موسیقی_و_صوت", artist, album]
        if year:
            return ["موسیقی_و_صوت", artist, year]
        
        return ["موسیقی_و_صوت", artist]

    @classmethod
    def destination_filename(cls, path, meta, pref="persian"):
        title = cls._clean(meta["title"])
        artist = cls._clean(cls._translate_artist(meta["artist"], pref))
        if title and artist:
            return f"{title} - {artist}{path.suffix.lower()}"
        return f"{cls._clean(path.stem)}{path.suffix.lower()}"
