import re
from pathlib import Path
try:
    from mutagen import File as MutagenFile
except ImportError:
    MutagenFile = None

class AudioAnalyzer:
    # نقشه جامع خوانندگان (نام فارسی و انگلیسی)
    SINGER_DATA = {
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
        "shajarian": ("شجریان", "Shajarian"),
        "hamid hiraad": ("حمید هیراد", "Hamid Hiraad"),
        "mohsen ebrahimzadeh": ("محسن ابراهیم زاده", "Mohsen Ebrahimzadeh"),
        "aron afshar": ("آرون افشار", "Aron Afshar"),
        "reza sadeghi": ("رضا صادقی", "Reza Sadeghi"),
        "mohsen chavoshi": ("محسن چاوشی", "Mohsen Chavoshi"),
        "mohsen yeganeh": ("محسن یگانه", "Mohsen Yeganeh"),
    }

    @classmethod
    def get_all_names_for(cls, artist_name):
        """برگرداندن تمام نام‌های ممکن برای یک خواننده جهت ادغام پوشه‌ها"""
        if not artist_name: return []
        nl = artist_name.lower().strip()
        for key, (per, eng) in cls.SINGER_DATA.items():
            if key in nl:
                return [per, eng, per.replace(" ", "_"), eng.replace(" ", "_"), key]
        return [artist_name]

    @classmethod
    def _translate(cls, name, pref="persian"):
        if not name: return ""
        nl = name.lower().strip()
        for key, (per, eng) in cls.SINGER_DATA.items():
            if key in nl:
                return per if pref == "persian" else eng
        return name

    @staticmethod
    def _clean(val):
        if not val: return ""
        # حذف اعداد ابتدایی آهنگ‌ها
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
                    # استخراج سال
                    date = audio.tags.get("date", [""])[0]
                    if date: meta["year"] = str(date)[:4]
            except: pass
        
        # اگر تگ نداشت، سعی کن از نام فایل خواننده را حدس بزنی
        if not meta["artist"]:
            parts = re.split(r"\s[-–—_]\s", path.stem)
            if len(parts) >= 2:
                meta["artist"] = parts[0].strip()
                meta["title"] = parts[1].strip()

        return meta

    @classmethod
    def folder_parts(cls, meta, pref="persian"):
        artist = cls._clean(cls._translate(meta["artist"], pref)) or "سایر_آهنگ‌ها"
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
        artist = cls._clean(cls._translate(meta["artist"], pref))
        if title and artist: return f"{title} - {artist}{ext}"
        return f"{cls._clean(path.stem)}{ext}"
