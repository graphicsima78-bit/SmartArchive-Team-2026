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
        "behnam bani": "بهنام بانی",
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
        "mohsen yeganeh": "محسن یگانه",
        "mohsen chavoshi": "محسن چاوشی",
        "sirvan khosravi": "سیروان خسروی",
        "reza sadeghi": "رضا صادقی",
        "babak jahanbakhsh": "بابک جهانبخش",
        "hamid hiraad": "حمید هیراد",
        "mohsen ebrahimzadeh": "محسن ابراهیم زاده",
    }

    @classmethod
    def get_preferred_name(cls, artist, pref="persian"):
        if not artist: return ""
        al = artist.lower().strip()
        for k, p in cls.SINGER_MAP.items():
            if k in al:
                return p if pref == "persian" else k.title()
        return artist

    @classmethod
    def get_all_variants(cls, artist):
        if not artist: return []
        al = artist.lower().strip()
        for k, p in cls.SINGER_MAP.items():
            if k in al:
                return [p, k, k.title(), p.replace(" ", "_"), k.replace(" ", "_")]
        return [artist]

    @staticmethod
    def _clean_text(val):
        if not val: return ""
        # Remove leading numbers (01, 002, 1., 2-)
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
                    d = audio.tags.get("date", [""])[0]
                    if d: meta["year"] = str(d)[:4]
            except: pass
        return meta

    @classmethod
    def destination_filename(cls, path, meta, pref="persian"):
        ext = path.suffix.lower()
        title = cls._clean_text(meta["title"])
        artist = cls._clean_text(cls.get_preferred_name(meta["artist"], pref))
        if title and artist:
            return f"{title} - {artist}{ext}"
        return f"{cls._clean_text(path.stem)}{ext}"
