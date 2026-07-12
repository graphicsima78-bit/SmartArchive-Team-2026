import hashlib
import mimetypes
from pathlib import Path

# Images
IMAGE_EXTS = {
    ".jpg", ".jpeg", ".png", ".bmp", ".webp", ".tif", ".tiff", ".gif", ".heic"
}

# Graphic design and vector files
VECTOR_EXTS = {".ai", ".psd", ".cdr", ".eps", ".svg", ".fig", ".sketch", ".afdesign"}

# Architecture and CAD files
ARCH_EXTS = {".dwg", ".dxf", ".skp", ".rvt", ".ifc", ".step", ".stp", ".iges", ".igs"}

# 3D files
THREE_D_EXTS = {
    ".blend", ".ma", ".mb", ".max", ".3ds", ".c4d", ".fbx", ".obj", ".dae",
    ".gltf", ".glb", ".usd", ".usda", ".usdc", ".stl", ".3mf", ".amf", ".vrm", ".x3d"
}

# Media
AUDIO_EXTS = {".mp3", ".wav", ".flac", ".aac", ".m4a", ".ogg", ".opus", ".wma", ".mid", ".midi"}
VIDEO_EXTS = {".mp4", ".mov", ".avi", ".mkv", ".webm", ".wmv", ".mpeg", ".mpg", ".m4v"}
MEDIA_EXTS = AUDIO_EXTS | VIDEO_EXTS

# Documents and Office files
PDF_EXTS = {".pdf"}
TEXT_EXTS = {".txt", ".md", ".rtf"}
DATA_EXTS = {".csv", ".json", ".xml", ".yaml", ".yml"}
WEB_EXTS = {".html", ".htm", ".css", ".js"}
CODE_EXTS = {".py", ".cpp", ".c", ".h", ".hpp", ".java", ".php", ".sql", ".cs", ".ts", ".go", ".rs", ".sh", ".ps1"}
DOC_EXTS = PDF_EXTS | TEXT_EXTS | DATA_EXTS | WEB_EXTS | CODE_EXTS
WORD_EXTS = {".doc", ".docx"}
EXCEL_EXTS = {".xls", ".xlsx", ".xlsm", ".csv"}
POWERPOINT_EXTS = {".ppt", ".pptx", ".pps", ".ppsx"}
OPENDOCUMENT_EXTS = {".odt", ".ods", ".odp"}
OFFICE_EXTS = WORD_EXTS | EXCEL_EXTS | POWERPOINT_EXTS | OPENDOCUMENT_EXTS

# Other file families
ZIP_EXTS = {".zip", ".rar", ".7z"}
LINUX_ARCHIVE_EXTS = {".tar", ".gz", ".bz2", ".xz", ".tgz", ".tbz", ".tbz2"}
ISO_EXTS = {".iso"}
COMPRESSED_EXTS = ZIP_EXTS | LINUX_ARCHIVE_EXTS | ISO_EXTS
WINDOWS_APP_EXTS = {".exe", ".msi", ".bat", ".cmd"}
ANDROID_APP_EXTS = {".apk"}
IOS_APP_EXTS = {".ipa"}
LINUX_APP_EXTS = {".deb", ".rpm", ".sh"}
MAC_APP_EXTS = {".dmg", ".pkg"}
SOFTWARE_EXTS = WINDOWS_APP_EXTS | ANDROID_APP_EXTS | IOS_APP_EXTS | LINUX_APP_EXTS | MAC_APP_EXTS
DATABASE_EXTS = {".sql", ".db", ".sqlite", ".sqlite3", ".mdb", ".accdb"}
GAME_EXTS = {".unity", ".uproject", ".godot", ".sav", ".rom"}
OTHER_EXTS = {".torrent", ".log", ".tmp", ".bak", ".old"}


class FileAnalyzer:
    @staticmethod
    def hash_file(path):
        md5 = hashlib.md5()
        sha256 = hashlib.sha256()
        with open(path, "rb") as file:
            for chunk in iter(lambda: file.read(1024 * 1024), b""):
                md5.update(chunk)
                sha256.update(chunk)
        return md5.hexdigest(), sha256.hexdigest()

    @staticmethod
    def basic_metadata(path):
        file_path = Path(path)
        stat = file_path.stat()
        mime, _ = mimetypes.guess_type(str(file_path))
        return {
            "name": file_path.name,
            "size": stat.st_size,
            "mtime": stat.st_mtime,
            "suffix": file_path.suffix.lower(),
            "mime": mime,
        }
