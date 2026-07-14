import os
import shutil
import threading
from datetime import datetime
from pathlib import Path
from PySide6.QtCore import QObject, Signal

class ArchiveWorker(QObject):
    progress = Signal(int)
    log = Signal(str)
    finished = Signal()

    def __init__(self, source_dir, dest_dir, use_date=True, use_persian=False, 
                 delete_after_copy=False, reprocess_archived=False, 
                 content_analysis=False, use_ocr=True, quarantine_duplicates=False, 
                 focus_types=None, family_location_when_dated=True, 
                 quick_transfer=False, project_config=None):
        super().__init__()
        self.source_dir = Path(source_dir)
        self.dest_dir = Path(dest_dir)
        self.use_date = use_date
        self.use_persian = use_persian
        self.move_mode = delete_after_copy
        self.reprocess_archived = reprocess_archived
        self.content_analysis = content_analysis
        self.use_ocr = use_ocr
        self.quarantine_duplicates = quarantine_duplicates
        self.focus_types = set(focus_types or [])
        self.quick_transfer = quick_transfer
        self.project_config = project_config
        self._stop = threading.Event()
        self._pause = threading.Event()
        self._pause.set()

    def _get_supreme_taxonomy(self, name):
        name = name.lower()
        # 1. Architecture & Construction Elements
        if any(x in name for x in ["plaster", "گچبری", "molding", "سقف", "ستون", "ستونها"]): return ["معماری", "عناصر_ساختمانی"]
        if any(x in name for x in ["curtain", "پرده", "blind", "شید"]): return ["معماری", "تجهیزات_داخلی", "پرده"]
        if any(x in name for x in ["chandelier", "لوستر", "lamp", "لامپ", "light", "آباژور", "shade", "روشنایی"]): return ["معماری", "تجهیزات_داخلی", "روشنایی"]
        if any(x in name for x in ["ac", "cooler", "کولر", "heater", "بخاری", "radiator", "پکیج", "تهویه"]): return ["معماری", "تجهیزات_داخلی", "تأسیسات"]

        # 2. Furniture & Decor
        if any(x in name for x in ["table", "میز", "desk"]): return ["مبلمان", "میز_و_سطوح"]
        if any(x in name for x in ["chair", "صندلی", "sofa", "مبل", "bench", "راحتی"]): return ["مبلمان", "نشیمن"]
        if any(x in name for x in ["bed", "خواب", "mattress", "تخت", "pillow", "بالش", "لحاف"]): return ["مبلمان", "سرویس_خواب"]
        if any(x in name for x in ["frame", "تابلو", "painting", "نقاشی", "art", "مجسمه", "تندیس"]): return ["هنر_و_دکوری", "تابلو_و_تزئینات"]
        if any(x in name for x in ["basket", "سبد", "vase", "گلدان", "mirror", "آینه", "دکوری"]): return ["هنر_و_دکوری", "اکسسوری"]

        # 3. IT & Technology
        if any(x in name for x in ["monitor", "مانیتور", "display", "صفحه_نمایش"]): return ["تکنولوژی", "سخت‌افزار", "نمایشگر"]
        if any(x in name for x in ["pc", "computer", "کیس", "کامپیوتر", "laptop", "لپ‌تاپ"]): return ["تکنولوژی", "سخت‌افزار", "سیستم"]
        if any(x in name for x in ["keyboard", "کیبورد", "mouse", "موس", "موشواره", "صفحه_کلید"]): return ["تکنولوژی", "سخت‌افزار", "جانبی"]
        if any(x in name for x in ["tv", "تلویزیون", "audio", "ضبط", "speaker", "باند", "بلندگو"]): return ["تکنولوژی", "صوتی_تصویری"]

        # 4. Lifestyle & Small Objects
        if any(x in name for x in ["cup", "glass", "لیوان", "mug", "ظرف", "بشقاب", "پارچ"]): return ["سبک_زندگی", "ظروف"]
        if any(x in name for x in ["tissue", "دستمال", "napkin", "کاغذی"]): return ["سبک_زندگی", "بهداشتی"]
        if any(x in name for x in ["cigar", "سیگار", "smoke", "lighter", "فندک"]): return ["سبک_زندگی", "شخصی"]

        # 5. Metals & Materials
        if any(x in name for x in ["gold", "طلا", "luxury", "لوکس"]): return ["متریال_خام", "فلزات", "طلا"]
        if any(x in name for x in ["silver", "نقره", "chrome", "platinum"]): return ["متریال_خام", "فلزات", "نقره"]
        if any(x in name for x in ["copper", "مس", "brass", "برنج", "bronze", "مفرغ"]): return ["متریال_خام", "فلزات", "مس_و_برنج"]
        if any(x in name for x in ["iron", "آهن", "steel", "فولاد", "metal", "فلز"]): return ["متریال_خام", "فلزات", "آهن_و_فولاد"]
        if any(x in name for x in ["fabric", "پارچه", "textile", "leather", "چرم", "پنبه"]): return ["متریال_خام", "منسوجات"]
        
        # 6. Geography & Symbols
        if any(x in name for x in ["flag", "پرچم", "national"]): return ["نمادها_و_ارز", "پرچم"]
        if any(x in name for x in ["money", "cash", "پول", "coin", "سکه", "dollar", "دلار"]): return ["نمادها_و_ارز", "پول"]
        if any(x in name for x in ["earth", "globe", "کره_زمین", "world", "جهان"]): return ["جغرافیا", "کره_زمین"]
        if any(x in name for x in ["city", "شهر", "country", "کشور", "map", "نقشه"]): return ["جغرافیا", "شهر_و_نقشه"]

        # 7. Transportation
        if any(x in name for x in ["car", "ماشین", "خودرو", "truck", "کامیون", "bus", "اتوبوس"]): return ["حمل_و_نقل", "خودرو"]
        if any(x in name for x in ["plane", "هواپیما", "ship", "کشتی", "boat", "قایق"]): return ["حمل_و_نقل", "هوایی_و_دریایی"]

        return None

    def _get_ultimate_path(self, path):
        ext = path.suffix.lower()
        name = path.stem.lower()
        
        # Special logic for Content Creation
        if any(x in name for x in ["reel", "ریلز", "story", "استوری", "thumbnail", "کاور"]):
            return ["۰۰_تولید_محتوا", "قالب‌ها_و_چیدمان"]

        supreme = self._get_supreme_taxonomy(name)
        
        if ext in {'.jpg', '.png', '.webp', '.tiff', '.bmp', '.heic'}:
            root = "۰۱_کتابخانه_تصاویر"
            if supreme: return [root] + supreme
            return [root, "سایر_تصاویر"]

        if ext in {'.ai', '.eps', '.svg', '.cdr', '.psd'}:
            root = "۰۲_گرافیک_وکتور_و_لایه_باز"
            if supreme: return [root] + supreme
            return [root, "سایر_وکتورها"]

        if ext in {'.mp4', '.mkv', '.mov', '.avi'}: return ["۰۳_رسانه_تصویری"]
        if ext in {'.mp3', '.wav', '.flac'}: return ["۰۴_صوت_و_موسیقی"]
        if ext in {'.pdf', '.docx', '.epub', '.txt'}: return ["۰۵_اسناد_و_آموزش"]
        if ext in {'.dwg', '.obj', '.fbx', '.max', '.blend'}: return ["۰۶_مهندسی_و_فنی"]
        if ext in {'.zip', '.rar', '.7z', '.exe', '.msi'}: return ["۰۷_سیستمی_و_فشرده"]
        
        return ["۹۹_سایر_موارد"]

    def run(self):
        try:
            self.log.emit("شروع فرآیند بایگانی...")
            files = [p for p in self.source_dir.rglob("*") if p.is_file()]
            total = len(files)
            if total == 0:
                self.log.emit("هیچ فایلی برای پردازش پیدا نشد.")
                self.progress.emit(100)
                return

            for i, path in enumerate(files):
                if self._stop.is_set():
                    self.log.emit("توقف توسط کاربر.")
                    break
                
                # Check for pause
                while not self._pause.is_set():
                    if self._stop.is_set(): break
                    threading.Event().wait(0.1)

                parts = self._get_ultimate_path(path)
                target = self.dest_dir.joinpath(*parts)
                target.mkdir(parents=True, exist_ok=True)
                
                dest = target / path.name
                if dest.exists():
                    dest = target / f"{path.stem}_{int(datetime.now().timestamp())}{path.suffix}"
                
                try:
                    shutil.copy2(path, dest)
                    if self.move_mode:
                        os.remove(path)
                    self.log.emit(f"موفق: {path.name} -> {parts[-1]}")
                except Exception as e:
                    self.log.emit(f"خطا در {path.name}: {str(e)}")
                
                self.progress.emit(int((i+1)*100/total))
            
            self.log.emit("عملیات با موفقیت به پایان رسید.")
            self.progress.emit(100)
        except Exception as outer_e:
            self.log.emit(f"خطای کلی سیستم: {str(outer_e)}")
        finally:
            self.finished.emit()

    def stop(self):
        self._stop.set()
        self._pause.set()

    def pause(self):
        self._pause.clear()

    def resume(self):
        self._pause.set()
