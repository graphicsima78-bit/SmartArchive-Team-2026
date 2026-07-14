import os
import shutil
import threading
from datetime import datetime
from pathlib import Path
from PySide6.QtCore import QObject, Signal

# برای آنالیز موسیقی نیاز به یک متد کمکی داریم
try:
    from audio_analyzer import AudioAnalyzer
except ImportError:
    AudioAnalyzer = None

class ArchiveWorker(QObject):
    progress = Signal(int)
    log = Signal(str)
    finished = Signal()

    def __init__(self, source_dir, dest_dir, **kwargs):
        super().__init__()
        self.source_dir = Path(source_dir)
        self.dest_dir = Path(dest_dir)
        self.move_mode = bool(kwargs.get('delete_after_copy', False))
        self.use_date = bool(kwargs.get('use_date', True))
        self._stop = threading.Event()
        self._pause = threading.Event()
        self._pause.set()

    def _get_supreme_taxonomy(self, name):
        name = name.lower()
        # Interior & Structural (Strictly for keywords, not by extensions)
        if any(x in name for x in ["plaster", "گچبری", "molding", "ستون"]): return ["معماری", "عناصر_ساختمانی"]
        if any(x in name for x in ["curtain", "پرده", "chandelier", "لوستر", "lamp", "لامپ", "آباژور"]): return ["معماری", "تجهیزات_داخلی", "روشنایی"]
        if any(x in name for x in ["ac", "cooler", "کولر", "heater", "بخاری"]): return ["معماری", "تجهیزات_داخلی", "تأسیسات"]
        return None

    def _get_ultimate_path(self, path):
        ext = path.suffix.lower()
        name = path.stem.lower()

        # 1. GRAPHICS & DESIGN (Corel, Photoshop, etc.)
        if ext == ".psd": return ["تصاویر", "فایل‌های_لایه_باز", "Photoshop"]
        if ext == ".cdr": return ["گرافیک_وکتور", "CorelDRAW"]
        if ext in {'.ai', '.eps', '.svg'}: return ["گرافیک_وکتور", "Adobe_Illustrator" if ext == ".ai" else "سایر_وکتورها"]

        # 2. IMAGES
        if ext in {'.jpg', '.jpeg', '.png', '.webp', '.tiff'}:
            supreme = self._get_supreme_taxonomy(name)
            if supreme: return ["تصاویر"] + supreme
            return ["تصاویر", "سایر_عکس‌ها"]

        # 3. MUSIC (Artist > Album Logic)
        if ext in {'.mp3', '.wav', '.flac', '.m4a'}:
            if AudioAnalyzer:
                hint = AudioAnalyzer.analyze(path)
                artist = hint.get("artist", "خواننده_نامشخص")
                album = hint.get("album", "آلبوم_نامشخص")
                return ["موسیقی_و_صوت", artist, album]
            return ["موسیقی_و_صوت", "دسته‌بندی_نشده"]

        # 4. VIDEO
        if ext in {'.mp4', '.mkv', '.mov', '.avi'}: return ["ویدئو_و_رسانه"]

        # 5. ENGINEERING & ARCHITECTURE (CAD & 3D)
        if ext in {'.dwg', '.dxf', '.rvt', '.skp'}: return ["مهندسی_و_معماری", "نقشه‌های_CAD"]
        if ext in {'.stl', '.obj', '.fbx', '.max', '.blend'}: return ["مهندسی_و_معماری", "مدل‌های_سه‌بعدی"]

        # 6. DOCUMENTS & EDUCATION
        if ext in {'.pdf', '.docx', '.xlsx', '.pptx', '.txt', '.epub'}: return ["اسناد_و_آموزش"]

        # 7. SYSTEM & APPS vs ARCHIVES
        if ext in {'.exe', '.msi', '.apk', '.dmg'}: return ["نرم‌افزار_و_سیستم", "فایل‌های_نصبی"]
        if ext in {'.zip', '.rar', '.7z'}: return ["بایگانی_و_فشرده"]
        if ext in {'.iso', '.img', '.vhd', '.bak', '.cdi'}: return ["بایگانی_و_فشرده", "ایمیج_و_بک‌آپ_دیسک"]

        return ["سایر_موارد"]

    def run(self):
        try:
            files = [p for p in self.source_dir.rglob("*") if p.is_file()]
            total = len(files)
            for i, path in enumerate(files):
                if self._stop.is_set(): break
                while not self._pause.is_set():
                    if self._stop.is_set(): break
                    threading.Event().wait(0.1)

                parts = self._get_ultimate_path(path)
                target = self.dest_dir.joinpath(*parts)
                target.mkdir(parents=True, exist_ok=True)
                
                dest = target / path.name
                if dest.exists():
                    dest = target / f"{path.stem}_{int(datetime.now().timestamp())}{path.suffix}"
                
                shutil.copy2(path, dest)
                if self.move_mode: os.remove(path)
                self.log.emit(f"بایگانی شد: {path.name} -> {parts[0]}")
                self.progress.emit(int((i+1)*100/max(total, 1)))
            
            self.log.emit("عملیات با موفقیت به پایان رسید.")
        except Exception as e:
            self.log.emit(f"خطا: {str(e)}")
        finally:
            self.finished.emit()

    def stop(self): self._stop.set(); self._pause.set()
