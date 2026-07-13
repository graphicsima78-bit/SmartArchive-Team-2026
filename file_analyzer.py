# Expanded Extension Lists for Ultimate Categorization
IMAGE_EXTS = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.tiff', '.tga', '.ico', '.heic', '.avif'}
RAW_PHOTO_EXTS = {'.cr2', '.nef', '.arw', '.dng', '.orf', '.sr2', '.crw', '.raf'}
VECTOR_EXTS = {'.svg', '.eps', '.ai', '.cdr', '.wmf', '.emf'}
GRAPHICS_PROJECTS = {'.psd', '.psb', '.fig', '.sketch', '.xd'}
FONT_EXTS = {'.ttf', '.otf', '.woff', '.woff2', '.fnt', '.fon'}

VIDEO_EXTS = {'.mp4', '.mkv', '.avi', '.mov', '.wmv', '.flv', '.webm', '.m4v', '.mpeg', '.mpg', '.3gp'}
VIDEO_PROJECTS = {'.aep', '.prproj', '.veg', '.fcp'}
AUDIO_EXTS = {'.mp3', '.wav', '.flac', '.aac', '.ogg', '.m4a', '.wma', '.aiff', '.mid', '.midi'}
AUDIO_PROJECTS = {'.flp', '.als', '.logic', '.cpr'}

DOC_EXTS = {'.doc', '.docx', '.rtf', '.odt', '.pages'}
EXCEL_EXTS = {'.xls', '.xlsx', '.csv', '.ods', '.xlsm'}
POWERPOINT_EXTS = {'.ppt', '.pptx', '.key', '.odp'}
PDF_EXTS = {'.pdf'}
EBOOK_EXTS = {'.epub', '.mobi', '.azw3', '.djvu', '.fb2'}
TEXT_EXTS = {'.txt', '.md', '.log', '.ans'}

CAD_EXTS = {'.dwg', '.dxf', '.rvt', '.pln', '.3dm'}
THREE_D_EXTS = {'.stl', '.obj', '.fbx', '.max', '.c4d', '.blend', '.step', '.stp', '.iges'}
ENGINEERING_EXTS = {'.gbr', '.dsn', '.pcbdoc', '.schdoc'}

WINDOWS_APP_EXTS = {'.exe', '.msi', '.bat', '.cmd', '.scr'}
ANDROID_APP_EXTS = {'.apk', '.xapk'}
MAC_APP_EXTS = {'.dmg', '.pkg', '.app'}
LINUX_APP_EXTS = {'.deb', '.rpm', '.run', '.sh'}

CODE_EXTS = {'.py', '.js', '.html', '.css', '.cpp', '.c', '.cs', '.java', '.php', '.go', '.rs', '.ts', '.swift'}
DATA_EXTS = {'.json', '.xml', '.yaml', '.yml', '.toml'}
DATABASE_EXTS = {'.sql', '.db', '.sqlite', '.mdb', '.accdb'}

ZIP_EXTS = {'.zip', '.rar', '.7z', '.tar', '.gz', '.bz2', '.xz'}
ISO_EXTS = {'.iso', '.img', '.vhd', '.vmdk', '.cue', '.bin'}

class FileAnalyzer:
    @staticmethod
    def get_file_info(file_path):
        ext = file_path.suffix.lower()
        # Mapping logic here...
        return {"ext": ext, "category": "unknown"}
