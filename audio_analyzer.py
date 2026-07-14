import re
from pathlib import Path
try:
    from mutagen import File as MutagenFile
except ImportError:
    MutagenFile = None

class AudioAnalyzer:
    # نقشه جامع برای تبدیل نام خوانندگان به فارسی
    SINGER_MAP = {
        "shadmehr": "شادمهر عقیلی",
        "dariush": "داریوش",
        "ebi": "ابی",
        "moein": "معین",
        "hayedeh": "هایده",
        "mahasti": "مهستی",
        "googoosh": "گوگوش",
        "siavash ghomayshi": "سیاوش قمیشی",
        "homayoun shajarian": "همایون شجریان",
        "mohammad reza shajarian": "محمدرضا شجریان",
        "shajarian": "شجریان",
        "sattar": "ستار",
        "vigen": "ویگن",
        "omid": "امید",
        "mansour": "منصور",
        "shahram shabpareh": "شهرام شب‌پره",
        "leila forouhar": "لیلا فروهر",
        "shoohreh": "شهره",
        "benam bani": "بهنام بانی",
        "mohsen yeganeh": "محسن یگانه",
        "mohsen chavoshi": "محسن چاوشی",
        "sirvan khosravi": "سیروان خسروی",
        "xaniar khosravi": "زانیار خسروی",
        "mortezza pashaei": "مرتضی پاشایی",
        "babak jahanbakhsh": "بابک جهانبخش",
        "farzad farzin": "فرزاد فرزین",
        "reza sadeghi": "رضا صادقی",
        "arash": "آرش",
        "andy": "اندی",
    }

    @staticmethod
    def _has_persian(text):
        return bool(re.search(r'[\u0600-\u06FF]', text))

    @classmethod
    def _get_persian_artist(cls, artist_name):
        if not artist_name: return ""
        if cls._has_persian(artist_name): return artist_name # خودش فارسی است
        
        # جستجو در نقشه تبدیل
        artist_lower = artist_name.lower().strip()
        for eng, per in cls.SINGER_MAP.items():
            if eng in artist_lower:
                return per
        return artist_name # اگر پیدا نشد همان فینگلیش بماند

    @staticmethod
    def _clean_text(val):
        if not val: return ""
        val = re.sub(r"^[0-9٠-٩\s._-]+", "", str(val))
        return re.sub(r'[<>:"/\\|?*]+', "_", val.strip())[:80]

    @classmethod
    def analyze(cls, path):
        path = Path(path)
        metadata = {"kind": "music", "artist": "", "album": "", "title": ""}
        if MutagenFile:
            try:
                audio = MutagenFile(path, easy=True)
                if audio and audio.tags:
                    metadata["artist"] = audio.tags.get("artist", [""])[0]
                    metadata["album"] = audio.tags.get("album", [""])[0]
                    metadata["title"] = audio.tags.get("title", [""])[0]
            except: pass
        
        # تبدیل نام خواننده به فارسی در صورت امکان
        metadata["artist"] = cls._get_persian_artist(metadata["artist"])
        return metadata

    @classmethod
    def folder_parts(cls, hint):
        artist = cls._clean_text(hint.get("artist"))
        album = cls._clean_text(hint.get("album"))
        if not artist: return ["موسیقی_و_صوت", "سایر_آهنگ‌ها"]
        if not album: return ["موسیقی_و_صوت", artist]
        return ["موسیقی_و_صوت", artist, album]

    @classmethod
    def destination_filename(cls, path, hint):
        ext = path.suffix.lower()
        title = cls._clean_text(hint.get("title"))
        artist = cls._clean_text(hint.get("artist"))
        if title and artist: return f"{title} - {artist}{ext}"
        return f"{re.sub(r'^[0-9٠-٩\s._-]+', '', path.stem)}{ext}"
