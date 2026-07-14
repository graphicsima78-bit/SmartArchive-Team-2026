import os
import shutil
import threading
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

    def _get_supreme_taxonomy(self, name):
        name = name.lower()
        if any(x in name for x in ["plaster", "گچبری", "molding", "ستون"]): return ["معماری", "عناصر_ساختمانی"]
        if any(x in name for x in ["curtain", "پرده", "chandelier", "لوستر", "lamp", "لامپ", "آباژور"]): return ["معماری", "تجهیزات_داخلی", "روشنایی"]
        if any(x in name for x in ["ac", "cooler", "کولر", "heater", "بخاری"]): return ["معماری", "تجهیزات_داخلی", "تأسیسات"]
        if any(x in name for x in ["table", "میز", "chair", "صندلی", "sofa", "مبل", "bed", "تخت"]): return ["مبلمان"]
        if any(x in name for x in ["monitor", "مانیتور", "pc", "computer", "keyboard", "mouse"]): return ["تکنولوژی", "سخت‌افزار"]
        if any(x in name for x in ["gold", "طلا", "copper", "مس", "brass", "برنج", "iron", "آهن"]): return ["متریال_خام", "فلزات"]
        if any(x in name for x in ["fabric", "پارچه", "textile", "leather", "چرم"]): return ["متریال_خام", "منسوجات"]
        if any(x in name for x in ["cigar", "سیگار", "tissue", "دستمال", "cup", "لیوان"]): return ["سبک_زندگی"]
        if any(x in name for x in ["flag", "پرچم", "money", "پول", "map", "نقشه"]): return ["نمادها_و_جغرافیا"]
        return None

    def _get_target_info(self, path):
        ext = path.suffix.lower()
        name = path.stem.lower()
        
        if ext == ".psd": return ["تصاویر", "لایه_باز", "Photoshop"], path.name
        if ext == ".cdr": return ["گرافیک_وکتور", "CorelDRAW"], path.name
        if ext in {'.ai', '.eps', '.svg'}: return ["گرافیک_وکتور", "Vector_Assets"], path.name

        if ext in {'.mp3', '.wav', '.flac', '.m4a'}:
            hint = AudioAnalyzer.analyze(path)
            return AudioAnalyzer.folder_parts(hint), AudioAnalyzer.destination_filename(path, hint)

        supreme = self._get_supreme_taxonomy(name)
        if ext in {'.jpg', '.png', '.webp', '.tiff'}:
            if supreme: return ["تصاویر"] + supreme, path.name
            return ["تصاویر", "سایر_عکس‌ها"], path.name

        if ext in {'.dwg', '.obj', '.blend'}: return ["مهندسی_و_معماری"], path.name
        if ext in {'.zip', '.rar', '.7z'}: return ["بایگانی_و_فشرده"], path.name
        if ext in {'.iso', '.bak', '.cdi'}: return ["بایگانی_و_فشرده", "ایمیج_و_بک‌آپ"], path.name

        return ["سایر_موارد"], path.name

    def run(self):
        try:
            files = [p for p in self.source_dir.rglob("*") if p.is_file()]
            total = len(files)
            if total == 0: self.progress.emit(100); return
            
            for i, path in enumerate(files):
                if self._stop.is_set(): break
                try:
                    parts, new_name = self._get_target_info(path)
                    target = self.dest_dir.joinpath(*parts)
                    target.mkdir(parents=True, exist_ok=True)
                    dest = target / new_name
                    if dest.exists():
                        dest = target / f"{Path(new_name).stem}_{int(datetime.now().timestamp())}{Path(new_name).suffix}"
                    shutil.copy2(path, dest)
                    if self.move_mode: os.remove(path)
                    self.log.emit(f"OK: {new_name}")
                except Exception as e: self.log.emit(f"ERR: {path.name} | {e}")
                self.progress.emit(int((i+1)*100/total))
        finally: self.finished.emit()

    def stop(self): self._stop.set()
