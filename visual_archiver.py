import os
import shutil
import threading
from pathlib import Path
from PySide6.QtCore import QObject, Signal

class VisualWorker(QObject):
    progress = Signal(int)
    log = Signal(str)
    finished = Signal()

    def __init__(self, source, dest, move_mode=False):
        super().__init__()
        self.source = Path(source)
        self.dest = Path(dest)
        self.move_mode = move_mode
        self._stop = threading.Event()

    def _get_taxonomy(self, name):
        name = name.lower()
        if any(x in name for x in ["plaster", "گچبری", "ستون"]): return ["معماری", "گچبری"]
        if any(x in name for x in ["curtain", "پرده", "chandelier", "لوستر", "lamp", "لامپ"]): return ["معماری", "تجهیزات_داخلی"]
        if any(x in name for x in ["table", "میز", "chair", "صندلی", "mobl", "مبل"]): return ["مبلمان"]
        if any(x in name for x in ["gold", "طلا", "copper", "مس", "silver", "نقره"]): return ["متریال", "فلزات"]
        return None

    def _get_vector_type(self, name):
        if any(x in name for x in ["icon", "آیکون", "symbol"]): return "آیکون_و_نماد"
        if any(x in name for x in ["pattern", "پترن", "seamless", "اسلیمی"]): return "پترن_و_بافت"
        if any(x in name for x in ["logo", "لوگو"]): return "لوگو_و_برندینگ"
        return "سایر_وکتورها"

    def run(self):
        files = [p for p in self.source.rglob("*") if p.is_file()]
        total = len(files)
        for i, path in enumerate(files):
            if self._stop.is_set(): break
            ext = path.suffix.lower()
            name = path.stem.lower()

            if ext in {'.psd', '.cdr', '.ai', '.eps', '.svg', '.jpg', '.png', '.webp'}:
                # Logic for Design
                if ext == ".psd": parts = ["تصاویر", "لایه_باز", "Photoshop"]
                elif ext == ".cdr": parts = ["گرافیک_وکتور", "CorelDRAW"]
                elif ext in {'.ai', '.eps', '.svg'}: parts = ["گرافیک_وکتور", self._get_vector_type(name)]
                else:
                    tax = self._get_taxonomy(name)
                    parts = ["تصاویر"] + (tax if tax else ["سایر_عکس‌ها"])
                
                target_dir = self.dest.joinpath(*parts)
                target_dir.mkdir(parents=True, exist_ok=True)
                dest = target_dir / path.name
                if dest.exists(): dest = target_dir / f"{path.stem}_کپی{ext}"
                
                try:
                    shutil.copy2(path, dest)
                    if self.move_mode: os.remove(path)
                    self.log.emit(f"بایگانی شد: {path.name}")
                except: pass
            
            self.progress.emit(int((i+1)*100/max(total, 1)))
        self.finished.emit()

    def stop(self): self._stop.set()
