import hashlib
import mimetypes

# Comprehensive Extension Lists for ArchivePro
IMAGE_EXTS = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.tiff', '.tga', '.ico', '.heic', '.avif'}
RAW_PHOTO_EXTS = {'.cr2', '.nef', '.arw', '.dng', '.orf', '.sr2', '.crw', '.raf'}
VECTOR_EXTS = {'.svg', '.eps', '.ai', '.cdr', '.wmf', '.emf'}
GRAPHICS_PROJECTS = {'.psd', '.psb', '.fig', '.sketch', '.xd'}
FONT_EXTS = {'.ttf', '.otf', '.woff', '.woff2', '.fnt', '.fon'}

VIDEO_EXTS = {'.mp4', '.mkv', '.avi', '.mov', '.wmv', '.flv', '.webm', '.m4v', '.mpeg', '.mpg', '.3gp'}
VIDEO_PROJECTS = {'.aep', '.prproj', '.veg', '.fcp'}
AUDIO_EXTS = {'.mp3', '.wav', '.flac', '.aac', '.ogg', '.m4a', '.wma', '.aiff', '.mid', '.midi'}
AUDIO_PROJECTS = {'.flp', '.als', '.logic', '.cpr'}

WORD_EXTS = {'.doc', '.docx', '.rtf', '.pages'}
EXCEL_EXTS = {'.xls', '.xlsx', '.csv', '.ods', '.xlsm'}
POWERPOINT_EXTS = {'.ppt', '.pptx', '.key', '.odp'}
OPENDOCUMENT_EXTS = {'.odt', '.ods', '.odp', '.odg', '.odf'}
PDF_EXTS = {'.pdf'}
EBOOK_EXTS = {'.epub', '.mobi', '.azw3', '.djvu', '.fb2'}
TEXT_EXTS = {'.txt', '.md', '.log', '.ans'}

ARCH_EXTS = {'.dwg', '.dxf', '.skp', '.rvt', '.ifc', '.step', '.stp', '.iges', '.igs'}
THREE_D_EXTS = {'.stl', '.obj', '.fbx', '.max', '.c4d', '.blend', '.step', '.stp', '.iges'}
ENGINEERING_EXTS = {'.gbr', '.dsn', '.pcbdoc', '.schdoc'}

WINDOWS_APP_EXTS = {'.exe', '.msi', '.bat', '.cmd', '.scr'}
ANDROID_APP_EXTS = {'.apk', '.xapk'}
MAC_APP_EXTS = {'.dmg', '.pkg', '.app'}
LINUX_APP_EXTS = {'.deb', '.rpm', '.run', '.sh'}
IOS_APP_EXTS = {'.ipa'}

CODE_EXTS = {'.py', '.js', '.html', '.css', '.cpp', '.c', '.cs', '.java', '.php', '.go', '.rs', '.ts', '.swift'}
WEB_EXTS = {'.html', '.htm', '.php', '.asp', '.aspx', '.jsp'}
DATA_EXTS = {'.json', '.xml', '.yaml', '.yml', '.toml'}
DATABASE_EXTS = {'.sql', '.db', '.sqlite', '.mdb', '.accdb'}

ZIP_EXTS = {'.zip', '.rar', '.7z', '.tar', '.gz', '.bz2', '.xz'}
LINUX_ARCHIVE_EXTS = {'.tar.gz', '.tgz', '.tar.bz2', '.tbz2', '.tar.xz', '.txz'}
ISO_EXTS = {'.iso', '.img', '.vhd', '.vmdk', '.cue', '.bin'}

GAME_EXTS = {'.unity', '.uproject', '.godot', '.sav', '.rom'}
OTHER_EXTS = {'.torrent', '.log', '.tmp', '.bak', '.old'}

class FileAnalyzer:
    @staticmethod
    def hash_file(file_path):
        md5_hash = hashlib.md5()
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                md5_hash.update(byte_block)
                sha256_hash.update(byte_block)
        return md5_hash.hexdigest(), sha256_hash.hexdigest()

    @staticmethod
    def basic_metadata(file_path):
        stat = file_path.stat()
        mime_type, _ = mimetypes.guess_type(file_path)
        return {
            "size": stat.st_size,
            "mtime": stat.st_mtime,
            "mime": mime_type or "application/octet-stream"
        }
