from pathlib import Path
import hashlib
import mimetypes

IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".webp", ".tif", ".tiff"}
VECTOR_EXTS = {".ai", ".psd", ".cdr", ".eps", ".svg", ".fig", ".sketch", ".afdesign"}
ARCH_EXTS = {".dwg", ".dxf", ".ifc", ".step", ".stp", ".iges", ".igs"}
THREE_D_EXTS = {".blend", ".ma", ".mb", ".c4d", ".fbx", ".obj", ".gltf", ".glb", ".usd", ".usda", ".usdc"}
DOC_EXTS = {".pdf", ".txt", ".md", ".rtf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx"}
MEDIA_EXTS = {".mp3", ".wav", ".flac", ".aac", ".m4a", ".mp4", ".mov", ".avi", ".mkv", ".webm"}
ZIP_EXTS = {".zip", ".rar", ".7z", ".tar", ".gz", ".bz2"}


class FileAnalyzer:
    @staticmethod
    def hash_file(path):
        md5 = hashlib.md5()
        sha256 = hashlib.sha256()
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(1024 * 1024), b""):
                md5.update(chunk)
                sha256.update(chunk)
        return md5.hexdigest(), sha256.hexdigest()

    @staticmethod
    def basic_metadata(path):
        p = Path(path)
        stat = p.stat()
        mime, _ = mimetypes.guess_type(str(p))
        return {
            "name": p.name,
            "size": stat.st_size,
            "mtime": stat.st_mtime,
            "suffix": p.suffix.lower(),
            "mime": mime,
        }
