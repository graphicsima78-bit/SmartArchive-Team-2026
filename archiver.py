import os
import shutil
import threading
import re
from pathlib import Path
from PySide6.QtCore import QObject, Signal

# لیست جامع خوانندگان برای تبدیل و ادغام
SINGER_DB = {
    "farzad farzin": "فرزاد فرزین",
    "ehsan khajeh amiri": "احسان خواجه امیری",
    "behnam bani": "بهنام بانی",
    "shadmehr": "شادمهر عقیلی",
    "dariush": "داریوش",
    "ebi": "ابی",
    "moein": "معین",
    "hayedeh": "هایده",
    "mahasti": "مهستی",
    "googoosh": "گوگوش",
    "siavash ghomayshi": "سیاوش قمیشی",
    "homayoun shajarian": "همایون شجریان",
    "mohsen yeganeh": "محسن یگانه",
    "mohsen chavoshi": "محسن چاوشی",
    "reza sadeghi": "رضا صادقی",
    "hamid hiraad": "حمید هیراد",
}

class ArchiveWorker(QObject):
    progress = Signal(int)
    log = Signal(str)
    finished = Signal()

    def __init__(self, source, dest, audio_pref="persian"):
        super().__init__()
        self.source = Path(source)
        self.dest = Path(dest)
        self.audio_pref = audio_pref
        self._stop = threading.Event()

    def _clean(self, text):
        if not text: return ""
        # حذف اعداد و علائم از ابتدا
        text = re.sub(r"^[0-9٠-٩\s._-]+", "", str(text))
        return re.sub(r'[<>:"/\\|?*]+', "_", text.strip())[:80]

    def _get_persian(self, name):
        if not name: return ""
        nl = name.lower()
        for eng, per in SINGER_DB.items():
            if eng in nl: return per
        return name

    def _sync_folder(self, parent, target_name):
        """اگر پوشه مشابه وجود دارد از آن استفاده کن، وگرنه بساز"""
        if not parent.exists(): return target_name
        norm_target = target_name.lower().replace(" ", "").replace("_", "")
        try:
            for entry in os.scandir(parent):
                if entry.is_dir():
                    if entry.name.lower().replace(" ", "").replace("_", "") == norm_target:
                        # اگر نام فعلی با نام هدف فرق دارد (مثلا انگلیسی به فارسی)، تغییر نام بده
                        if entry.name != target_name and self.audio_pref == "persian":
                            new_path = parent / target_name
                            try: 
                                os.rename(entry.path, new_path)
                                return target_name
                            except: return entry.name
                        return entry.name
        except: pass
        return target_name

    def run(self):
        try:
            files = [p for p in self.source.rglob("*") if p.is_file()]
            total = len(files)
            if total == 0: self.progress.emit(100); return

            for i, path in enumerate(files):
                if self._stop.is_set(): break
                ext = path.suffix.lower()
                
                # منطق صوتی
                if ext in {'.mp3', '.wav', '.flac'}:
                    artist = "سایر_آهنگ‌ها"
                    # در اینجا فرض بر این است که متادیتا در نسخه‌های قبل خوانده شده، 
                    # برای سادگی و عدم کرش، از نام فایل برای تشخیص استفاده می‌کنیم
                    parts = re.split(r"\s[-–—_]\s", path.stem)
                    raw_artist = parts[0] if len(parts) >= 2 else ""
                    
                    if raw_artist:
                        pref_name = self._get_persian(raw_artist) if self.audio_pref == "persian" else raw_artist
                        root = self.dest / "موسیقی_و_صوت"
                        root.mkdir(parents=True, exist_ok=True)
                        
                        folder_name = self._sync_folder(root, pref_name)
                        final_dir = root / folder_name
                        final_name = f"{self._clean(path.stem)}{ext}"
                    else:
                        final_dir = self.dest / "موسیقی_و_صوت" / "سایر_آهنگ‌ها"
                        final_name = f"{self._clean(path.stem)}{ext}"
                
                # سایر فایل‌ها
                elif ext in {'.psd', '.cdr', '.ai'}:
                    final_dir = self.dest / "گرافیک_و_طراحی"
                    final_name = path.name
                elif ext in {'.jpg', '.png', '.webp'}:
                    final_dir = self.dest / "تصاویر"
                    final_name = self._clean(path.stem) + ext
                else:
                    final_dir = self.dest / "سایر_موارد"
                    final_name = path.name

                final_dir.mkdir(parents=True, exist_ok=True)
                dest = final_dir / final_name
                if dest.exists(): dest = final_dir / f"{Path(final_name).stem}_کپی{Path(final_name).suffix}"
                
                try:
                    shutil.copy2(path, dest)
                    self.log.emit(f"بایگانی: {final_name}")
                except: pass
                
                self.progress.emit(int((i+1)*100/total))
            
            self.log.emit("--- پایان موفقیت‌آمیز ---")
        finally:
            self.finished.emit()

    def stop(self): self._stop.set()
