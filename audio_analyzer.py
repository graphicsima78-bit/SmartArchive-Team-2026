import re
from pathlib import Path
try:
    from mutagen import File as MutagenFile
except ImportError:
    MutagenFile = None

class AudioAnalyzer:
    SINGER_MAP = {
        "farzad farzin": "فرزاد فرزین",
        "ehsan khajeh amiri": "احسان خواجه امیری",
        "ehsan khajeamiri": "احسان خواجه امیری",
        "behnam bani": "بهنام بانی",
        "shadmehr": "شادمهر عقیلی",
        "dariush": "داریوش",
        "ebi": "ابی",
        "moein": "معین",
        "hayedeh": "هایده",
        "mahasti": "مهستی",
        "googoosh": "گوگوش",
        "siavash ghomayshi": "سیاوش قمیشی",
        "shajarian": "شجریان",
        "mohsen yeganeh": "محسن یگانه",
        "mohsen chavoshi": "محسن چاوشی",
        "reza sadeghi": "رضا صادقی",
        "sirvan khosravi": "سیروان خسروی",
        "hamid hiraad": "حمید هیراد",
        "mohsen ebrahimzadeh": "محسن ابراهیم زاده",
    }

    @classmethod
    def get_persian_artist(cls, name):
        if not name: return ""
        nl = name.lower().strip()
        for eng, per in cls.SINGER_MAP.items():
            if eng in nl: return per
        return name

    @classmethod
    def get_all_variants(cls, name):
        if not name: return []
        per = cls.get_persian_artist(name)
        return [per, name, name.lower(), name.title(), name.replace(" ", "_"), name.replace(" ", "")]

    @staticmethod
    def _clean(text):
        if not text: return ""
        # حذف آدرس سایت ها و اعداد ابتدایی
        text = re.sub(r"(?i)\b.*\.(com|ir|net|org|me|co|info)\b", "", str(text))
        text = re.sub(r"^[0-9٠-٩\s._-]+", "", text)
        return re.sub(r'[<>:"/\\|?*]+', "_", text.strip())[:80]

    @classmethod
    def analyze(cls, path):
        path = Path(path)
        meta = {"artist": "", "album": "", "title": path.stem, "year": ""}
        if MutagenFile:
            try:
                audio = MutagenFile(path, easy=True)
                if audio and audio.tags:
                    meta["artist"] = cls.get_persian_artist(audio.tags.get("artist", [""])[0])
                    meta["album"] = audio.tags.get("album", [""])[0]
                    meta["title"] = audio.tags.get("title", [""])[0] or path.stem
                    d = audio.tags.get("date", [""])[0]
                    if d: meta["year"] = str(d)[:4]
            except: pass
        return meta

    @classmethod
    def destination_filename(cls, path, meta):
        ext = path.suffix.lower()
        title = cls._clean(meta["title"])
        artist = cls._clean(meta["artist"])
        if title and artist: return f"{title} - {artist}{ext}"
        return f"{cls._clean(path.stem)}{ext}"
