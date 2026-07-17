import os, shutil, threading
from pathlib import Path
from PySide6.QtCore import QObject, Signal
class ProjectWorker(QObject):
    progress = Signal(int); log = Signal(str); finished = Signal()
    def __init__(self, source, dest, name):
        super().__init__(); self.source = Path(source); self.dest = Path(dest) / name; self._stop = threading.Event()
    def run(self):
        files = [p for p in self.source.rglob("*") if p.is_file()]
        total = len(files)
        for i, path in enumerate(files):
            if self._stop.is_set(): break
            ext = path.suffix.lower()
            target_dir = self.dest / ext.replace(".","")
            target_dir.mkdir(parents=True, exist_ok=True)
            try: shutil.copy2(path, target_dir / path.name); self.log.emit(f"بایگانی پروژه: {path.name}")
            except: pass
            self.progress.emit(int((i+1)*100/max(total,1)))
        self.finished.emit()
    def stop(self): self._stop.set()
