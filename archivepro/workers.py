"""
workers.py
اجرای عملیات کپی/جابجایی و دسته‌بندی در ترد جداگانه (QThread) - بدون قفل UI
Stop = safe (finishes the file currently being processed, then stops)
Pause = waits between files
"""

import os
import shutil
from pathlib import Path

from PySide6.QtCore import QThread, Signal

from utils import (
    calculate_hash, IMAGE_EXTS, VECTOR_EXTS, ARCHITECTURE_EXTS, THREE_D_EXTS,
    AUDIO_EXTS, VIDEO_EXTS, DOCUMENT_EXTS, OFFICE_EXTS, ARCHIVE_EXTS,
    DATABASE_EXTS, GAME_EXTS, WINDOWS_SOFTWARE_EXTS, ANDROID_SOFTWARE_EXTS,
    IOS_SOFTWARE_EXTS, MAC_SOFTWARE_EXTS, LINUX_SOFTWARE_EXTS,
)
from classifiers import ImageClassifier, GraphicsClassifier, AudioClassifier, SoftwareClassifier


def unique_dest(dest_path: Path) -> Path:
    """Avoid overwriting: file.ext -> file_copy1.ext, file_copy2.ext, ..."""
    if not dest_path.exists():
        return dest_path
    stem, suffix, parent = dest_path.stem, dest_path.suffix, dest_path.parent
    i = 1
    while True:
        candidate = parent / f"{stem}_copy{i}{suffix}"
        if not candidate.exists():
            return candidate
        i += 1


class BaseWorker(QThread):
    progress = Signal(int, int)
    log = Signal(str)
    finished_ok = Signal(dict)

    def __init__(self, sources, dest, mode, db, tab_name):
        super().__init__()
        self.sources = [Path(s) for s in sources]
        self.dest = Path(dest)
        self.mode = mode  # 'copy' | 'move'
        self.db = db
        self.tab_name = tab_name
        self._paused = False
        self._stop_requested = False

    def toggle_pause(self):
        self._paused = not self._paused

    def request_stop(self):
        self._stop_requested = True

    def _wait_if_paused(self):
        while self._paused and not self._stop_requested:
            self.msleep(200)

    def _iter_files(self):
        for src in self.sources:
            if src.is_file():
                yield src
            elif src.is_dir():
                for p in src.rglob("*"):
                    if p.is_file():
                        yield p

    def _transfer(self, src_file: Path, dest_file: Path):
        os.makedirs(dest_file.parent, exist_ok=True)
        dest_file = unique_dest(dest_file)
        if self.mode == "copy":
            shutil.copy2(src_file, dest_file)
        else:
            # copy-first, then remove source (safer than shutil.move on cross-device)
            shutil.copy2(src_file, dest_file)
            if dest_file.exists() and dest_file.stat().st_size == src_file.stat().st_size:
                os.remove(src_file)
        return dest_file

    def _check_duplicate(self, src_file: Path):
        file_hash = calculate_hash(src_file)
        existing = self.db.hash_exists(file_hash) if file_hash else None
        return file_hash, existing

    def run(self):
        raise NotImplementedError


class GeneralWorker(BaseWorker):
    """Tab 1: pure mirror copy/move, no renaming, no classification."""

    def run(self):
        files = list(self._iter_files())
        total = len(files)
        stats = {"processed": 0, "skipped": 0, "failed": 0}

        for idx, src_file in enumerate(files, 1):
            if self._stop_requested:
                break
            self._wait_if_paused()
            if self._stop_requested:
                break
            try:
                # find which source root this file came from, to preserve relative structure
                rel = None
                for root in self.sources:
                    try:
                        rel = src_file.relative_to(root)
                        break
                    except ValueError:
                        continue
                if rel is None:
                    rel = src_file.name
                dest_file = self.dest / rel

                file_hash, dup = self._check_duplicate(src_file)
                if dup:
                    stats["skipped"] += 1
                    self.log.emit(f"⚠ duplicate skipped: {src_file.name}")
                else:
                    final_dest = self._transfer(src_file, dest_file)
                    stats["processed"] += 1
                    self.db.insert_file({
                        "tab": self.tab_name, "source": str(src_file), "dest": str(final_dest),
                        "category": "", "sub_category": "", "filename": final_dest.name,
                        "file_hash": file_hash, "size": src_file.stat().st_size, "status": "ok",
                    })
                    self.log.emit(f"✔ {src_file.name} -> {final_dest}")
            except Exception as e:
                stats["failed"] += 1
                self.log.emit(f"✘ error: {src_file.name} ({e})")

            self.progress.emit(idx, total)

        self.finished_ok.emit(stats)


