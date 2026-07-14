"""Audio metadata extraction and practical folder classification for ArchivePro."""

import re
from datetime import datetime
from pathlib import Path

try:
    from mutagen import File as MutagenFile
except ImportError:  # The rest of ArchivePro can still work without mutagen.
    MutagenFile = None


class AudioAnalyzer:
    """Read audio metadata when available and classify common personal audio files."""

    RECORDING_KEYWORDS = {
        "ویس": ["voice", "voicenote", "voice_note", "whatsapp", "telegram", "ویس", "صدا"],
        "جلسه": ["meeting", "جلسه", "conference", "call"],
        "کلاس": ["class", "lecture", "lesson", "کلاس", "درس"],
        "مصاحبه": ["interview", "مصاحبه"],
    }
    AMBIENT_KEYWORDS = {
        "باران": ["rain", "باران"],
        "دریا": ["sea", "ocean", "wave", "دریا", "موج"],
        "جنگل": ["forest", "jungle", "جنگل"],
        "شهر": ["city", "street", "traffic", "شهر", "خیابان"],
        "کافه": ["cafe", "coffee", "کافه"],
        "باد": ["wind", "باد"],
    }
    EFFECT_KEYWORDS = {
        "رابط_کاربری": ["ui", "interface", "click", "notification", "رابط", "کلیک", "اعلان"],
        "هشدار": ["alert", "alarm", "warning", "beep", "هشدار", "آلارم"],
        "طبیعت": ["nature", "thunder", "rain", "bird", "طبیعت", "رعد", "باران"],
        "حیوانات": ["animal", "dog", "cat", "bird", "حیوان", "سگ", "گربه", "پرنده"],
        "انسان": ["human", "crowd", "clap", "laugh", "انسان", "جمعیت", "خنده"],
        "وسایل_نقلیه": ["car", "engine", "train", "plane", "vehicle", "ماشین", "موتور", "قطار"],
        "انفجار": ["explosion", "blast", "boom", "انفجار"],
    }
    WEBSITE_WORDS = {
        "download", "دانلود", "telegram", "تلگرام", "instagram", "اینستاگرام",
        "http", "https", "www", "tme", "free", "official",
    }

    @staticmethod
    def _first_tag(tags, *names):
        if not tags:
            return ""
        for name in names:
            value = tags.get(name)
            if isinstance(value, (list, tuple)):
                value = value[0] if value else ""
            if value:
                return str(value).strip()
        return ""

    @staticmethod
    def _safe_folder_name(value, fallback="بدون_متادیتا"):
        value = re.sub(r'[<>:"/\\|?*]+', "_", str(value or "").strip())
        value = re.sub(r"\s+", " ", value).strip(" .")
        return value[:100] if value else fallback

    @staticmethod
    def _keyword_match(text, keywords):
        return any(keyword in text for keyword in keywords)

    @classmethod
    def _find_subtype(cls, text, mapping):
        for subtype, keywords in mapping.items():
            if cls._keyword_match(text, keywords):
                return subtype
        return "سایر"

    @staticmethod
    def _year_from(value, fallback_timestamp):
        match = re.search(r"\b(19|20)\d{2}\b", str(value or ""))
        if match:
            return match.group(0)
        return datetime.fromtimestamp(fallback_timestamp).strftime("%Y")

    @staticmethod
    def _month_from(timestamp):
        return datetime.fromtimestamp(timestamp).strftime("%Y-%m")

    @classmethod
    def _clean_filename_for_inference(cls, filename_stem):
        """Remove URLs and download-site labels so they are never used as artist or folder names."""
        text = str(filename_stem)
        text = re.sub(r"https?://\S+|www\.\S+|t\.me/\S+", " ", text, flags=re.IGNORECASE)
        text = re.sub(r"\b[\w-]+\.(?:com|ir|net|org|io|me|co)\b", " ", text, flags=re.IGNORECASE)
        text = cls._remove_leading_zeros(text)
        for word in cls.WEBSITE_WORDS:
            text = re.sub(rf"\b{re.escape(word)}\b", " ", text, flags=re.IGNORECASE)
        text = re.sub(r"[\[\](){}]+", " ", text)
        text = re.sub(r"\s+", " ", text).strip(" -_.")
        return text

    @classmethod
    def _looks_like_website_name(cls, value):
        value = str(value or "").casefold()
        return (
            not value
            or "http" in value
            or "www" in value
            or any(domain in value for domain in [".com", ".ir", ".net", ".org", "t.me"])
        )

    @classmethod
    def _infer_from_filename(cls, filename_stem):
        """Use a clear 'artist - title' pattern only; never use URLs or site labels."""
        clean = cls._clean_filename_for_inference(filename_stem)
        if not clean or cls._looks_like_website_name(clean):
            return "", ""

        parts = [part.strip() for part in re.split(r"\s[-–—]\s|\s_\s", clean) if part.strip()]
        if len(parts) >= 2 and not cls._looks_like_website_name(parts[0]):
            return cls._safe_folder_name(parts[0], fallback=""), cls._safe_folder_name(" - ".join(parts[1:]), fallback="")

        # If only a clean name remains, use it as a possible singer folder but do not invent a song title.
        return cls._safe_folder_name(clean, fallback=""), ""

    @classmethod
    def analyze(cls, path):
        """Return classification plus normalized audio metadata. Never raises for a bad audio file."""
        path = Path(path)
        stat = path.stat()
        extension = path.suffix.lower()
        metadata = {
            "kind": "music",
            "subtype": "",
            "artist": "",
            "album": "",
            "title": path.stem,
            "track": "",
            "genre": "",
            "year": cls._year_from("", stat.st_mtime),
            "duration_seconds": None,
            "bitrate": None,
            "sample_rate": None,
            "bit_depth": None,
            "channels": None,
            "lossless": extension in {".flac", ".wav"},
            "format": extension.lstrip(".").upper() or "UNKNOWN",
            "source": "filename fallback",
            "filename_pattern": False,
        }

        if extension in {".mid", ".midi"}:
            metadata["kind"] = "midi"
            return metadata

        tags = {}
        if MutagenFile is not None:
            try:
                audio = MutagenFile(path, easy=True)
                if audio is not None:
                    tags = audio.tags or {}
                    metadata.update({
                        "artist": cls._first_tag(tags, "artist", "albumartist", "composer"),
                        "album": cls._first_tag(tags, "album"),
                        "title": cls._first_tag(tags, "title") or path.stem,
                        "track": cls._first_tag(tags, "tracknumber"),
                        "genre": cls._first_tag(tags, "genre"),
                        "year": cls._year_from(cls._first_tag(tags, "date", "year"), stat.st_mtime),
                        "source": "metadata",
                    })
                    info = getattr(audio, "info", None)
                    if info:
                        metadata["duration_seconds"] = round(float(getattr(info, "length", 0) or 0), 2)
                        metadata["bitrate"] = getattr(info, "bitrate", None)
                        metadata["sample_rate"] = getattr(info, "sample_rate", None)
                        metadata["bit_depth"] = getattr(info, "bits_per_sample", None)
                        metadata["channels"] = getattr(info, "channels", None)
            except Exception:
                # File extension can be audio while contents are not parseable; filename routing still works.
                pass

        # Website/domain text must never become an artist, album or folder name.
        if cls._looks_like_website_name(metadata["artist"]):
            metadata["artist"] = ""
        if cls._looks_like_website_name(metadata["album"]):
            metadata["album"] = ""

        # Filename is the first fallback when Artist metadata is absent.
        if not metadata["artist"]:
            inferred_artist, inferred_title = cls._infer_from_filename(path.stem)
            if inferred_artist:
                metadata["artist"] = inferred_artist
                if inferred_title:
                    metadata["title"] = inferred_title
                    metadata["filename_pattern"] = True
                metadata["source"] = "filename inferred"

        combined = " ".join([
            cls._clean_filename_for_inference(path.stem).casefold(),
            metadata["artist"].casefold(),
            metadata["album"].casefold(),
            metadata["title"].casefold(),
            metadata["genre"].casefold(),
        ])

        ambient_subtype = cls._find_subtype(combined, cls.AMBIENT_KEYWORDS)
        if ambient_subtype != "سایر":
            metadata.update({"kind": "ambient", "subtype": ambient_subtype})
            return metadata

        effect_markers = ["sfx", "sound effect", "soundeffect", "effect", " fx", "افکت"]
        if cls._keyword_match(combined, effect_markers):
            metadata.update({"kind": "effect", "subtype": cls._find_subtype(combined, cls.EFFECT_KEYWORDS)})
            return metadata

        recording_subtype = cls._find_subtype(combined, cls.RECORDING_KEYWORDS)
        if recording_subtype != "سایر":
            metadata.update({"kind": "recording", "subtype": recording_subtype, "year_month": cls._month_from(stat.st_mtime)})
            return metadata

        book_markers = ["audiobook", "audio book", "book", "کتاب صوتی", "کتاب"]
        if cls._keyword_match(combined, book_markers):
            metadata.update({"kind": "audiobook"})
            return metadata

        podcast_markers = ["podcast", "episode", "ep.", "پادکست", "قسمت"]
        is_podcast_tag = bool(cls._first_tag(tags, "podcast", "podcasturl"))
        if is_podcast_tag or cls._keyword_match(combined, podcast_markers):
            metadata.update({"kind": "podcast"})
            return metadata

        instrumental_markers = ["instrumental", "karaoke", "بی کلام", "بیکلام"]
        if cls._keyword_match(combined, instrumental_markers):
            metadata["instrumental"] = True
        else:
            metadata["instrumental"] = False
        return metadata

    @staticmethod
    def _remove_leading_zeros(filename_stem):
        """Remove only a run of leading ASCII/Persian/Arabic zeros and its separator."""
        cleaned = re.sub(r"^[0٠۰]+[\s._-]*", "", filename_stem)
        return cleaned.strip() or filename_stem

    @classmethod
    def destination_filename(cls, path, hint):
        """Create a clean destination name without renaming the original source file."""
        path = Path(path)
        cleaned_original = f"{cls._remove_leading_zeros(path.stem)}{path.suffix.lower()}"

        if hint.get("kind") != "music":
            return cleaned_original

        title = cls._safe_folder_name(hint.get("title"), fallback="")
        artist = cls._safe_folder_name(hint.get("artist"), fallback="")
        has_verified_metadata = hint.get("source") == "metadata"
        has_clear_filename_pattern = bool(hint.get("filename_pattern"))
        if not title or not artist or not (has_verified_metadata or has_clear_filename_pattern):
            return cleaned_original

        # User preference: Song title - singer.ext
        return f"{title} - {artist}{path.suffix.lower()}"

    @classmethod
    def folder_parts(cls, hint):
        """Translate the analysis result to ArchivePro's Persian destination tree."""
        kind = hint.get("kind", "music")
        raw_artist = hint.get("artist") or ""
        raw_album = hint.get("album") or ""
        artist = cls._safe_folder_name(raw_artist)
        album = cls._safe_folder_name(raw_album)

        if kind == "midi": 
            return ["موسیقی", "MIDI"]
        if kind == "ambient":
            return ["صدای_محیط", hint.get("subtype") or "سایر"]
        if kind == "effect":
            return ["افکت‌های_صوتی", hint.get("subtype") or "سایر"]
        if kind == "recording":
            return ["ضبط‌ها", hint.get("subtype") or "ویس", hint.get("year_month") or "بدون_تاریخ"]
        if kind == "podcast":
            show = cls._safe_folder_name(hint.get("album") or hint.get("artist"))
            return ["پادکست", show, hint.get("year") or "بدون_تاریخ"]
        if kind == "audiobook":
            author = cls._safe_folder_name(hint.get("artist"))
            book = cls._safe_folder_name(hint.get("album") or hint.get("title"))
            return ["کتاب_صوتی", author, book]

        parts = ["موسیقی"]
        if hint.get("lossless"):
            parts.extend(["Lossless", hint.get("format") or "سایر"])
        elif hint.get("instrumental"):
            parts.append("بی‌کلام")

        if not raw_artist or cls._looks_like_website_name(raw_artist):
            return parts + ["دسته‌بندی نشده"]
        # Artist is known but album is not: place the audio directly under the artist folder.
        if not raw_album or cls._looks_like_website_name(raw_album):
            return parts + [artist]
        return parts + [artist, album]
