import os
import shutil
import threading
import time
from datetime import datetime
from pathlib import Path
from PySide6.QtCore import QObject, Signal

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

    def run(self):
        try:
            self.log.emit("در حال ارزیابی درایو و فایل‌ها...")
            files = [p for p in self.source_dir.rglob("*") if p.is_file()]
            total = len(files)
            
            if total == 0:
                self.progress.emit(100)
                return

            for i, path in enumerate(files):
                if self._stop.is_set():
                    self.log.emit("توقف امن انجام شد. فایل‌ها در امان هستند.")
                    break
                
                try:
                    # Logic remains but with extra safety
                    ext = path.suffix.lower()
                    target_folder = self.dest_dir / "بایگانی_شده" / ext.replace(".", "")
                    target_folder.mkdir(parents=True, exist_ok=True)
                    
                    dest = target_folder / path.name
                    # Prevent overwriting
                    if dest.exists():
                        dest = target_folder / f"{path.stem}_{int(time.time())}{path.suffix}"
                    
                    shutil.copy2(path, dest)
                    self.log.emit(f"کپی شد: {path.name}")
                    
                except Exception as e:
                    self.log.emit(f"خطا در فایل {path.name}: {str(e)}")
                
                self.progress.emit(int((i+1)*100/total))
            
        except Exception as e:
            self.log.emit(f"خطای سیستمی: {str(e)}")
        finally:
            self.finished.emit()

    def stop(self):
        self._stop.set()
