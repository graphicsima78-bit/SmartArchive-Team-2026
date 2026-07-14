import os
import shutil
import threading
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
        self.audio_pref = kwargs.get('audio_pref', 'persian')
        self.move_mode = bool(kwargs.get('delete_after_copy', False))
        self._stop = threading.Event()

    def _normalize(self, n):
        return n.lower().replace(" ", "").replace("_", "").replace("-", "").replace("ي", "ی").replace("ك", "ک")

    def _find_smart_folder(self, parent, target):
        """هوشمندترین متد برای پیدا کردن پوشه‌های از قبل موجود"""
        if not parent.exists(): return None
        target_norm = self._normalize(target)
        try:
            entries = list(os.scandir(parent))
            # 1. چک کردن شباهت اسمی مستقیم
            for entry in entries:
                if entry.is_dir() and self._normalize(entry.name) == target_norm:
                    return entry.name
            
            # 2. چک کردن نام‌های جایگزین (خواننده‌ها)
            variants = AudioAnalyzer.get_all_names_for(target)
            if variants:
                var_norms = [self._normalize(v) for v in variants]
                for entry in entries:
                    if entry.is_dir() and self._normalize(entry.name) in var_norms:
                        return entry.name
        except: pass
        return None

    def _get_path(self, parts):
        curr = self.dest_dir
        for p in parts:
            existing = self._find_smart_folder(curr, p)
            name = existing if existing else p
            curr = curr / name
        return curr

    def _get_info(self, path):
        ext = path.suffix.lower()
        name = path.stem.lower()
        
        # Priority: Graphics
        if ext == ".psd": return ["تصاویر", "لایه_باز", "Photoshop"], path.name
        if ext == ".cdr": return ["گرافیک_وکتور", "CorelDRAW"], path.name
        
        # Priority: Audio
        if ext in {'.mp3', '.wav', '.flac', '.m4a'}:
            meta = AudioAnalyzer.analyze(path)
            parts = AudioAnalyzer.folder_parts(meta, self.audio_pref)
            # Normalize root folder name
            if parts[0] == "موسیقی": parts[0] = "موسیقی_و_صوت"
            new_name = AudioAnalyzer.destination_filename(path, meta, self.audio_pref)
            return parts, new_name

        # Priority: Architecture
        if ext in {'.jpg', '.png', '.dwg', '.obj'}:
            if any(x in name for x in ["plaster", "گچبری", "molding", "ستون"]): return ["معماری", "ساختمانی"], path.name
            if any(x in name for x in ["curtain", "پرده", "chandelier", "لوستر", "lamp"]): return ["معماری", "تجهیزات"], path.name

        if ext in {'.jpg', '.png'}: return ["تصاویر", "سایر"], path.name
        if ext in {'.zip', '.rar', '.7z'}: return ["بایگانی_و_فشرده"], path.name
        return ["سایر_موارد"], path.name

    def run(self):
        try:
            files = [p for p in self.source_dir.rglob("*") if p.is_file()]
            total = len(files)
            if total == 0: self.progress.emit(100); return
            
            for i, path in enumerate(files):
                if self._stop.is_set(): break
                try:
                    parts, new_name = self._get_info(path)
                    target_dir = self._get_path(parts)
                    target_dir.mkdir(parents=True, exist_ok=True)
                    
                    dest = target_dir / new_name
                    if dest.exists():
                        dest = target_dir / f"{Path(new_name).stem}_کپی{Path(new_name).suffix}"
                    
                    shutil.copy2(path, dest)
                    if self.move_mode: os.remove(path)
                    self.log.emit(f"بایگانی در {target_dir.name}: {new_name}")
                except Exception as e: self.log.emit(f"خطا: {e}")
                self.progress.emit(int((i+1)*100/total))
        finally: self.finished.emit()

    def stop(self): self._stop.set()
