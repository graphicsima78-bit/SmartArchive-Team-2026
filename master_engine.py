import os
import shutil
import threading
import time
from pathlib import Path
from PySide6.QtCore import QObject, Signal
from audio_analyzer import AudioAnalyzer

class MasterWorker(QObject):
    progress = Signal(int)
    log = Signal(str)
    finished = Signal()

    def __init__(self, source, dest, mode="media", **kwargs):
        super().__init__()
        self.source = Path(source); self.dest = Path(dest)
        self.mode = mode
        self.audio_pref = kwargs.get('pref', 'persian')
        self.move_mode = bool(kwargs.get('move_mode', False))
        self._stop = threading.Event()

    def _normalize(self, n):
        return n.lower().replace(" ", "").replace("_", "").replace("-", "").replace("ي", "ی").replace("ك", "ک")

    def _sync_folder(self, parent, target, is_artist=False):
        if not parent.exists(): return target
        t_norm = self._normalize(target)
        variants = AudioAnalyzer.get_all_variants(target) if is_artist else [target]
        v_norms = [self._normalize(v) for v in variants]
        
        try:
            for entry in os.scandir(parent):
                if entry.is_dir():
                    curr_norm = self._normalize(entry.name)
                    if curr_norm in v_norms or curr_norm == t_norm:
                        if is_artist and entry.name != target and any('\u0600' <= c <= '\u06FF' for c in target):
                            try:
                                os.rename(entry.path, parent / target)
                                self.log.emit(f"Syncing folder name: {target}")
                                return target
                            except: return entry.name
                        return entry.name
        except: pass
        return target

    def run(self):
        try:
            files = [p for p in self.source.rglob("*") if p.is_file()]
            total = len(files)
            if total == 0: self.progress.emit(100); return
            for i, path in enumerate(files):
                if self._stop.is_set(): break
                ext = path.suffix.lower(); name = path.stem.lower()
                
                if self.mode == "media" and ext in {'.mp3', '.wav', '.flac'}:
                    meta = AudioAnalyzer.analyze(path)
                    pref_a = AudioAnalyzer.get_preferred_name(meta["artist"], self.audio_pref) or "سایر_آهنگ‌ها"
                    parts = ["موسیقی_و_صوت", pref_a]
                    if meta["album"]: parts.append(meta["album"])
                    new_name = AudioAnalyzer.destination_filename(path, meta)
                else:
                    if ext == ".psd": parts = ["تصاویر", "لایه_باز", "Photoshop"]
                    elif ext == ".cdr": parts = ["گرافیک_وکتور", "CorelDRAW"]
                    elif ext in {'.ai', '.eps'}: parts = ["گرافیک_وکتور", "Vector_Assets"]
                    elif ext in {'.jpg', '.png'}: parts = ["تصاویر", "سایر"]
                    else: parts = ["بایگانی_نشده"]
                    new_name = path.name

                curr = self.dest
                for j, p in enumerate(parts):
                    folder = self._sync_folder(curr, p, is_artist=(j==1 and parts[0]=="موسیقی_و_صوت"))
                    curr = curr / folder
                
                curr.mkdir(parents=True, exist_ok=True)
                dest_file = curr / new_name
                if dest_file.exists(): dest_file = curr / f"{Path(new_name).stem}_کپی{Path(new_name).suffix}"
                
                try:
                    shutil.copy2(path, dest_file)
                    if self.move_mode: os.remove(path)
                    self.log.emit(f"بایگانی شد: {new_name}")
                except Exception as e: self.log.emit(f"Error: {e}")
                self.progress.emit(int((i+1)*100/max(total, 1)))
        finally: self.finished.emit()

    def stop(self): self._stop.set()
