import os
import shutil
import threading
from datetime import datetime
from pathlib import Path

import jdatetime
from PySide6.QtCore import QObject, Signal

from database import DatabaseManager
from file_analyzer import (
    ARCH_EXTS,
    DOC_EXTS,
    IMAGE_EXTS,
    MEDIA_EXTS,
    THREE_D_EXTS,
    VECTOR_EXTS,
    ZIP_EXTS,
    FileAnalyzer,
)
from gemma_connector import GemmaConnector


class ArchiveWorker(QObject):
    progress = Signal(int)
    log = Signal(str)
    finished = Signal()

    def __init__(self, source_dir, dest_dir, use_date=True, use_persian=False):
        super().__init__()
        self.source_dir = Path(source_dir)
        self.dest_dir = Path(dest_dir)
        self.use_date = use_date
        self.use_persian = use_persian
        self.move_mode = True
        self._pause = threading.Event()
        self._pause.set()
        self._stop = threading.Event()
        self.db = DatabaseManager()
        self.gemma = GemmaConnector()

    def pause(self):
        self._pause.clear()

    def resume(self):
        self._pause.set()

    def stop(self):
        self._stop.set()
        self._pause.set()

    def _wait(self):
        while not self._pause.is_set():
            if self._stop.is_set():
                return False
            threading.Event().wait(0.1)
        return not self._stop.is_set()

    def _validate_paths(self):
        """از انتخاب اشتباه مبدأ/مقصد و مرتب‌سازی فایل‌های مقصد جلوگیری می‌کند."""
        if not self.source_dir.is_dir():
            raise ValueError(f"Source folder does not exist: {self.source_dir}")

        source = self.source_dir.resolve()
        destination = self.dest_dir.resolve()

        if source == destination:
            raise ValueError("Source and destination folders must be different.")
        if source in destination.parents:
            raise ValueError("Destination folder must not be inside the source folder.")

    def _date_folder(self):
        if not self.use_date:
            return None
        now = datetime.now()
        if self.use_persian:
            j = jdatetime.datetime.fromgregorian(datetime=now)
            return f"{j.year:04d}-{j.month:02d}-{j.day:02d}"
        return now.strftime("%Y-%m-%d")

    def _image_hint_to_folder(self, ai_hint):
        if not ai_hint:
            return ["تصاویر", "سایر"]

        category = str(ai_hint.get("category", "images")).strip().lower()
        subcategory = str(ai_hint.get("subcategory", "other")).strip().lower()
        confidence = float(ai_hint.get("confidence", 0.0) or 0.0)

        if confidence < 0.5:
            return ["تصاویر", "سایر"]

        if category in {"people", "person", "human", "humans"}:
            return ["تصاویر", "انسان"]
        if category in {"animals", "animal"}:
            return ["تصاویر", "حیوان", subcategory or "سایر"]
        if category in {"landscape", "landscapes"}:
            return ["تصاویر", "منظره", subcategory or "سایر"]
        if category in {"plant", "plants"}:
            return ["تصاویر", "گیاه"]
        if category in {"food"}:
            return ["تصاویر", "غذا", subcategory or "سایر"]
        if category in {"building", "architecture"}:
            return ["تصاویر", "ساختمان", subcategory or "سایر"]
        if category in {"vehicle", "vehicles"}:
            return ["تصاویر", "خودرو", subcategory or "سایر"]
        if category in {"documents", "document"}:
            return ["تصاویر", "اسناد", subcategory or "سایر"]
        if category in {"objects", "object"}:
            return ["تصاویر", "اشیاء", subcategory or "سایر"]
        if category in {"art_texture", "art", "texture"}:
            return ["تصاویر", "هنر و تکسچر"]
        return ["تصاویر", "سایر"]

    def _main_folder_for(self, path, ai_hint=None):
        ext = path.suffix.lower()

        if ext in VECTOR_EXTS:
            mapping = {
                ".ai": ["وکتور", "Illustrator"],
                ".psd": ["وکتور", "Photoshop"],
                ".cdr": ["وکتور", "CorelDRAW"],
                ".eps": ["وکتور", "EPS"],
                ".svg": ["وکتور", "SVG"],
                ".fig": ["وکتور", "Figma"],
                ".sketch": ["وکتور", "Sketch"],
                ".afdesign": ["وکتور", "Affinity"],
            }
            return mapping.get(ext, ["وکتور", "سایر"])

        if ext in ARCH_EXTS:
            mapping = {
                ".dwg": ["معماری", "AutoCAD"],
                ".dxf": ["معماری", "AutoCAD"],
                ".ifc": ["معماری", "تبادل"],
                ".step": ["معماری", "تبادل"],
                ".stp": ["معماری", "تبادل"],
                ".iges": ["معماری", "تبادل"],
                ".igs": ["معماری", "تبادل"],
            }
            return mapping.get(ext, ["معماری", "تبادل"])

        if ext in THREE_D_EXTS:
            mapping = {
                ".blend": ["سه‌بعدی", "Blender"],
                ".ma": ["سه‌بعدی", "Maya"],
                ".mb": ["سه‌بعدی", "Maya"],
                ".c4d": ["سه‌بعدی", "Cinema4D"],
                ".fbx": ["سه‌بعدی", "تبادل"],
                ".obj": ["سه‌بعدی", "تبادل"],
                ".gltf": ["سه‌بعدی", "تبادل"],
                ".glb": ["سه‌بعدی", "تبادل"],
                ".usd": ["سه‌بعدی", "تبادل"],
                ".usda": ["سه‌بعدی", "تبادل"],
                ".usdc": ["سه‌بعدی", "تبادل"],
            }
            return mapping.get(ext, ["سه‌بعدی", "تبادل"])

        if ext in MEDIA_EXTS:
            if ext in {".mp3", ".wav", ".flac", ".aac", ".m4a"}:
                return ["چندرسانه‌ای", "موسیقی"]
            return ["چندرسانه‌ای", "ویدئو"]

        if ext in DOC_EXTS:
            return ["سایر", "اسناد"]

        if ext in ZIP_EXTS:
            return ["سایر", "فشرده"]

        if ext in IMAGE_EXTS:
            if ai_hint:
                return self._image_hint_to_folder(ai_hint)
            return ["تصاویر", "سایر"]

        return ["سایر", "سایر"]

    def _target_dir(self, parts):
        if self.use_date:
            date_part = self._date_folder()
            if date_part:
                parts = list(parts) + [date_part]
        target_dir = self.dest_dir.joinpath(*parts)
        target_dir.mkdir(parents=True, exist_ok=True)
        return target_dir

    def _dest_path(self, path, parts):
        return self._target_dir(parts) / path.name

    def _copy_or_move(self, src, dst):
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        if self.move_mode:
            try:
                os.remove(src)
            except Exception:
                pass

    def _preview_path(self, main_parts, image_path):
        preview_dir = self._target_dir(main_parts + ["preview"])
        return preview_dir / image_path.name

    def _scan_pairs(self, files):
        by_stem = {}
        for p in files:
            by_stem.setdefault(p.stem.lower(), []).append(p)
        return by_stem

    def run(self):
        try:
            self._validate_paths()
            self.log.emit("Safe test mode: files will be copied; source files will not be deleted.")
            files = [p for p in self.source_dir.rglob("*") if p.is_file()]
            total = max(len(files), 1)
            index = 0
            processed = set()
            pairs = self._scan_pairs(files)

            for _, items in pairs.items():
                if self._stop.is_set():
                    break

                images = [x for x in items if x.suffix.lower() in IMAGE_EXTS]
                mains = [x for x in items if x.suffix.lower() not in IMAGE_EXTS]

                if mains:
                    for main_file in sorted(mains):
                        if main_file in processed:
                            continue
                        processed.add(main_file)

                        if not self._wait():
                            break

                        md5, sha256 = FileAnalyzer.hash_file(main_file)
                        meta = FileAnalyzer.basic_metadata(main_file)

                        if self.db.has_sha256(sha256):
                            self.db.insert_duplicate(str(main_file), sha256)
                            self.log.emit(f"Duplicate skipped: {main_file}")
                            index += 1
                            self.progress.emit(int(index * 100 / total))
                            continue

                        main_parts = self._main_folder_for(main_file)
                        dest_main = self._dest_path(main_file, main_parts)

                        if not dest_main.exists():
                            self._copy_or_move(main_file, dest_main)
                            self.db.insert_file(
                                str(main_file),
                                str(dest_main),
                                md5,
                                sha256,
                                meta["size"],
                                meta["mtime"],
                                meta["mime"],
                                {"type": "main", **meta},
                            )
                            self.log.emit(f"Archived main: {main_file.name} -> {dest_main}")
                        else:
                            self.db.insert_duplicate(str(main_file), sha256)
                            self.log.emit(f"Destination exists, skipped main: {main_file}")

                        index += 1
                        self.progress.emit(int(index * 100 / total))

                        for img in images:
                            if img in processed:
                                continue
                            processed.add(img)

                            if not self._wait():
                                break

                            img_md5, img_sha256 = FileAnalyzer.hash_file(img)
                            img_meta = FileAnalyzer.basic_metadata(img)
                            preview_dst = self._preview_path(main_parts, img)

                            if self.db.has_sha256(img_sha256):
                                self.db.insert_duplicate(str(img), img_sha256)
                                self.log.emit(f"Duplicate preview skipped: {img}")
                                index += 1
                                self.progress.emit(int(index * 100 / total))
                                continue

                            if not preview_dst.exists():
                                self._copy_or_move(img, preview_dst)
                                self.db.insert_file(
                                    str(img),
                                    str(preview_dst),
                                    img_md5,
                                    img_sha256,
                                    img_meta["size"],
                                    img_meta["mtime"],
                                    img_meta["mime"],
                                    {"type": "preview", "paired_with": str(main_file), **img_meta},
                                )
                                self.log.emit(f"Archived preview: {img.name} -> {preview_dst}")
                            else:
                                self.db.insert_duplicate(str(img), img_sha256)
                                self.log.emit(f"Destination exists, skipped preview: {img}")

                            index += 1
                            self.progress.emit(int(index * 100 / total))

                else:
                    for img in images:
                        if img in processed:
                            continue
                        processed.add(img)

                        if not self._wait():
                            break

                        md5, sha256 = FileAnalyzer.hash_file(img)
                        meta = FileAnalyzer.basic_metadata(img)

                        if self.db.has_sha256(sha256):
                            self.db.insert_duplicate(str(img), sha256)
                            self.log.emit(f"Duplicate skipped: {img}")
                            index += 1
                            self.progress.emit(int(index * 100 / total))
                            continue

                        try:
                            ai_hint = self.gemma.analyze_image(img)
                        except Exception as e:
                            ai_hint = None
                            self.log.emit(f"Gemma error for {img.name}: {e}")

                        parts = self._main_folder_for(img, ai_hint=ai_hint)
                        dest = self._dest_path(img, parts)

                        if not dest.exists():
                            self._copy_or_move(img, dest)
                            self.db.insert_file(
                                str(img),
                                str(dest),
                                md5,
                                sha256,
                                meta["size"],
                                meta["mtime"],
                                meta["mime"],
                                {"type": "image", "ai": ai_hint, **meta},
                            )
                            self.log.emit(f"Archived image: {img.name} -> {dest}")
                        else:
                            self.db.insert_duplicate(str(img), sha256)
                            self.log.emit(f"Destination exists, skipped: {img}")

                        index += 1
                        self.progress.emit(int(index * 100 / total))

            self.progress.emit(100)
        except Exception as error:
            self.log.emit(f"ERROR: {type(error).__name__}: {error}")
        finally:
            self.db.close()
            self.finished.emit()
