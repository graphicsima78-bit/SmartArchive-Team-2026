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
        self._stop = threading.Event()

    def _find_existing_folder(self, parent, target):
        if not parent.exists(): return None
        tn = target.lower().replace(" ", "")
        for entry in os.scandir(parent):
            if entry.is_dir() and entry.name.lower().replace(" ", "") == tn:
                return entry.name
        return None

    def _resolve_path(self, parts):
        curr = self.dest_dir
        res = []
        for p in parts:
            exist = self._find_existing_folder(curr, p)
            name = exist if exist else p
            curr = curr / name
            res.append(name)
        return curr

    def run(self):
        files = [p for p in self.source_dir.rglob("*") if p.is_file()]
        total = len(files)
        for i, path in enumerate(files):
            if self._stop.is_set(): break
            ext = path.suffix.lower()
            
            # Media Logic
            if ext in {'.mp3', '.wav', '.flac'}:
                meta = AudioAnalyzer.analyze(path)
                parts = AudioAnalyzer.folder_parts(meta, self.audio_pref)
                name = AudioAnalyzer.destination_filename(path, meta, self.audio_pref)
            else:
                # Basic Categorization for others
                if ext in {'.psd', '.cdr', '.ai'}: parts = ["گرافیک"]
                elif ext in {'.jpg', '.png'}: parts = ["تصاویر"]
                else: parts = ["سایر"]
                name = path.name

            target = self._resolve_path(parts)
            target.mkdir(parents=True, exist_ok=True)
            dest = target / name
            
            try:
                shutil.copy2(path, dest)
                self.log.emit(f"OK: {name}")
            except Exception as e: self.log.emit(f"Error: {e}")
            
            self.progress.emit(int((i+1)*100/max(total, 1)))
        self.finished.emit()

    def stop(self): self._stop.set()
