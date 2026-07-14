import os
import shutil
import threading
import re
from pathlib import Path
from PySide6.QtCore import QObject, Signal
from audio_analyzer import AudioAnalyzer

class ArchiveWorker(QObject):
    progress = Signal(int)
    log = Signal(str)
    finished = Signal()

    def __init__(self, source, dest, **kwargs):
        super().__init__()
        self.source = Path(source)
        self.dest = Path(dest)
        self.audio_pref = kwargs.get('audio_pref', 'persian')
        self.move_mode = bool(kwargs.get('delete_after_copy', False))
        self.project_config = kwargs.get('project_config')
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
                        # Migration logic: if pref is Persian but folder is English, Rename.
                        if self.audio_pref == "persian" and is_artist and entry.name != target:
                            try:
                                os.rename(entry.path, parent / target)
                                return target
                            except: pass
                        return entry.name
        except: pass
        return target

    def _get_taxonomy(self, name):
        name = name.lower()
        if any(x in name for x in ["plaster", "گچبری", "molding", "ستون"]): return ["معماری", "عناصر_ساختمانی"]
        if any(x in name for x in ["curtain", "پرده", "chandelier", "لوستر", "lamp", "لامپ"]): return ["معماری", "تجهیزات_داخلی"]
        if any(x in name for x in ["table", "میز", "chair", "صندلی", "mobl", "مبل", "bed", "تخت"]): return ["مبلمان"]
        if any(x in name for x in ["monitor", "pc", "keyboard", "mouse", "مانیتور", "کامپیوتر"]): return ["تکنولوژی", "سخت‌افزار"]
        if any(x in name for x in ["gold", "طلا", "copper", "مس", "brass", "برنج", "iron", "آهن"]): return ["متریال_خام", "فلزات"]
        if any(x in name for x in ["fabric", "پارچه", "textile", "leather", "چرم"]): return ["متریال_خام", "منسوجات"]
        if any(x in name for x in ["cigar", "سیگار", "tissue", "دستمال", "cup", "لیوان"]): return ["اکسسوری_و_سبک_زندگی"]
        return None

    def _get_info(self, path):
        ext = path.suffix.lower()
        name = path.stem.lower()
        
        if self.project_config:
            return ["پروژه‌ها", self.project_config.get('name', 'پروژه_بدون_نام')], path.name

        # Priority 1: Graphics
        if ext == ".psd": return ["تصاویر", "لایه_باز", "Photoshop"], path.name
        if ext == ".cdr": return ["گرافیک_وکتور", "CorelDRAW"], path.name
        if ext in {'.ai', '.eps', '.svg'}: return ["گرافیک_وکتور", "Vector_Assets"], path.name

        # Priority 2: Audio
        if ext in {'.mp3', '.wav', '.flac', '.m4a'}:
            meta = AudioAnalyzer.analyze(path)
            artist = AudioAnalyzer.get_preferred_name(meta["artist"], self.audio_pref) or "سایر_آهنگ‌ها"
            p = ["موسیقی_و_صوت", artist]
            if meta["album"]: p.append(meta["album"])
            elif meta["year"]: p.append(meta["year"])
            return p, AudioAnalyzer.destination_filename(path, meta, self.audio_pref)

        # Priority 3: Taxonomy
        tax = self._get_taxonomy(name)
        if tax:
            root = "تصاویر" if ext in {'.jpg', '.png'} else "مهندسی_و_معماری"
            return [root] + tax, path.name

        # Fallbacks
        if ext in {'.jpg', '.png', '.webp'}: return ["تصاویر", "سایر_عکس‌ها"], path.name
        if ext in {'.pdf', '.docx', '.epub'}: return ["اسناد_و_آموزش"], path.name
        if ext in {'.zip', '.rar', '.7z'}: return ["بایگانی_و_فشرده"], path.name
        
        return ["سایر_موارد"], path.name

    def run(self):
        try:
            files = [p for p in self.source.rglob("*") if p.is_file()]
            total = len(files)
            if total == 0: self.progress.emit(100); return
            for i, path in enumerate(files):
                if self._stop.is_set(): break
                try:
                    parts, new_name = self._get_info(path)
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
                    self.log.emit(f"بایگانی شد: {new_name}")
                except Exception as e: self.log.emit(f"خطا در {path.name}: {e}")
                self.progress.emit(int((i+1)*100/total))
        finally: self.finished.emit()

    def stop(self): self._stop.set()
