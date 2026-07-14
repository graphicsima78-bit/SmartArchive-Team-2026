import re
from datetime import datetime
from pathlib import Path

try:
    from mutagen import File as MutagenFile
except ImportError:
    MutagenFile = None

class AudioAnalyzer:
    AMBIENT_KEYWORDS = {
        "باران": ["rain", "باران"],
        "دریا": ["sea", "ocean", "wave", "دریا", "موج"],
        "جنگل": ["forest", "jungle", "جنگل"],
        "شهر": ["city", "street", "traffic", "شهر", "خیابان"],
    }
    
    @staticmethod
    def _safe_name(value, fallback="نامشخص"):
        if not value: return fallback
        return re.sub(r'[<>:"/\\|?*]+', "_", str(value).strip())[:80]

    @classmethod
    def analyze(cls, path):
        path = Path(path)
        metadata = {"kind": "music", "artist": "", "album": "", "title": path.stem, "source": "none"}
        
        if MutagenFile:
            try:
                audio = MutagenFile(path, easy=True)
                if audio and audio.tags:
                    metadata["artist"] = audio.tags.get("artist", [""])[0]
                    metadata["album"] = audio.tags.get("album", [""])[0]
                    metadata["title"] = audio.tags.get("title", [""])[0] or path.stem
                    metadata["source"] = "metadata"
            except: pass

        # FIX: If it has metadata (Artist or Album), it's definitely MUSIC. Skip ambient check.
        if metadata["artist"] or metadata["album"]:
            return metadata

        # If no metadata, check for ambient keywords in filename only
        name = path.stem.lower()
        for subtype, keywords in cls.AMBIENT_KEYWORDS.items():
            if any(k in name for k in keywords):
                metadata["kind"] = "ambient"
                metadata["subtype"] = subtype
                return metadata
        
        return metadata

    @classmethod
    def folder_parts(cls, hint):
        if hint.get("kind") == "ambient":
            return ["صدای_محیط", hint.get("subtype", "سایر")]
        
        artist = cls._safe_name(hint.get("artist"), "خواننده_نامشخص")
        album = cls._safe_name(hint.get("album"), "آلبوم_نامشخص")
        return ["موسیقی_و_صوت", artist, album]

    @classmethod
    def destination_filename(cls, path, hint):
        if hint.get("kind") == "ambient": return path.name
        
        # Clean leading numbers from filename
        clean_name = re.sub(r"^[0-9٠-٩\s._-]+", "", path.stem).strip()
        artist = cls._safe_name(hint.get("artist"), "")
        
        if artist and clean_name:
            return f"{clean_name} - {artist}{path.suffix.lower()}"
        return path.name
