import os
import shutil
import threading
from pathlib import Path
from PySide6.QtCore import QObject, Signal
from audio_analyzer import AudioAnalyzer

class MediaWorker(QObject):
    progress = Signal(int)
    log = Signal(str)
    finished = Signal()

    def __init__(self, source, dest, pref="persian", move_mode=False):
        super().__init__()
        self.source = Path(source); self.dest = Path(dest)
        self.pref = pref; self.move_mode = move_mode
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
                    if curr_norm == t_norm or curr_norm in v_norms:
                        # Migration: تغییر نام پوشه موجود به زبان دلخواه
                        if is_artist and entry.name != target and self.pref == "persian":
                            try: os.rename(entry.path, parent / target); return target
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
                ext = path.suffix.lower()
                if ext in {'.mp3', '.wav', '.flac', '.m4a'}:
                    meta = AudioAnalyzer.analyze(path)
                    if meta.get("kind") == "ambient":
                        target_dir = self.dest / "صدای_محیط" / meta["subtype"]
                        new_name = path.name
                    else:
                        pref_a = AudioAnalyzer.get_preferred_name(meta["artist"], self.pref) or "سایر_آهنگ‌ها"
                        root = self.dest / "موسیقی_و_صوت"
                        root.mkdir(parents=True, exist_ok=True)
                        artist_folder = self._sync_folder(root, pref_a, is_artist=True)
                        target_dir = root / artist_folder
                        sub = meta["album"] or meta["year"]
                        if sub: target_dir = target_dir / self._sync_folder(target_dir, sub)
                        new_name = AudioAnalyzer.destination_filename(path, meta, self.pref)
                elif ext in {'.mp4', '.mkv', '.mov'}:
                    target_dir = self.dest / "ویدئو_و_رسانه"; new_name = path.name
                else:
                    target_dir = self.dest / "بایگانی_نشده"; new_name = path.name

                target_dir.mkdir(parents=True, exist_ok=True)
                dest = target_dir / new_name
                if dest.exists(): dest = target_dir / f"{Path(new_name).stem}_کپی{ext}"
                shutil.copy2(path, dest)
                if self.move_mode: os.remove(path)
                self.log.emit(f"بایگانی: {new_name}")
                self.progress.emit(int((i+1)*100/total))
        finally: self.finished.emit()

    def stop(self): self._stop.set()
