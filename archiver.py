import os
import shutil
import threading
import time
from datetime import datetime
from pathlib import Path
from PySide6.QtCore import QObject, Signal
from audio_analyzer import AudioAnalyzer

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

    def _get_target_info(self, path):
        ext = path.suffix.lower()
        name = path.stem.lower()
        
        # PRIORITY 1: Strictly by Extension (Graphics)
        if ext == ".psd": return ["تصاویر", "لایه_باز", "Photoshop"], path.name
        if ext == ".cdr": return ["گرافیک_وکتور", "CorelDRAW"], path.name
        if ext in {'.ai', '.eps', '.svg'}: return ["گرافیک_وکتور", "Vector_Assets"], path.name

        # PRIORITY 2: Audio Intelligence (Music Artist > Album)
        if ext in {'.mp3', '.wav', '.flac', '.m4a'}:
            hint = AudioAnalyzer.analyze(path)
            parts = AudioAnalyzer.folder_parts(hint)
            if parts and parts[0] == "موسیقی": parts[0] = "موسیقی_و_صوت"
            new_name = AudioAnalyzer.destination_filename(path, hint)
            return parts, new_name

        # PRIORITY 3: Supreme Taxonomy (Keywords for interior/architecture)
        # Apply this only to images or 3D files
        if ext in {'.jpg', '.jpeg', '.png', '.webp', '.dwg', '.obj', '.max', '.blend'}:
            if any(x in name for x in ["plaster", "گچبری", "molding", "ستون"]): 
                p = ["معماری", "عناصر_ساختمانی"]
                return (["تصاویر"] + p) if ext in {'.jpg', '.png'} else (["مهندسی_و_معماری"] + p), path.name
            if any(x in name for x in ["curtain", "پرده", "chandelier", "لوستر", "lamp", "لامپ", "آباژور"]):
                p = ["معماری", "تجهیزات_داخلی"]
                return (["تصاویر"] + p) if ext in {'.jpg', '.png'} else (["مهندسی_و_معماری"] + p), path.name
            if any(x in name for x in ["ac", "cooler", "کولر", "heater", "بخاری"]):
                p = ["معماری", "تجهیزات_داخلی", "تأسیسات"]
                return (["تصاویر"] + p) if ext in {'.jpg', '.png'} else (["مهندسی_و_معماری"] + p), path.name

        # PRIORITY 4: General Fallback
        if ext in {'.jpg', '.png', '.webp'}: return ["تصاویر", "سایر_عکس‌ها"], path.name
        if ext in {'.mp4', '.mkv', '.mov'}: return ["ویدئو_و_رسانه"], path.name
        if ext in {'.dwg', '.obj', '.blend', '.fbx'}: return ["مهندسی_و_معماری"], path.name
        if ext in {'.pdf', '.docx', '.xlsx', '.txt'}: return ["اسناد_و_آموزش"], path.name
        if ext in {'.zip', '.rar', '.7z'}: return ["بایگانی_و_فشرده"], path.name
        if ext in {'.iso', '.bak', '.cdi'}: return ["بایگانی_و_فشرده", "ایمیج_و_بک‌آپ"], path.name

        return ["سایر_موارد"], path.name

    def run(self):
        try:
            self.log.emit("اسکن اولیه فایل‌ها...")
            files = [p for p in self.source_dir.rglob("*") if p.is_file()]
            total = len(files)
            if total == 0: 
                self.log.emit("فایلی یافت نشد.")
                self.progress.emit(100)
                return

            for i, path in enumerate(files):
                if self._stop.is_set(): break
                try:
                    parts, new_name = self._get_target_info(path)
                    target = self.dest_dir.joinpath(*parts)
                    target.mkdir(parents=True, exist_ok=True)
                    
                    dest = target / new_name
                    if dest.exists():
                        dest = target / f"{Path(new_name).stem}_{int(time.time())}{Path(new_name).suffix}"
                    
                    shutil.copy2(path, dest)
                    if self.move_mode:
                        try: os.remove(path)
                        except: pass
                    
                    self.log.emit(f"موفق: {new_name}")
                except Exception as inner_e:
                    self.log.emit(f"خطا در فایل {path.name}: {str(inner_e)}")
                
                self.progress.emit(int((i+1)*100/total))
            
            self.log.emit("--- عملیات با موفقیت پایان یافت ---")
        except Exception as e:
            self.log.emit(f"خطای بحرانی سیستم: {str(e)}")
        finally:
            self.finished.emit()

    def stop(self): self._stop.set()
