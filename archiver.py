import os
import shutil
import threading
from datetime import datetime
from pathlib import Path
from PySide6.QtCore import QObject, Signal

class ArchiveWorker(QObject):
    progress = Signal(int)
    log = Signal(str)
    finished = Signal()

    def __init__(self, source_dir, dest_dir, **kwargs):
        super().__init__()
        self.source_dir = Path(source_dir)
        self.dest_dir = Path(dest_dir)
        self.move_mode = bool(kwargs.get('delete_after_copy', False))
        self._stop = threading.Event()

    def _get_creator_path(self, name, ext):
        """Usage-Centric Logic for Content Creators & Designers"""
        
        # 1. Social Media UI & Interaction
        if any(x in name for x in ["subscribe", "like", "follow", "instagram", "youtube", "social", "button", "دکمه", "سابسکرایب"]):
            return ["۰۴_عناصر_تعاملی_و_آیکون", "شبکه‌های_اجتماعی"]
        
        # 2. Overlays & Light Effects (For Reels & Photoshop)
        if any(x in name for x in ["light", "flare", "dust", "overlay", "grain", "sparkle", "نور", "افکت"]):
            return ["۰۲_عناصر_روی‌هم‌گذار", "نور_و_بافت_سینمایی"]

        # 3. Backgrounds & Materials (The 'Base' layer)
        if any(x in name for x in ["bg", "background", "texture", "gold", "silver", "metal", "stone", "پس_زمینه", "طلا", "فلز"]):
            return ["۰۱_متریال_و_پس‌زمینه", "بافت_و_پایه"]

        # 4. Templates & Layouts (Reels vs Covers)
        if any(x in name for x in ["reel", "story", "vertical", "mobile", "ریلز", "استوری", "عمودی"]):
            return ["۰۶_قالب_و_چیدمان", "عمودی_ریلز_استوری"]
        if any(x in name for x in ["cover", "thumbnail", "banner", "youtube", "کاور", "بنر", "یوتیوب"]):
            return ["۰۶_قالب_و_چیدمان", "افقی_کاور_یوتیوب"]

        # 5. PNG Cutouts & Objects
        if any(x in name for x in ["png", "cutout", "object", "car", "person", "phone", "بدون_پس_زمینه", "ماشین", "موبایل"]):
            return ["۰۳_اشیاء_و_دوربری", "آماده_استفاده"]

        # 6. Typography
        if any(x in name for x in ["text", "quote", "title", "calligraphy", "متن", "عنوان", "خوشنویسی"]):
            return ["۰۵_تایپوگرافی_و_عنوان"]

        return None

    def _get_ultimate_path(self, path):
        ext = path.suffix.lower()
        name = path.stem.lower()
        
        # Creator Logic First
        creator_path = self._get_creator_path(name, ext)
        if creator_path:
            root = "۰۱_آرشیو_تولید_محتوا"
            return [root] + creator_path

        # Standard Taxonomy Fallback
        if ext in {'.jpg', '.png', '.webp'}: return ["۰۲_کتابخانه_تصاویر", "سایر"]
        if ext in {'.ai', '.eps', '.svg'}: return ["۰۳_گرافیک_وکتور", "سایر"]
        if ext in {'.mp4', '.mov'}: return ["۰۴_ویدئو_و_فوتیج"]
        if ext in {'.pdf', '.docx'}: return ["۰۵_اسناد_و_متون"]
        
        return ["۹۹_سایر_موارد"]

    def run(self):
        files = [p for p in self.source_dir.rglob("*") if p.is_file()]
        total = len(files)
        for i, path in enumerate(files):
            if self._stop.is_set(): break
            parts = self._get_ultimate_path(path)
            target = self.dest_dir.joinpath(*parts)
            target.mkdir(parents=True, exist_ok=True)
            dest = target / path.name
            if dest.exists():
                dest = target / f"{path.stem}_{int(datetime.now().timestamp())}{path.suffix}"
            try:
                shutil.copy2(path, dest)
                if self.move_mode: os.remove(path)
                self.log.emit(f"Ready for Design: {path.name}")
            except Exception as e:
                self.log.emit(f"ERR: {path.name} | {str(e)}")
            self.progress.emit(int((i+1)*100/max(total, 1)))
        self.finished.emit()

    def stop(self): self._stop.set()
