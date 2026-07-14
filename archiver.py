import os
import shutil
import threading
from datetime import datetime
from pathlib import Path
from PySide6.QtCore import QObject, Signal

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
        self._stop = threading.Event()
        self._pause = threading.Event()
        self._pause.set()

    def _get_target_info(self, path):
        ext = path.suffix.lower()
        name = path.stem.lower()
        
        # Logic for Corel/PS
        if ext == ".psd": return ["تصاویر", "فایل‌های_لایه_باز", "Photoshop"], path.name
        if ext == ".cdr": return ["گرافیک_وکتور", "CorelDRAW"], path.name
        if ext in {'.ai', '.eps', '.svg'}: return ["گرافیک_وکتور", "Vector_Assets"], path.name

        # Audio Logic
        if ext in {'.mp3', '.wav', '.flac', '.m4a'}:
            if AudioAnalyzer:
                hint = AudioAnalyzer.analyze(path)
                parts = AudioAnalyzer.folder_parts(hint)
                if parts and parts[0] == "موسیقی": parts[0] = "موسیقی_و_صوت"
                new_name = AudioAnalyzer.destination_filename(path, hint)
                return parts, new_name
            return ["موسیقی_و_صوت", "دسته‌بندی_نشده"], path.name

        # Default paths (no numbers)
        if ext in {'.jpg', '.png', '.webp'}: return ["تصاویر", "سایر"], path.name
        if ext in {'.mp4', '.mkv', '.mov'}: return ["ویدئو_و_رسانه"], path.name
        if ext in {'.dwg', '.obj', '.blend'}: return ["مهندسی_و_معماری"], path.name
        if ext in {'.pdf', '.docx', '.xlsx'}: return ["اسناد_و_آموزش"], path.name
        if ext in {'.zip', '.rar', '.7z'}: return ["بایگانی_و_فشرده"], path.name
        if ext in {'.iso', '.bak'}: return ["بایگانی_و_فشرده", "ایمیج_و_بک‌آپ"], path.name

        return ["سایر_موارد"], path.name

    def run(self):
        try:
            self.log.emit("در حال جستجوی فایل‌ها...")
            files = [p for p in self.source_dir.rglob("*") if p.is_file()]
            total = len(files)
            self.log.emit(f"تعداد {total} فایل پیدا شد.")
            
            if total == 0:
                self.progress.emit(100)
                return

            for i, path in enumerate(files):
                if self._stop.is_set():
                    self.log.emit("عملیات متوقف شد.")
                    break
                
                try:
                    parts, new_name = self._get_target_info(path)
                    target = self.dest_dir.joinpath(*parts)
                    target.mkdir(parents=True, exist_ok=True)
                    
                    dest = target / new_name
                    if dest.exists():
                        dest = target / f"{path.stem}_{int(datetime.now().timestamp())}{path.suffix}"
                    
                    shutil.copy2(path, dest)
                    if self.move_mode:
                        try: os.remove(path)
                        except: pass
                    
                    self.log.emit(f"انجام شد: {new_name}")
                except Exception as inner_e:
                    self.log.emit(f"خطا در فایل {path.name}: {str(inner_e)}")
                
                self.progress.emit(int((i+1)*100/total))
            
        except Exception as e:
            self.log.emit(f"خطای بحرانی: {str(e)}")
        finally:
            self.finished.emit()

    def stop(self): self._stop.set()
