import re
import os
from pathlib import Path
try:
    from mutagen import File as MutagenFile
except ImportError:
    MutagenFile = None

class AudioAnalyzer:
    @staticmethod
    def _clean_text(val):
        if not val: return ""
        return re.sub(r'[<>:"/\\|?*]+', "_", str(val).strip())[:80]

    @staticmethod
    def _remove_leading_numbers(text):
        return re.sub(r"^[0-9٠-٩\s._-]+", "", text).strip()

    @classmethod
    def analyze(cls, path):
        path = Path(path)
        metadata = {"kind": "music", "artist": "", "album": "", "title": path.stem}
        if MutagenFile:
            try:
                audio = MutagenFile(path, easy=True)
                if audio and audio.tags:
                    metadata["artist"] = audio.tags.get("artist", [""])[0]
                    metadata["album"] = audio.tags.get("album", [""])[0]
                    metadata["title"] = audio.tags.get("title", [""])[0] or path.stem
            except: pass
        return metadata

    @classmethod
    def folder_parts(cls, hint):
        artist = cls._clean_text(hint.get("artist")) or "خواننده_نامشخص"
        album = cls._clean_text(hint.get("album")) or "آلبوم_نامشخص"
        return ["موسیقی_و_صوت", artist, album]

    @classmethod
    def destination_filename(cls, path, hint):
        clean_title = cls._remove_leading_numbers(hint.get("title") or path.stem)
        artist = cls._clean_text(hint.get("artist"))
        if artist and clean_title:
            return f"{clean_title} - {artist}{path.suffix.lower()}"
        return f"{cls._remove_leading_numbers(path.stem)}{path.suffix.lower()}"
