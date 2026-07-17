import os
import shutil
import threading
import time
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
                                self.log.emit(f"🔄 هماهنگی نام پوشه: {target}")
                                return target
                            except: return entry.name
                        return entry.name
        except: pass
        return target

    def run(self):
        try:
            self.log.emit("🔍 در حال جستجوی فایل‌ها در پوشه مبدأ...")
            if not self.source_dir.exists():
                self.log.emit("❌ خطا: پوشه مبدأ پیدا نشد!")
                return

            files = []
            for p in self.source_dir.rglob("*"):
                if self._stop.is_set(): break
                if p.is_file(): files.append(p)
            
            total = len(files)
            self.log.emit(f"📊 تعداد {total} فایل برای پردازش شناسایی شد.")
            
            if total == 0:
                self.log.emit("⚠️ هیچ فایلی برای بایگانی وجود ندارد.")
                self.progress.emit(100)
                return

            for i, path in enumerate(files):
                if self._stop.is_set(): 
                    self.log.emit("🛑 عملیات توسط کاربر متوقف شد.")
                    break
                
                try:
                    ext = path.suffix.lower()
                    if ext in {'.mp3', '.wav', '.flac'}:
                        meta = AudioAnalyzer.analyze(path)
                        artist = AudioAnalyzer.get_persian_artist(meta["artist"]) or "سایر_آهنگ‌ها"
                        root = self.dest_dir / "موسیقی_و_صوت"
                        root.mkdir(parents=True, exist_ok=True)
                        
                        art_folder = self._sync_folder(root, artist, is_artist=True)
                        target_dir = root / art_folder
                        
                        sub = meta["album"] or meta["year"]
                        if sub:
                            target_dir = target_dir / self._sync_folder(target_dir, sub)
                        
                        new_name = AudioAnalyzer.destination_filename(path, meta)
                    else:
                        target_dir = self.dest_dir / ("تصاویر" if ext in {'.jpg', '.png', '.psd'} else "سایر")
                        new_name = path.name

                    target_dir.mkdir(parents=True, exist_ok=True)
                    dest = target_dir / new_name
                    
                    if dest.exists():
                        dest = target_dir / f"{path.stem}_کپی{ext}"
                    
                    shutil.copy2(path, dest)
                    if self.move_mode:
                        try: os.remove(path)
                        except: pass
                    
                    self.log.emit(f"✅ بایگانی شد: {new_name}")
                except Exception as inner_e:
                    self.log.emit(f"❌ خطا در فایل {path.name}: {str(inner_e)}")
                
                self.progress.emit(int((i+1)*100/total))
            
            self.log.emit("✨ فرآیند با موفقیت ۱۰۰٪ به پایان رسید.")
        except Exception as e:
            self.log.emit(f"💥 خطای بحرانی سیستم: {str(e)}")
        finally:
            self.finished.emit()

    def stop(self):
        self._stop.set()
