import os
import shutil
import threading
from datetime import datetime
from pathlib import Path

import jdatetime
from PySide6.QtCore import QObject, Signal

from audio_analyzer import AudioAnalyzer
from database import DatabaseManager
from file_analyzer import (
    ANDROID_APP_EXTS,
    ARCH_EXTS,
    AUDIO_EXTS,
    CODE_EXTS,
    DATA_EXTS,
    DATABASE_EXTS,
    GAME_EXTS,
    IMAGE_EXTS,
    IOS_APP_EXTS,
    ISO_EXTS,
    LINUX_APP_EXTS,
    LINUX_ARCHIVE_EXTS,
    MAC_APP_EXTS,
    OFFICE_EXTS,
    OPENDOCUMENT_EXTS,
    OTHER_EXTS,
    PDF_EXTS,
    POWERPOINT_EXTS,
    SOFTWARE_EXTS,
    TEXT_EXTS,
    THREE_D_EXTS,
    VECTOR_EXTS,
    VIDEO_EXTS,
    WEB_EXTS,
    WINDOWS_APP_EXTS,
    WORD_EXTS,
    EXCEL_EXTS,
    ZIP_EXTS,
    FileAnalyzer,
)
from gemma_connector import GemmaConnector


class ArchiveWorker(QObject):
    progress = Signal(int)
    log = Signal(str)
    finished = Signal()

    def __init__(
        self,
        source_dir,
        dest_dir,
        use_date=True,
        use_persian=False,
        delete_after_copy=False,
        reprocess_archived=False,
        use_gemma=False,
        quarantine_duplicates=False,
    ):
        super().__init__()
        self.source_dir = Path(source_dir)
        self.dest_dir = Path(dest_dir)
        self.use_date = use_date
        self.use_persian = use_persian
        self.move_mode = bool(delete_after_copy)
        self.reprocess_archived = bool(reprocess_archived)
        self.use_gemma = bool(use_gemma)
        self.quarantine_duplicates = bool(quarantine_duplicates)
        self.gemma_available = False
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
            jalali = jdatetime.datetime.fromgregorian(datetime=now)
            return f"{jalali.year:04d}-{jalali.month:02d}-{jalali.day:02d}"
        return now.strftime("%Y-%m-%d")

    @staticmethod
    def _subcategory_label(subcategory):
        labels = {
            "logo": "لوگو",
            "art": "هنر",
            "texture": "تکسچر",
            "portrait": "پرتره",
            "other": "سایر",
            "": "سایر",
        }
        return labels.get(str(subcategory).strip().lower(), "سایر")

    def _image_hint_to_folder(self, ai_hint):
        if not ai_hint:
            return ["تصاویر", "سایر"]

        category = str(ai_hint.get("category", "images")).strip().lower()
        subcategory = self._subcategory_label(ai_hint.get("subcategory", "other"))
        confidence = float(ai_hint.get("confidence", 0.0) or 0.0)
        if confidence < 0.5:
            return ["تصاویر", "سایر"]

        if category in {"people", "person", "human", "humans"}:
            return ["تصاویر", "انسان"]
        if category in {"animals", "animal"}:
            return ["تصاویر", "حیوان", subcategory]
        if category in {"landscape", "landscapes"}:
            return ["تصاویر", "منظره", subcategory]
        if category in {"plant", "plants"}:
            return ["تصاویر", "گیاه", subcategory]
        if category == "food":
            return ["تصاویر", "غذا", subcategory]
        if category in {"building", "architecture"}:
            return ["تصاویر", "ساختمان", subcategory]
        if category in {"vehicle", "vehicles"}:
            return ["تصاویر", "خودرو", subcategory]
        if category in {"objects", "object"}:
            return ["تصاویر", "اشیاء", subcategory]
        if category in {"art_texture", "art", "texture"}:
            return ["تصاویر", "هنر" if subcategory == "هنر" else "تکسچر"]
        return ["تصاویر", "سایر"]

    def _main_folder_for(self, path, ai_hint=None, audio_hint=None):
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
            return mapping[ext]

        if ext in ARCH_EXTS:
            mapping = {
                ".dwg": ["معماری", "AutoCAD"],
                ".dxf": ["معماری", "AutoCAD"],
                ".skp": ["معماری", "SketchUp"],
                ".rvt": ["معماری", "Revit"],
                ".ifc": ["معماری", "تبادل", "IFC"],
                ".step": ["معماری", "تبادل", "STEP"],
                ".stp": ["معماری", "تبادل", "STEP"],
                ".iges": ["معماری", "تبادل", "IGES"],
                ".igs": ["معماری", "تبادل", "IGES"],
            }
            return mapping[ext]

        if ext in THREE_D_EXTS:
            mapping = {
                ".blend": ["سه‌بعدی", "Blender"],
                ".ma": ["سه‌بعدی", "Maya"],
                ".mb": ["سه‌بعدی", "Maya"],
                ".max": ["سه‌بعدی", "3ds_Max"],
                ".3ds": ["سه‌بعدی", "3ds_Max"],
                ".c4d": ["سه‌بعدی", "Cinema4D"],
                ".fbx": ["سه‌بعدی", "تبادل", "FBX"],
                ".obj": ["سه‌بعدی", "تبادل", "OBJ"],
                ".dae": ["سه‌بعدی", "تبادل", "DAE"],
                ".gltf": ["سه‌بعدی", "تبادل", "GLTF"],
                ".glb": ["سه‌بعدی", "تبادل", "GLTF"],
                ".usd": ["سه‌بعدی", "تبادل", "USD"],
                ".usda": ["سه‌بعدی", "تبادل", "USD"],
                ".usdc": ["سه‌بعدی", "تبادل", "USD"],
                ".stl": ["سه‌بعدی", "چاپ_سه‌بعدی", "STL"],
                ".3mf": ["سه‌بعدی", "چاپ_سه‌بعدی", "3MF"],
                ".amf": ["سه‌بعدی", "چاپ_سه‌بعدی", "AMF"],
                ".vrm": ["سه‌بعدی", "VR_AR", "VRM"],
                ".x3d": ["سه‌بعدی", "VR_AR", "X3D"],
            }
            return mapping[ext]

        if ext in AUDIO_EXTS:
            return AudioAnalyzer.folder_parts(audio_hint or AudioAnalyzer.analyze(path))
        if ext in VIDEO_EXTS:
            return ["ویدئو", "سایر"]

        if ext in WORD_EXTS:
            return ["آفیس", "Word"]
        if ext in EXCEL_EXTS and ext != ".csv":
            return ["آفیس", "Excel"]
        if ext in POWERPOINT_EXTS:
            return ["آفیس", "PowerPoint"]
        if ext in OPENDOCUMENT_EXTS:
            return ["آفیس", "OpenDocument"]

        if ext in PDF_EXTS:
            return ["اسناد", "PDF"]
        if ext in TEXT_EXTS:
            return ["اسناد", "متنی"]
        if ext in DATA_EXTS:
            return ["اسناد", "داده"]
        if ext in WEB_EXTS:
            return ["اسناد", "وب"]
        if ext in CODE_EXTS:
            return ["اسناد", "کد"]

        if ext in ZIP_EXTS:
            return ["فشرده", "زیپ" if ext == ".zip" else "رار" if ext == ".rar" else "۷زیپ"]
        if ext in LINUX_ARCHIVE_EXTS:
            return ["فشرده", "لینوکس"]
        if ext in ISO_EXTS:
            return ["فشرده", "ایزو"]

        if ext in WINDOWS_APP_EXTS:
            return ["نرم‌افزار", "ویندوز"]
        if ext in ANDROID_APP_EXTS:
            return ["نرم‌افزار", "اندروید"]
        if ext in IOS_APP_EXTS:
            return ["نرم‌افزار", "iOS"]
        if ext in LINUX_APP_EXTS:
            return ["نرم‌افزار", "لینوکس"]
        if ext in MAC_APP_EXTS:
            return ["نرم‌افزار", "مک"]

        if ext in DATABASE_EXTS:
            if ext == ".sql":
                return ["پایگاه‌داده", "SQL"]
            if ext in {".db", ".sqlite", ".sqlite3"}:
                return ["پایگاه‌داده", "SQLite"]
            return ["پایگاه‌داده", "Access"]

        if ext in GAME_EXTS:
            mapping = {
                ".unity": "Unity", ".uproject": "Unreal", ".godot": "Godot",
                ".sav": "Save", ".rom": "ROM",
            }
            return ["بازی", mapping[ext]]

        if ext in IMAGE_EXTS:
            return self._image_hint_to_folder(ai_hint) if ai_hint else ["تصاویر", "سایر"]

        if ext in OTHER_EXTS:
            mapping = {".torrent": "تورنت", ".log": "لاگ", ".tmp": "موقت", ".bak": "پشتیبان", ".old": "پشتیبان"}
            return ["سایر", mapping[ext]]
        return ["سایر", "سایر"]

    def _target_dir(self, parts):
        folder_parts = list(parts)
        date_part = self._date_folder()
        if date_part:
            folder_parts.append(date_part)
        target_dir = self.dest_dir.joinpath(*folder_parts)
        target_dir.mkdir(parents=True, exist_ok=True)
        return target_dir

    def _dest_path(self, path, parts, destination_name=None):
        target_dir = self._target_dir(parts)
        filename = destination_name or path.name
        candidate = target_dir / filename
        if not candidate.exists():
            return candidate

        filename_path = Path(filename)
        counter = 1
        while True:
            candidate = target_dir / f"{filename_path.stem} ({counter}){filename_path.suffix}"
            if not candidate.exists():
                return candidate
            counter += 1

    def _copy_or_move(self, source, destination):
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
        if self.move_mode:
            try:
                os.remove(source)
            except OSError as error:
                self.log.emit(f"Copied, but source could not be deleted: {source.name} | {error}")

    def _preview_path(self, main_parts, image_path):
        preview_dir = self._target_dir(list(main_parts) + ["preview"])
        candidate = preview_dir / image_path.name
        if not candidate.exists():
            return candidate
        counter = 1
        while True:
            candidate = preview_dir / f"{image_path.stem} ({counter}){image_path.suffix}"
            if not candidate.exists():
                return candidate
            counter += 1

    def _duplicate_path(self, path):
        """Return a safe destination inside the reviewable duplicate quarantine folder."""
        duplicate_dir = self.dest_dir / "تکراری‌ها"
        duplicate_dir.mkdir(parents=True, exist_ok=True)
        candidate = duplicate_dir / path.name
        if not candidate.exists():
            return candidate

        counter = 1
        while True:
            candidate = duplicate_dir / f"{path.stem} ({counter}){path.suffix}"
            if not candidate.exists():
                return candidate
            counter += 1

    def _handle_duplicate(self, path, sha256, label="Duplicate"):
        """Record an exact SHA-256 duplicate and optionally move it to a safe review folder."""
        self.db.insert_duplicate(str(path), sha256)
        if not self.quarantine_duplicates:
            self.log.emit(f"{label} skipped: {path}")
            return

        try:
            quarantine_destination = self._duplicate_path(path)
            shutil.move(str(path), str(quarantine_destination))
            self.log.emit(f"{label} moved to quarantine: {path.name} -> {quarantine_destination}")
        except Exception as error:
            self.log.emit(f"{label} detected, but could not move it: {path} | {error}")

    @staticmethod
    def _scan_pairs(files):
        by_stem = {}
        for path in files:
            by_stem.setdefault(path.stem.lower(), []).append(path)
        return by_stem

    def _is_duplicate(self, sha256):
        return not self.reprocess_archived and self.db.has_sha256(sha256)

    def _mark_progress(self, index, total):
        self.progress.emit(int(index * 100 / max(total, 1)))

    def _archive_main_file(self, path):
        md5, sha256 = FileAnalyzer.hash_file(path)
        metadata = FileAnalyzer.basic_metadata(path)
        if self._is_duplicate(sha256):
            self._handle_duplicate(path, sha256)
            return self._main_folder_for(path)

        audio_hint = AudioAnalyzer.analyze(path) if path.suffix.lower() in AUDIO_EXTS else None
        parts = self._main_folder_for(path, audio_hint=audio_hint)
        destination_name = AudioAnalyzer.destination_filename(path, audio_hint) if audio_hint else path.name
        destination = self._dest_path(path, parts, destination_name)
        self._copy_or_move(path, destination)
        record_metadata = {"type": "main", **metadata}
        if audio_hint:
            record_metadata["audio"] = audio_hint
        self.db.insert_file(str(path), str(destination), md5, sha256, metadata["size"], metadata["mtime"], metadata["mime"], record_metadata)
        if audio_hint:
            self.log.emit(f"Archived audio: {path.name} -> {destination} | {audio_hint.get('kind', 'music')}")
        else:
            self.log.emit(f"Archived main: {path.name} -> {destination}")
        return parts

    def _archive_preview(self, image_path, main_parts, main_file):
        md5, sha256 = FileAnalyzer.hash_file(image_path)
        metadata = FileAnalyzer.basic_metadata(image_path)
        if self._is_duplicate(sha256):
            self._handle_duplicate(image_path, sha256, "Duplicate preview")
            return

        destination = self._preview_path(main_parts, image_path)
        self._copy_or_move(image_path, destination)
        self.db.insert_file(str(image_path), str(destination), md5, sha256, metadata["size"], metadata["mtime"], metadata["mime"], {"type": "preview", "paired_with": str(main_file), **metadata})
        self.log.emit(f"Archived preview: {image_path.name} -> {destination}")

    def _archive_image(self, image_path):
        md5, sha256 = FileAnalyzer.hash_file(image_path)
        metadata = FileAnalyzer.basic_metadata(image_path)
        if self._is_duplicate(sha256):
            self._handle_duplicate(image_path, sha256)
            return

        if self.use_gemma and self.gemma_available:
            ai_hint = self.gemma.analyze_image(image_path)
        else:
            ai_hint = self.gemma.quick_classify_image(image_path)
        parts = self._main_folder_for(image_path, ai_hint=ai_hint)
        destination = self._dest_path(image_path, parts)
        self._copy_or_move(image_path, destination)
        self.db.insert_file(str(image_path), str(destination), md5, sha256, metadata["size"], metadata["mtime"], metadata["mime"], {"type": "image", "ai": ai_hint, **metadata})
        self.log.emit(f"Archived image: {image_path.name} -> {destination} | {ai_hint.get('reason', '')}")

    def run(self):
        try:
            self._validate_paths()
            mode = "MOVE (source files will be deleted after a successful copy)" if self.move_mode else "COPY (source files will be retained)"
            self.log.emit(f"Processing mode: {mode}")
            if self.reprocess_archived:
                self.log.emit("Reprocess mode is enabled: files already in history will be processed again.")
            elif self.quarantine_duplicates:
                self.log.emit("Exact SHA-256 duplicates will be moved to the تکراری‌ها review folder.")

            if self.use_gemma:
                self.log.emit("Checking Gemma Vision service...")
                self.gemma_available = self.gemma.is_available()
                if self.gemma_available:
                    self.log.emit("Gemma Vision is ready. Image analysis can take time on each image.")
                else:
                    self.log.emit("Gemma Vision is unavailable. Fast filename mode will be used without waiting.")
            else:
                self.log.emit("Fast image mode is enabled. Gemma Vision will not be used.")

            if self.db.legacy_files_table:
                self.log.emit(f"Old database table preserved as {self.db.legacy_files_table}; a new compatible table was created.")

            files = [path for path in self.source_dir.rglob("*") if path.is_file()]
            total = max(len(files), 1)
            index = 0
            processed = set()
            pairs = self._scan_pairs(files)

            for items in pairs.values():
                if self._stop.is_set():
                    break

                images = [path for path in items if path.suffix.lower() in IMAGE_EXTS]
                main_files = [path for path in items if path.suffix.lower() not in IMAGE_EXTS]

                if main_files:
                    for main_file in sorted(main_files):
                        if main_file in processed:
                            continue
                        processed.add(main_file)
                        if not self._wait():
                            break

                        main_parts = self._archive_main_file(main_file)
                        index += 1
                        self._mark_progress(index, total)

                        for image_path in images:
                            if image_path in processed:
                                continue
                            processed.add(image_path)
                            if not self._wait():
                                break
                            self._archive_preview(image_path, main_parts, main_file)
                            index += 1
                            self._mark_progress(index, total)
                else:
                    for image_path in images:
                        if image_path in processed:
                            continue
                        processed.add(image_path)
                        if not self._wait():
                            break
                        self._archive_image(image_path)
                        index += 1
                        self._mark_progress(index, total)

            self.progress.emit(100)
        except Exception as error:
            self.log.emit(f"ERROR: {type(error).__name__}: {error}")
        finally:
            self.db.close()
            self.finished.emit()
