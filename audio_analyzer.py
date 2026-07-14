import re
from pathlib import Path
try:
    from mutagen import File as MutagenFile
except ImportError:
    MutagenFile = None

class AudioAnalyzer:
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
        "reza sadeghi": ("رضا صادقی", "Reza Sadeghi"),
        "mohsen chavoshi": ("محسن چاوشی", "Mohsen Chavoshi"),
        "mohsen yeganeh": ("محسن یگانه", "Mohsen Yeganeh"),
        "sirvan khosravi": ("سیروان خسروی", "Sirvan Khosravi"),
        "hamid hiraad": ("حمید هیراد", "Hamid Hiraad"),
    }

    @classmethod
    def get_preferred_name(cls, artist, pref="persian"):
        if not artist: return ""
        al = artist.lower().strip()
        for k, (p, e) in cls.SINGER_DATA.items():
            if k in al: return p if pref == "persian" else e
        return artist

    @classmethod
    def get_all_variants(cls, artist):
        if not artist: return []
        al = artist.lower().strip()
        for k, (p, e) in cls.SINGER_DATA.items():
            if k in al: return [p, e, k, p.replace(" ", "_"), e.replace(" ", "_")]
        return [artist]

    @staticmethod
    def _clean(text):
        if not text: return ""
        # حذف تهاجمی اعداد ابتدایی
        text = re.sub(r"^[0-9٠-٩\s._-]+", "", str(text))
        return re.sub(r'[<>:"/\\|?*]+', "_", text.strip())[:80]

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
        title = cls._clean(meta["title"])
        artist = cls._clean(cls.get_preferred_name(meta["artist"], pref))
        if title and artist: return f"{title} - {artist}{ext}"
        return f"{cls._clean(path.stem)}{ext}"
