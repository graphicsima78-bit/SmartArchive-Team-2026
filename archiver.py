import os
import shutil
import threading
import time
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
        self.use_ai = bool(kwargs.get('use_ai', True))
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
                        if self.audio_pref == "persian" and is_artist and entry.name != target:
                            try:
                                os.rename(entry.path, parent / target)
                                return target
                            except: pass
                        return entry.name
        except: pass
        return target

    def _get_vector_type(self, name):
        """تشخیص نوع وکتور برای طراحان"""
        if any(x in name for x in ["icon", "آیکون", "pictogram", "symbol"]): return "آیکون_و_نماد"
        if any(x in name for x in ["pattern", "پترن", "seamless", "tile", "اسلیمی"]): return "پترن_و_بافت"
        if any(x in name for x in ["logo", "لوگو", "branding"]): return "لوگو_و_برندینگ"
        if any(x in name for x in ["ornament", "تزئینی", "frame", "قاب"]): return "المان‌های_تزئینی"
        if any(x in name for x in ["character", "کاراکتر", "person"]): return "تصویرسازی"
        return "سایر_وکتورها"

    def _get_taxonomy(self, name):
        """دیکشنری جامع اشیاء و معماری"""
        if any(x in name for x in ["plaster", "گچبری", "molding"]): return ["معماری", "گچبری"]
        if any(x in name for x in ["curtain", "پرده", "chandelier", "لوستر", "lamp", "لامپ"]): return ["معماری", "تجهیزات_داخلی"]
        if any(x in name for x in ["table", "میز", "chair", "صندلی", "mobl", "مبل"]): return ["مبلمان"]
        if any(x in name for x in ["gold", "طلا", "copper", "مس", "silver", "نقره"]): return ["متریال", "فلزات"]
        if any(x in name for x in ["monitor", "pc", "مانیتور", "computer"]): return ["تکنولوژی", "سخت‌افزار"]
        return None

    def _get_info(self, path):
        ext = path.suffix.lower()
        name = path.stem.lower()
        
        # 1. AUDIO
        if ext in {'.mp3', '.wav', '.flac', '.m4a'}:
            meta = AudioAnalyzer.analyze(path)
            artist = AudioAnalyzer.get_preferred_name(meta["artist"], self.audio_pref) or "سایر_آهنگ‌ها"
            p = ["موسیقی_و_صوت", artist]
            if meta["album"]: p.append(meta["album"])
            return p, AudioAnalyzer.destination_filename(path, meta, self.audio_pref)

        # 2. GRAPHICS & VECTORS
        if ext in {'.ai', '.eps', '.svg', '.cdr'}:
            v_type = self._get_vector_type(name)
            tax = self._get_taxonomy(name)
            base = ["گرافیک_وکتور"]
            if tax: base += tax
            base.append(v_type)
            return base, path.name

        if ext == ".psd":
            tax = self._get_taxonomy(name)
            base = ["تصاویر", "لایه_باز", "Photoshop"]
            if tax: base += tax
            return base, path.name

        # 3. IMAGES
        if ext in {'.jpg', '.png', '.webp', '.tiff'}:
            tax = self._get_taxonomy(name)
            if tax: return ["تصاویر"] + tax, path.name
            return ["تصاویر", "سایر_عکس‌ها"], path.name

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
                    self.log.emit(f"OK: {new_name}")
                except: pass
                self.progress.emit(int((i+1)*100/total))
        finally: self.finished.emit()

    def stop(self): self._stop.set()
