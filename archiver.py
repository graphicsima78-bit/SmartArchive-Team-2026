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

    def _normalize(self, n):
        return n.lower().replace(" ", "").replace("_", "").replace("-", "").replace("ي", "ی").replace("ك", "ک")

    def _find_and_sync_folder(self, parent, target_name, is_artist=False):
        """هوشمندترین متد برای یافتن و تبدیل پوشه به نام دلخواه کاربر"""
        if not parent.exists(): return target_name
        
        target_norm = self._normalize(target_name)
        variants = AudioAnalyzer.get_all_variants(target_name) if is_artist else [target_name]
        variant_norms = [self._normalize(v) for v in variants]

        try:
            for entry in os.scandir(parent):
                if entry.is_dir():
                    curr_norm = self._normalize(entry.name)
                    # اگر پوشه مشابهی پیدا شد
                    if curr_norm == target_norm or curr_norm in variant_norms:
                        # اگر نام فعلی با نام دلخواه کاربر فرق دارد، تغییر نام بده
                        if entry.name != target_name:
                            new_path = parent / target_name
                            try:
                                os.rename(entry.path, new_path)
                                self.log.emit(f"تبدیل پوشه: {entry.name} -> {target_name}")
                                return target_name
                            except:
                                return entry.name # اگر تغییر نام نشد، از همون قبلی استفاده کن
                        return entry.name
        except: pass
        return target_name

    def run(self):
        try:
            files = [p for p in self.source_dir.rglob("*") if p.is_file()]
            total = len(files)
            if total == 0: self.progress.emit(100); return
            
            for i, path in enumerate(files):
                if self._stop.is_set(): break
                ext = path.suffix.lower()
                
                # Logic for Audio
                if ext in {'.mp3', '.wav', '.flac'}:
                    meta = AudioAnalyzer.analyze(path)
                    pref_artist = AudioAnalyzer.get_preferred_name(meta["artist"], self.audio_pref) or "سایر_آهنگ‌ها"
                    
                    # Resolve Root: موسیقی_و_صوت
                    root_dir = self.dest_dir / "موسیقی_و_صوت"
                    root_dir.mkdir(parents=True, exist_ok=True)
                    
                    # Resolve Artist Folder (With Sync)
                    artist_name = self._find_and_sync_folder(root_dir, pref_artist, is_artist=True)
                    artist_dir = root_dir / artist_name
                    artist_dir.mkdir(parents=True, exist_ok=True)
                    
                    # Resolve Album or Year
                    sub = meta["album"] or meta["year"]
                    if sub:
                        sub_name = self._find_and_sync_folder(artist_dir, sub)
                        final_dir = artist_dir / sub_name
                    else:
                        final_dir = artist_dir
                    
                    final_name = AudioAnalyzer.destination_filename(path, meta, self.audio_pref)
                else:
                    # Others
                    final_dir = self.dest_dir / ("تصاویر" if ext in {'.psd', '.jpg', '.png'} else "سایر")
                    final_name = path.name

                final_dir.mkdir(parents=True, exist_ok=True)
                dest = final_dir / final_name
                if dest.exists(): dest = final_dir / f"{Path(final_name).stem}_کپی{Path(final_name).suffix}"
                
                try:
                    shutil.copy2(path, dest)
                    self.log.emit(f"بایگانی: {final_name}")
                except Exception as e: self.log.emit(f"خطا: {e}")
                
                self.progress.emit(int((i+1)*100/total))
        finally: self.finished.emit()

    def stop(self): self._stop.set()
