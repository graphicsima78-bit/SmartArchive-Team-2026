import os
import shutil
import threading
import time
import re
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

    def _normalize_name(self, name):
        """نرمال‌سازی نام برای مقایسه دقیق‌تر پوشه‌ها"""
        name = name.lower().replace(" ", "").replace("_", "").replace("-", "")
        # تبدیل حروف عربی به فارسی برای تطبیق بهتر
        name = name.replace("ي", "ی").replace("ك", "ک")
        return name

    def _find_existing_folder(self, parent_path, target_name):
        """جستجو برای یافتن پوشه‌ای که از قبل وجود دارد و مشابه هدف ماست"""
        if not parent_path.exists():
            return None
        
        target_norm = self._normalize_name(target_name)
        
        try:
            for entry in os.scandir(parent_path):
                if entry.is_dir():
                    if self._normalize_name(entry.name) == target_norm:
                        return entry.name
        except:
            pass
        return None

    def _resolve_smart_path(self, parts):
        """ساخت مسیر نهایی با اولویت استفاده از پوشه‌های موجود"""
        current_path = self.dest_dir
        resolved_parts = []
        
        for part in parts:
            existing_name = self._find_existing_folder(current_path, part)
            if existing_name:
                current_path = current_path / existing_name
                resolved_parts.append(existing_name)
            else:
                current_path = current_path / part
                resolved_parts.append(part)
        
        return current_path

    def _get_target_info(self, path):
        ext = path.suffix.lower()
        name = path.stem.lower()
        
        # Priority 1: Graphics
        if ext == ".psd": return ["تصاویر", "لایه_باز", "Photoshop"], path.name
        if ext == ".cdr": return ["گرافیک_وکتور", "CorelDRAW"], path.name
        if ext in {'.ai', '.eps', '.svg'}: return ["گرافیک_وکتور", "Vector_Assets"], path.name

        # Priority 2: Audio (Finglish to Persian Singer Map is in audio_analyzer)
        if ext in {'.mp3', '.wav', '.flac', '.m4a'}:
            hint = AudioAnalyzer.analyze(path)
            parts = AudioAnalyzer.folder_parts(hint)
            if parts and parts[0] == "موسیقی": parts[0] = "موسیقی_و_صوت"
            new_name = AudioAnalyzer.destination_filename(path, hint)
            return parts, new_name

        # Priority 3: Architecture / Interior
        if ext in {'.jpg', '.png', '.webp', '.dwg', '.obj'}:
            if any(x in name for x in ["plaster", "گچبری", "molding", "ستون"]): 
                p = ["معماری", "عناصر_ساختمانی"]
                return (["تصاویر"] + p) if ext in {'.jpg', '.png'} else (["مهندسی_و_معماری"] + p), path.name
            if any(x in name for x in ["curtain", "پرده", "chandelier", "لوستر", "lamp", "لامپ"]):
                p = ["معماری", "تجهیزات_داخلی"]
                return (["تصاویر"] + p) if ext in {'.jpg', '.png'} else (["مهندسی_و_معماری"] + p), path.name

        # Fallback
        if ext in {'.jpg', '.png'}: return ["تصاویر", "سایر_عکس‌ها"], path.name
        if ext in {'.mp4', '.mkv', '.mov'}: return ["ویدئو_و_رسانه"], path.name
        if ext in {'.dwg', '.obj', '.blend'}: return ["مهندسی_و_معماری"], path.name
        if ext in {'.zip', '.rar', '.7z'}: return ["بایگانی_و_فشرده"], path.name

        return ["سایر_موارد"], path.name

    def run(self):
        try:
            files = [p for p in self.source_dir.rglob("*") if p.is_file()]
            total = len(files)
            if total == 0: 
                self.progress.emit(100)
                return

            for i, path in enumerate(files):
                if self._stop.is_set(): break
                try:
                    parts, new_name = self._get_target_info(path)
                    
                    # USE SMART MERGE LOGIC
                    final_dir = self._resolve_smart_path(parts)
                    final_dir.mkdir(parents=True, exist_ok=True)
                    
                    dest = final_dir / new_name
                    if dest.exists():
                        dest = final_dir / f"{Path(new_name).stem}_کپی{Path(new_name).suffix}"
                    
                    shutil.copy2(path, dest)
                    if self.move_mode:
                        try: os.remove(path)
                        except: pass
                    
                    self.log.emit(f"بایگانی در {final_dir.name}: {new_name}")
                except Exception as inner_e:
                    self.log.emit(f"خطا: {inner_e}")
                
                self.progress.emit(int((i+1)*100/total))
            
        except Exception as e:
            self.log.emit(f"خطای بحرانی: {e}")
        finally:
            self.finished.emit()

    def stop(self): self._stop.set()
