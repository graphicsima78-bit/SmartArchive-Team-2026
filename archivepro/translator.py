"""
translator.py
سیستم ترجمه دو زبانه (فارسی/انگلیسی) - پیش‌فرض انگلیسی
"""


class Translator:
    def __init__(self, lang="en"):
        self.lang = lang
        self.strings = {
            "en": {
                "app_title": "ArchivePro - Smart Archiving",
                "menu_file": "File", "menu_exit": "Exit", "menu_help": "Help", "about": "About",
                "about_text": "ArchivePro - Smart Archiving\nVersion 3.0\nDeveloper: Majid Dehaki",
                "language": "Language", "theme": "Theme",
                "source": "Source:", "source_multi": "Source folder(s):",
                "dest": "Destination:", "add": "Add", "browse": "Browse", "clear": "Clear",
                "mode": "Mode:", "mode_copy": "Copy", "mode_move": "Move",
                "start": "Start", "pause": "Pause", "resume": "Resume", "stop": "Stop",
                "ready": "Ready", "running": "Running...", "paused": "Paused",
                "stopping": "Stopping after current file...", "completed": "Completed",
                "progress_fmt": "%p% (%v / %m files)",
                "tab_general": "General", "tab_images": "Images", "tab_graphics": "Graphics / Vectors",
                "tab_audio": "Audio", "tab_software": "Software",
                "log": "Live Log", "report": "Report", "generate_report": "Generate Report (CSV)",
                "error": "Error", "error_source": "Please select at least one source folder.",
                "error_dest": "Please select a destination folder.",
                "error_same": "Source and destination cannot be the same.",
                "done_title": "Done", "done_text": "Operation finished.\n\nProcessed: {}\nSkipped/Duplicates: {}\nFailed: {}",
                # general tab
                "general_desc": "Mirrors every file from source to destination with the exact same "
                                "folder structure and names. No renaming, no content classification.",
                # images tab
                "images_desc": "Classifies photos either by family context (Shamsi date + location) or by "
                                "visual/graphic content (OCR + keyword rules), or a combination of both.",
                "images_mode_label": "Photo classification method:",
                "images_family": "Family photos (Shamsi date + location)",
                "images_work": "Work / graphic content (content-based)",
                "images_combined": "Combined (family if EXIF available, otherwise content-based)",
                "images_ocr": "Use OCR for text-heavy / document images",
                "images_screenshot": "Detect screenshots automatically",
                # graphics tab
                "graphics_desc": "Classifies design/vector files (AI, EPS, SVG, PSD, CDR, FIG, SKETCH, ...) "
                                 "by software and, if a same-name preview image exists, by visual content.",
                "graphics_preview_check": "If no preview image exists for a vector file, generate one "
                                          "(same base name, small size, local render when possible)",
                # audio tab
                "audio_desc": "Cleans track numbers and junk text from filenames/tags, groups all songs "
                              "of an artist into one folder (with album sub-folder if detected).",
                "audio_lang_label": "Do you want artist & track names in Persian or English?",
                "audio_lang_en": "English (default)",
                "audio_lang_fa": "Persian",
                "audio_album_folder": "Create album sub-folder when album is detected",
                # software tab
                "software_desc": "Classifies installers by platform (Windows/Android/macOS/Linux/iOS) "
                                 "and then by application category (2D/3D design, CAD, Office, Utilities, ...).",
                "software_online_check": "Try to detect app category online (optional, default off)",
                "duplicate_found": "Duplicate (already archived) -> skipped",
                "files_label": "Files: {} / {}",
            },
            "fa": {
                "app_title": "ArchivePro - بایگانی هوشمند",
                "menu_file": "فایل", "menu_exit": "خروج", "menu_help": "راهنما", "about": "درباره",
                "about_text": "ArchivePro - بایگانی هوشمند\nنسخه ۳.۰\nتوسعه‌دهنده: مجید دهکی",
                "language": "زبان", "theme": "تم",
                "source": "مبدا:", "source_multi": "پوشه(های) مبدا:",
                "dest": "مقصد:", "add": "افزودن", "browse": "انتخاب", "clear": "پاک‌کردن",
                "mode": "حالت:", "mode_copy": "کپی", "mode_move": "جابجایی",
                "start": "شروع", "pause": "مکث", "resume": "ادامه", "stop": "توقف",
                "ready": "آماده", "running": "در حال اجرا...", "paused": "مکث شده",
                "stopping": "در حال توقف بعد از فایل جاری...", "completed": "انجام شد",
                "progress_fmt": "%p% (%v از %m فایل)",
                "tab_general": "دسته‌بندی کلی", "tab_images": "تصاویر", "tab_graphics": "گرافیک و وکتور",
                "tab_audio": "صوتی", "tab_software": "نرم‌افزارها",
                "log": "گزارش لحظه‌ای", "report": "گزارش", "generate_report": "تولید گزارش (CSV)",
                "error": "خطا", "error_source": "لطفاً حداقل یک پوشه مبدا انتخاب کنید.",
                "error_dest": "لطفاً یک پوشه مقصد انتخاب کنید.",
                "error_same": "پوشه مبدا و مقصد نباید یکسان باشند.",
                "done_title": "پایان", "done_text": "عملیات پایان یافت.\n\nپردازش‌شده: {}\nتکراری/رد‌شده: {}\nناموفق: {}",
                "general_desc": "همه فایل‌ها را با همان ساختار پوشه و نام از مبدا به مقصد منتقل می‌کند. "
                                "بدون تغییر نام و بدون دسته‌بندی محتوا.",
                "images_desc": "عکس‌ها را یا بر اساس بافت خانوادگی (تاریخ شمسی + مکان) یا بر اساس محتوای "
                                "بصری/گرافیکی (OCR + قوانین کلیدواژه)، یا ترکیبی از هر دو دسته‌بندی می‌کند.",
                "images_mode_label": "روش دسته‌بندی عکس‌ها:",
                "images_family": "عکس‌های خانوادگی (تاریخ شمسی + مکان)",
                "images_work": "کاری/گرافیکی (بر اساس محتوا)",
                "images_combined": "ترکیبی (اگر EXIF داشت خانوادگی، وگرنه محتوایی)",
                "images_ocr": "استفاده از OCR برای تصاویر متنی/سندی",
                "images_screenshot": "تشخیص خودکار اسکرین‌شات",
                "graphics_desc": "فایل‌های گرافیکی/وکتور (AI, EPS, SVG, PSD, CDR, FIG, SKETCH, ...) را بر اساس "
                                 "نرم‌افزار و در صورت وجود عکس پیش‌نمایش هم‌نام، بر اساس محتوای بصری دسته‌بندی می‌کند.",
                "graphics_preview_check": "اگر برای فایل وکتور پیش‌نمایش نبود، یکی بساز (هم‌نام، کم‌حجم، رندر محلی در صورت امکان)",
                "audio_desc": "شماره ترک و متن‌های اضافی را از نام فایل/تگ حذف می‌کند و همه آهنگ‌های یک خواننده را "
                              "در یک پوشه (و پوشه آلبوم در صورت شناسایی) قرار می‌دهد.",
                "audio_lang_label": "آیا می‌خواهید نام خواننده و آهنگ به فارسی باشد یا انگلیسی؟",
                "audio_lang_en": "انگلیسی (پیش‌فرض)",
                "audio_lang_fa": "فارسی",
                "audio_album_folder": "ساخت پوشه آلبوم در صورت شناسایی",
                "software_desc": "نصب‌کننده‌ها را بر اساس پلتفرم (ویندوز/اندروید/مک/لینوکس/iOS) و سپس بر اساس "
                                 "دسته‌ی برنامه (طراحی دوبعدی/سه‌بعدی، CAD، آفیس، ابزارها، ...) دسته‌بندی می‌کند.",
                "software_online_check": "تلاش برای تشخیص دسته برنامه با اینترنت (اختیاری، پیش‌فرض خاموش)",
                "duplicate_found": "تکراری (قبلاً بایگانی شده) -> رد شد",
                "files_label": "فایل‌ها: {} از {}",
            },
        }

    def tr(self, key, *args):
        text = self.strings.get(self.lang, {}).get(key, key)
        return text.format(*args) if args else text

    def set_lang(self, lang):
        if lang in ("fa", "en"):
            self.lang = lang