class ImagesWorker(BaseWorker):
    def __init__(self, sources, dest, mode, db, tab_name, image_mode, use_ocr, detect_screenshot):
        super().__init__(sources, dest, mode, db, tab_name)
        self.classifier = ImageClassifier(mode=image_mode, use_ocr=use_ocr, detect_screenshot=detect_screenshot)

    def run(self):
        files = [f for f in self._iter_files() if f.suffix.lower() in IMAGE_EXTS]
        total = len(files)
        stats = {"processed": 0, "skipped": 0, "failed": 0}

        for idx, src_file in enumerate(files, 1):
            if self._stop_requested:
                break
            self._wait_if_paused()
            if self._stop_requested:
                break
            try:
                file_hash, dup = self._check_duplicate(src_file)
                if dup:
                    stats["skipped"] += 1
                    self.log.emit(f"⚠ duplicate skipped: {src_file.name}")
                    self.progress.emit(idx, total)
                    continue

                main_cat, sub_path = self.classifier.classify(src_file)
                dest_file = self.dest / "Images" / main_cat / sub_path / src_file.name
                final_dest = self._transfer(src_file, dest_file)
                stats["processed"] += 1
                self.db.insert_file({
                    "tab": self.tab_name, "source": str(src_file), "dest": str(final_dest),
                    "category": main_cat, "sub_category": sub_path, "filename": final_dest.name,
                    "file_hash": file_hash, "size": src_file.stat().st_size, "status": "ok",
                })
                self.log.emit(f"✔ [{main_cat}] {src_file.name} -> {final_dest}")
            except Exception as e:
                stats["failed"] += 1
                self.log.emit(f"✘ error: {src_file.name} ({e})")

            self.progress.emit(idx, total)

        self.finished_ok.emit(stats)


class GraphicsWorker(BaseWorker):
    def __init__(self, sources, dest, mode, db, tab_name, auto_preview, use_ocr):
        super().__init__(sources, dest, mode, db, tab_name)
        self.classifier = GraphicsClassifier(auto_generate_preview=auto_preview, use_ocr=use_ocr)

    def run(self):
        vector_exts = set(VECTOR_EXTS.keys())
        files = [f for f in self._iter_files() if f.suffix.lower() in vector_exts]
        total = len(files)
        stats = {"processed": 0, "skipped": 0, "failed": 0}

        for idx, src_file in enumerate(files, 1):
            if self._stop_requested:
                break
            self._wait_if_paused()
            if self._stop_requested:
                break
            try:
                file_hash, dup = self._check_duplicate(src_file)
                if dup:
                    stats["skipped"] += 1
                    self.log.emit(f"⚠ duplicate skipped: {src_file.name}")
                    self.progress.emit(idx, total)
                    continue

                software, category, preview = self.classifier.classify(src_file)
                dest_dir = self.dest / "Graphics" / software / category
                dest_file = dest_dir / src_file.name
                final_dest = self._transfer(src_file, dest_file)

                # move/copy sidecar preview alongside
                if preview is not None and preview.exists():
                    preview_dest = dest_dir / preview.name
                    try:
                        self._transfer(preview, preview_dest)
                    except Exception:
                        pass

                stats["processed"] += 1
                self.db.insert_file({
                    "tab": self.tab_name, "source": str(src_file), "dest": str(final_dest),
                    "category": software, "sub_category": category, "filename": final_dest.name,
                    "file_hash": file_hash, "size": src_file.stat().st_size, "status": "ok",
                })
                self.log.emit(f"✔ [{software}/{category}] {src_file.name} -> {final_dest}")
            except Exception as e:
                stats["failed"] += 1
                self.log.emit(f"✘ error: {src_file.name} ({e})")

            self.progress.emit(idx, total)

        self.finished_ok.emit(stats)


