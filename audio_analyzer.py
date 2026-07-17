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
    SINGER_MAP = {
        "farzad farzin": "فرزاد فرزین", "ehsan khajeh amiri": "احسان خواجه امیری",
        "ehsan khajeamiri": "احسان خواجه امیری", "behnam bani": "بهنام بانی",
        "shadmehr": "شادمهر عقیلی", "dariush": "داریوش", "ebi": "ابی",
        "moein": "معین", "hayedeh": "هایده", "mahasti": "مهستی", "googoosh": "گوگوش",
        "siavash ghomayshi": "سیاوش قمیشی", "shajarian": "شجریان",
        "mohsen yeganeh": "محسن یگانه", "mohsen chavoshi": "محسن چاوشی",
        "reza sadeghi": "رضا صادقی", "sirvan khosravi": "سیروان خسروی",
        "hamid hiraad": "حمید هیراد", "mohsen ebrahimzadeh": "محسن ابراهیم زاده",
    }

    @classmethod
    def _to_persian_artist(cls, value):
        normalized = str(value or "").casefold().strip()
        for alias, persian in cls.SINGER_MAP.items():
            if alias in normalized:
                return persian
        return str(value or "").strip()

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
<<<<<<< HEAD
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

        metadata["artist"] = cls._to_persian_artist(metadata["artist"])

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
=======
                if audio and audio.tags:
                    meta["artist"] = cls.get_persian_artist(audio.tags.get("artist", [""])[0])
                    meta["album"] = audio.tags.get("album", [""])[0]
                    meta["title"] = audio.tags.get("title", [""])[0] or path.stem
                    d = audio.tags.get("date", [""])[0]
                    if d: meta["year"] = str(d)[:4]
            except: pass
        return meta
>>>>>>> 4475405e9a62faad7ce612d30a163a98aa2cedc0

    @classmethod
    def destination_filename(cls, path, meta):
        ext = path.suffix.lower()
        title = cls._clean(meta["title"])
        artist = cls._clean(meta["artist"])
        if title and artist: return f"{title} - {artist}{ext}"
        return f"{cls._clean(path.stem)}{ext}"
