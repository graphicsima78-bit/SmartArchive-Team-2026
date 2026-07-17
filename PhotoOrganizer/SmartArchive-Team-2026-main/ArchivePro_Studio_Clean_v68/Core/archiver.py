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

    def _sync_folder(self, parent, target, is_artist=False):
        """Smart Merge: Syncs folders even across different languages (En/Fa)"""
        if not parent.exists(): return target
        t_norm = self._normalize(target)
        variants = AudioAnalyzer.get_all_variants(target) if is_artist else [target]
        v_norms = [self._normalize(v) for v in variants]
        
        try:
            for entry in os.scandir(parent):
                if entry.is_dir():
                    curr_norm = self._normalize(entry.name)
                    if curr_norm in v_norms or curr_norm == t_norm:
                        # RENAME if user wants Persian but folder is English
                        if is_artist and entry.name != target and any('\u0600' <= c <= '\u06FF' for c in target):
                            try:
                                os.rename(entry.path, parent / target)
                                return target
                            except: return entry.name
                        return entry.name
        except: pass
        return target

    def _get_path_info(self, path):
        ext = path.suffix.lower(); name = path.stem.lower()
        
        # 1. AUDIO (Meta-first, clean names)
        if ext in {'.mp3', '.wav', '.flac'}:
            meta = AudioAnalyzer.analyze(path)
            pref_a = AudioAnalyzer.get_persian_artist(meta["artist"]) or "سایر_آهنگ‌ها"
            p = ["موسیقی_و_صوت", pref_a]
            if meta["album"]: p.append(meta["album"])
            elif meta["year"]: p.append(meta["year"])
            return p, AudioAnalyzer.destination_filename(path, meta)

        # 2. GRAPHICS (Strict priority)
        if ext == ".psd": return ["تصاویر", "لایه_باز", "Photoshop"], path.name
        if ext == ".cdr": return ["گرافیک_وکتور", "CorelDRAW"], path.name
        if ext in {'.ai', '.eps', '.svg'}: return ["گرافیک_وکتور", "Vector_Assets"], path.name

        # 3. INTERIOR & ARCHITECTURE
        if any(x in name for x in ["plaster", "گچبری", "molding"]): return ["معماری", "گچبری"], path.name
        if any(x in name for x in ["curtain", "پرده", "chandelier", "لوستر"]): return ["معماری", "تجهیزات"], path.name

        # Default fallbacks
        if ext in {'.jpg', '.png', '.webp'}: return ["تصاویر", "سایر"], path.name
        if ext in {'.pdf', '.docx'}: return ["اسناد"], path.name
        return ["بایگانی_نشده"], path.name

    def run(self):
        try:
            files = [p for p in self.source_dir.rglob("*") if p.is_file()]
            total = len(files)
            if total == 0: self.progress.emit(100); return
            for i, path in enumerate(files):
                if self._stop.is_set(): break
                try:
                    parts, new_name = self._get_path_info(path)
                    curr = self.dest
                    for j, p in enumerate(parts):
                        is_art = (j == 1 and parts[0] == "موسیقی_و_صوت")
                        folder = self._sync_folder(curr, p, is_artist=is_art)
                        curr = curr / folder
                    curr.mkdir(parents=True, exist_ok=True)
                    dest = curr / new_name
                    if dest.exists(): dest = curr / f"{Path(new_name).stem}_کپی{Path(new_name).suffix}"
                    shutil.copy2(path, dest)
                    if self.move_mode: os.remove(path)
                    self.log.emit(f"OK: {new_name}")
                except Exception as e: self.log.emit(f"Error: {e}")
                self.progress.emit(int((i+1)*100/total))
        finally: self.finished.emit()

    def stop(self): self._stop.set()