class AudioWorker(BaseWorker):
    def __init__(self, sources, dest, mode, db, tab_name, persian_names, use_album_folder):
        super().__init__(sources, dest, mode, db, tab_name)
        self.classifier = AudioClassifier(persian_names=persian_names, use_album_folder=use_album_folder)

    def run(self):
        files = [f for f in self._iter_files() if f.suffix.lower() in AUDIO_EXTS]
        total = len(files)
        stats = {"processed": 0, "skipped": 0, "failed": 0}

        for idx, src_file in enumerate(files, 1):
            if self._stop_requested:
                break
            self._wait_if_paused()
            if self._stop_requested:
                break
            try:
                file_hash, dup = self._check_duplicate(src_file)
                if dup:
                    stats["skipped"] += 1
                    self.log.emit(f"⚠ duplicate skipped: {src_file.name}")
                    self.progress.emit(idx, total)
                    continue

                sub_path, filename = self.classifier.classify(src_file)
                dest_file = self.dest / "Audio" / sub_path / f"{filename}{src_file.suffix.lower()}"
                final_dest = self._transfer(src_file, dest_file)
                stats["processed"] += 1
                self.db.insert_file({
                    "tab": self.tab_name, "source": str(src_file), "dest": str(final_dest),
                    "category": sub_path, "sub_category": "", "filename": final_dest.name,
                    "file_hash": file_hash, "size": src_file.stat().st_size, "status": "ok",
                })
                self.log.emit(f"✔ {src_file.name} -> {final_dest}")
            except Exception as e:
                stats["failed"] += 1
                self.log.emit(f"✘ error: {src_file.name} ({e})")

            self.progress.emit(idx, total)

        self.finished_ok.emit(stats)


class SoftwareWorker(BaseWorker):
    ALL_SOFTWARE_EXTS = (WINDOWS_SOFTWARE_EXTS | ANDROID_SOFTWARE_EXTS | IOS_SOFTWARE_EXTS
                         | MAC_SOFTWARE_EXTS | LINUX_SOFTWARE_EXTS)

    def __init__(self, sources, dest, mode, db, tab_name, online_detection):
        super().__init__(sources, dest, mode, db, tab_name)
        self.classifier = SoftwareClassifier(online_detection=online_detection)

    def run(self):
        files = [f for f in self._iter_files() if f.suffix.lower() in self.ALL_SOFTWARE_EXTS]
        total = len(files)
        stats = {"processed": 0, "skipped": 0, "failed": 0}

        for idx, src_file in enumerate(files, 1):
            if self._stop_requested:
                break
            self._wait_if_paused()
            if self._stop_requested:
                break
            try:
                file_hash, dup = self._check_duplicate(src_file)
                if dup:
                    stats["skipped"] += 1
                    self.log.emit(f"⚠ duplicate skipped: {src_file.name}")
                    self.progress.emit(idx, total)
                    continue

                platform, category, app_name = self.classifier.classify(src_file)
                dest_file = self.dest / "Software" / platform / category / app_name / src_file.name
                final_dest = self._transfer(src_file, dest_file)
                stats["processed"] += 1
                self.db.insert_file({
                    "tab": self.tab_name, "source": str(src_file), "dest": str(final_dest),
                    "category": platform, "sub_category": f"{category}/{app_name}",
                    "filename": final_dest.name, "file_hash": file_hash,
                    "size": src_file.stat().st_size, "status": "ok",
                })
                self.log.emit(f"✔ [{platform}/{category}] {src_file.name} -> {final_dest}")
            except Exception as e:
                stats["failed"] += 1
                self.log.emit(f"✘ error: {src_file.name} ({e})")

            self.progress.emit(idx, total)

        self.finished_ok.emit(stats)
