import os
import shutil
import threading
import zipfile
from datetime import datetime
from pathlib import Path

import jdatetime
from PySide6.QtCore import QObject, Signal

from audio_analyzer import AudioAnalyzer
from database import DatabaseManager
from fast_image_analyzer import FastImageAnalyzer
from file_analyzer import (
    ANDROID_APP_EXTS, AUDIO_EXTS, CODE_EXTS, DATA_EXTS, DATABASE_EXTS,
    IMAGE_EXTS, ISO_EXTS, LINUX_APP_EXTS,
    MAC_APP_EXTS, PDF_EXTS,
    POWERPOINT_EXTS, TEXT_EXTS, THREE_D_EXTS, VECTOR_EXTS, VIDEO_EXTS,
    WINDOWS_APP_EXTS, WORD_EXTS, EXCEL_EXTS, ZIP_EXTS, FileAnalyzer,
)
from gemma_connector import GemmaConnector
from photo_analyzer import PhotoAnalyzer
from taxonomy import TaxonomyManager


class ArchiveWorker(QObject):
    progress = Signal(int)
    log = Signal(str)
    finished = Signal()

    PENDING_ROOT = "00_در_انتظار_تکمیل_دسته‌بندی"

    def __init__(
        self,
        source_dir,
        dest_dir,
        use_date=True,
        use_persian=False,
        delete_after_copy=False,
        reprocess_archived=False,
        content_analysis=False,
        use_ocr=True,
        quarantine_duplicates=False,
        focus_types=None,
        family_location_when_dated=True,
        quick_transfer=False,
        project_config=None,
    ):
        super().__init__()
        self.source_dir = Path(source_dir)
        self.dest_dir = Path(dest_dir)
        self.use_date = bool(use_date)
        self.use_persian = bool(use_persian)
        self.move_mode = bool(delete_after_copy)
        self.reprocess_archived = bool(reprocess_archived)
        self.content_analysis = bool(content_analysis)
        self.quarantine_duplicates = bool(quarantine_duplicates)
        self.focus_types = set(focus_types or [])
        self.quick_transfer = bool(quick_transfer)
        self.project_config = dict(project_config or {})
        self.family_location_when_dated = bool(family_location_when_dated and use_date)
        self.gemma_available = False
        self._pause = threading.Event()
        self._pause.set()
        self._stop = threading.Event()
        self.db = DatabaseManager()
        self.gemma = GemmaConnector()
        self.fast_image = FastImageAnalyzer(use_ocr=use_ocr)
        self.taxonomy = TaxonomyManager()

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

    def _is_focused(self, file_group):
        if file_group == "images":
            return bool({"images", "documents"} & self.focus_types)
        return file_group in self.focus_types

    def _validate_paths(self):
        if not self.source_dir.is_dir():
            raise ValueError(f"Source folder does not exist: {self.source_dir}")
        source = self.source_dir.resolve()
        destination = self.dest_dir.resolve()
        if source == destination:
            raise ValueError("Source and destination folders must be different.")
        if source in destination.parents:
            raise ValueError("Destination folder must not be inside the source folder.")

    def _format_date(self, value):
        if self.use_persian:
            jalali = jdatetime.datetime.fromgregorian(datetime=value)
            return f"{jalali.year:04d}-{jalali.month:02d}-{jalali.day:02d}"
        return value.strftime("%Y-%m-%d")

    def _date_folder(self):
        return self._format_date(datetime.now()) if self.use_date else None

    def _format_year(self, value):
        if self.use_persian:
            return str(jdatetime.datetime.fromgregorian(datetime=value).year)
        return str(value.year)

    @staticmethod
    def _is_date_folder(value):
        value = str(value)
        return len(value) == 10 and value[4:5] == "-" and value[7:8] == "-" and value.replace("-", "").isdigit()

    @staticmethod
    def _safe_label(value, fallback="نامشخص"):
        value = str(value or "").strip()
        for character in '<>:"/\\|?*':
            value = value.replace(character, "_")
        value = " ".join(value.split()).strip(" ._")
        return value[:80] if value else fallback

    @staticmethod
    def _subcategory_label(subcategory):
        labels = {
            "logo": "لوگو", "art": "هنر", "texture": "تکسچر", "portrait": "پرتره",
            "invoice": "فاکتور", "contract": "قرارداد", "letter": "نامه",
            "report": "گزارش", "id": "مدارک", "payment": "پرداختی", "other": "سایر", "": "سایر",
        }
        return labels.get(str(subcategory).strip().lower(), "سایر")

    @staticmethod
    def _graphic_app(ext):
        return {
            ".ai": "Illustrator", ".psd": "Photoshop", ".cdr": "CorelDRAW",
            ".eps": "EPS", ".svg": "SVG", ".fig": "Figma", ".sketch": "Sketch",
            ".afdesign": "Affinity",
        }.get(ext.lower(), "سایر")

    def _graphic_companion_hint(self, image_path):
        if image_path is None:
            return {"category": "unclassified", "confidence": 0.0}
        hint = self.gemma.quick_classify_image(image_path)
        if float(hint.get("confidence", 0) or 0) >= 0.5:
            return hint
        fast_hint = self.fast_image.analyze(image_path)
        if float(fast_hint.get("confidence", 0) or 0) >= 0.5:
            return fast_hint
        if self.content_analysis and self.gemma_available:
            return self.gemma.analyze_image(image_path)
        return {"category": "unclassified", "confidence": 0.0}

    def _pending_graphic_parts(self, ext):
        return [self.PENDING_ROOT, "طراحی_گرافیک", self._graphic_app(ext)]

    def _pending_document_parts(self, kind, subtype):
        return [self.PENDING_ROOT, "اسناد_و_نوشتاری", kind, subtype]

    def _family_photo_parts(self, path):
        info = PhotoAnalyzer.exif_info(path)
        location = info.get("location") or "بدون_موقعیت"
        return ["01_تصاویر", "خانوادگی", self._format_year(info["taken_at"]), location]

    def _image_parts(self, path, hint):
        category = str((hint or {}).get("category", "unclassified")).strip().lower()
        confidence = float((hint or {}).get("confidence", 0) or 0)
        screenshot = PhotoAnalyzer.is_screenshot(path)
        subtype = self._subcategory_label((hint or {}).get("subcategory", "other"))

        if screenshot:
            if category in {"documents", "document"} and confidence >= 0.5:
                if str(hint.get("subcategory", "")).lower() == "payment":
                    return ["07_اسناد", "پرداختی", self._safe_label(hint.get("recipient"))], False
                return ["07_اسناد", subtype], False
            if category in {"objects", "object"} and confidence >= 0.5:
                return ["01_تصاویر", "اشیاء", subtype], False
            return ["01_تصاویر", "نماگرفت‌ها", "دسته‌بندی نشده"], False

        if category in {"objects", "object"} and str((hint or {}).get("subcategory", "")).lower() == "logo":
            return ["01_تصاویر", "اشیاء", "لوگو"], False

        taxonomy_terms = f"{path.stem} {(hint or {}).get('taxonomy_terms', '')}"
        taxonomy_path = self.taxonomy.resolve_image_path(category, taxonomy_terms)
        if taxonomy_path and category not in {"people", "person", "documents", "document"}:
            return taxonomy_path, False

        if category in {"documents", "document"} and confidence >= 0.5:
            if str(hint.get("subcategory", "")).lower() == "payment":
                return ["07_اسناد", "پرداختی", self._safe_label(hint.get("recipient"))], False
            return ["07_اسناد", subtype], False
        if category in {"objects", "object"} and confidence >= 0.5:
            return ["01_تصاویر", "اشیاء", subtype], False
        if category in {"food", "plant", "building", "vehicle", "art_texture"} and confidence >= 0.5:
            mapping = {
                "food": "غذا", "plant": "گیاه", "building": "ساختمان",
                "vehicle": "خودرو", "art_texture": "هنر_و_تکسچر",
            }
            return ["01_تصاویر", mapping[category], subtype], False

        if self.family_location_when_dated:
            return self._family_photo_parts(path), False  # Date already included in the explicit family path.
        if category in {"people", "person"} and confidence >= 0.5:
            return ["01_تصاویر", "انسان"], self.use_date
        return ["01_تصاویر", "دسته‌بندی نشده"], self.use_date

    def _graphic_folder_from_content(self, vector_path, companion_image=None):
        app = self._graphic_app(vector_path.suffix)
        name = vector_path.stem.casefold()
        if companion_image:
            name += " " + companion_image.stem.casefold()

        # Usage-oriented graphic asset categories. File names are fast, safe evidence for obvious assets.
        if any(word in name for word in ["logo", "لوگو", "brand", "branding"]):
            return ["02_طراحی_گرافیک", "02_برندینگ_و_تبلیغات", "لوگو", app]
        if any(word in name for word in ["color wheel", "colorwheel", "چرخه رنگ", "palette", "پالت"]):
            return ["02_طراحی_گرافیک", "04_مراجع_طراحی", "چرخه_رنگ", app]
        if any(word in name for word in ["cloud", "ابر", "sky", "آسمان"]):
            return ["02_طراحی_گرافیک", "01_دارایی‌های_طراحی", "آسمان_و_طبیعت", "ابر", app]
        if any(word in name for word in ["flare", "flash", "halo", "light", "هاله", "فلش", "نور"]):
            return ["02_طراحی_گرافیک", "01_دارایی‌های_طراحی", "نور_و_افکت", "فلش_و_LensFlare", app]
        if any(word in name for word in ["background", "backdrop", "bg", "بکگراند", "پس زمینه", "gradient", "گرادیان"]):
            return ["02_طراحی_گرافیک", "01_دارایی‌های_طراحی", "پس‌زمینه", "انتزاعی", app]
        if any(word in name for word in ["icon", "آیکون", "arrow", "فلش راهنما", "frame", "قاب"]):
            return ["02_طراحی_گرافیک", "01_دارایی‌های_طراحی", "عناصر_گرافیکی", "آیکون", app]
        if any(word in name for word in ["poster", "پوستر", "banner", "بنر", "flyer", "تراکت"]):
            return ["02_طراحی_گرافیک", "02_برندینگ_و_تبلیغات", "پوستر", app]

        hint = self._graphic_companion_hint(companion_image)
        category = str(hint.get("category", "unclassified")).lower()
        if category in {"objects", "object"}:
            return ["02_طراحی_گرافیک", "01_دارایی‌های_طراحی", "عناصر_گرافیکی", "آیکون", app]
        if category in {"landscape", "plant"}:
            return ["02_طراحی_گرافیک", "01_دارایی‌های_طراحی", "آسمان_و_طبیعت", "سایر", app]
        if category in {"people", "animal"}:
            return ["02_طراحی_گرافیک", "01_دارایی‌های_طراحی", "تصویرسازی", "سایر", app]
        return ["02_طراحی_گرافیک", "99_دسته‌بندی_نشده", app]

    def _zip_is_android_package(self, path):
        if path.suffix.lower() != ".zip":
            return False
        try:
            with zipfile.ZipFile(path) as archive:
                names = [name.casefold() for name in archive.namelist()]
            return any(name.endswith((".apk", ".xapk", ".apks", ".aab", ".obb")) for name in names)
        except Exception:
            return False

    def _project_parts(self, path):
        """Keep all project files inside one explicit project tree instead of global categories."""
        config = self.project_config
        project_name = self._safe_label(config.get("name"), "پروژه_بدون_نام")
        project_type = config.get("type", "architecture")
        year = self._safe_label(config.get("year"), str(datetime.now().year))
        ext = path.suffix.lower()

        if project_type == "content":
            platform = self._safe_label(config.get("platform"), "سایر")
            content_type = self._safe_label(config.get("content_type"), "سایر")
            root = ["12_پروژه‌ها", "02_تولید_محتوا", platform, content_type, project_name]
            lower = path.stem.casefold()
            if ext in IMAGE_EXTS or ext in VIDEO_EXTS:
                section = "06_خروجی_نهایی" if any(x in lower for x in ["final", "output", "export", "نهایی", "خروجی"]) else "01_فایل‌های_خام"
            elif ext in AUDIO_EXTS:
                section = "02_صوت_و_موسیقی"
            elif ext in VECTOR_EXTS:
                section = "03_گرافیک_و_کاور"
            elif ext in PDF_EXTS or ext in TEXT_EXTS or ext in DATA_EXTS or ext in WEB_EXTS or ext in CODE_EXTS:
                section = "04_متن_و_کپشن"
            else:
                section = "05_فایل_پروژه"
            return root + [section]

        root = ["12_پروژه‌ها", "01_معماری_و_سه‌بعدی", year, project_name]
        lower = path.stem.casefold()
        if ext in {".dwg", ".dxf"}:
            section = "01_اتوکد"
        elif ext in THREE_D_EXTS:
            section = "02_سه‌بعدی"
        elif ext in IMAGE_EXTS:
            section = "03_رندرها" if any(x in lower for x in ["render", "preview", "output", "رندر", "خروجی"]) else "04_تصاویر_مرجع"
        elif ext in VECTOR_EXTS:
            section = "05_متریال_و_تکسچر"
        elif ext in PDF_EXTS or ext in TEXT_EXTS or ext in DATA_EXTS:
            section = "06_اسناد_و_قراردادها"
        else:
            section = "07_خروجی_و_سایر"
        return root + [section]

    def _main_folder_for(self, path, audio_hint=None, paired_image=None):
        if self.project_config:
            return self._project_parts(path)
        ext = path.suffix.lower()

        if ext in VECTOR_EXTS:
            if not self._is_focused("graphics"):
                # Fast transfer still puts graphics in their final graphic branch, not in pending.
                if self.quick_transfer:
                    return ["02_طراحی_گرافیک", "99_دسته‌بندی_نشده", self._graphic_app(ext)]
                return self._pending_graphic_parts(ext)
            return self._graphic_folder_from_content(path, paired_image)

        if ext in ARCH_EXTS:
            mapping = {
                ".dwg": ["03_معماری_CAD", "AutoCAD"], ".dxf": ["03_معماری_CAD", "AutoCAD"],
                ".skp": ["03_معماری_CAD", "SketchUp"], ".rvt": ["03_معماری_CAD", "Revit"],
                ".ifc": ["03_معماری_CAD", "تبادل", "IFC"], ".step": ["03_معماری_CAD", "تبادل", "STEP"],
                ".stp": ["03_معماری_CAD", "تبادل", "STEP"], ".iges": ["03_معماری_CAD", "تبادل", "IGES"],
                ".igs": ["03_معماری_CAD", "تبادل", "IGES"],
            }
            return mapping[ext]

        if ext in THREE_D_EXTS:
            mapping = {
                ".blend": ["04_سه‌بعدی", "Blender"], ".ma": ["04_سه‌بعدی", "Maya"],
                ".mb": ["04_سه‌بعدی", "Maya"], ".max": ["04_سه‌بعدی", "3ds_Max"],
                ".3ds": ["04_سه‌بعدی", "3ds_Max"], ".c4d": ["04_سه‌بعدی", "Cinema4D"],
                ".fbx": ["04_سه‌بعدی", "تبادل", "FBX"], ".obj": ["04_سه‌بعدی", "تبادل", "OBJ"],
                ".dae": ["04_سه‌بعدی", "تبادل", "DAE"], ".gltf": ["04_سه‌بعدی", "تبادل", "GLTF"],
                ".glb": ["04_سه‌بعدی", "تبادل", "GLTF"], ".usd": ["04_سه‌بعدی", "تبادل", "USD"],
                ".usda": ["04_سه‌بعدی", "تبادل", "USD"], ".usdc": ["04_سه‌بعدی", "تبادل", "USD"],
                ".stl": ["04_سه‌بعدی", "چاپ_سه‌بعدی", "STL"], ".3mf": ["04_سه‌بعدی", "چاپ_سه‌بعدی", "3MF"],
                ".amf": ["04_سه‌بعدی", "چاپ_سه‌بعدی", "AMF"], ".vrm": ["04_سه‌بعدی", "VR_AR", "VRM"],
                ".x3d": ["04_سه‌بعدی", "VR_AR", "X3D"],
            }
            return mapping[ext]

        if ext in AUDIO_EXTS:
            if not self._is_focused("audio"):
                return ["05_صوت", "موسیقی", "دسته‌بندی نشده"]
            return ["05_صوت"] + AudioAnalyzer.folder_parts(audio_hint) if audio_hint else ["05_صوت", "موسیقی", "دسته‌بندی نشده"]
        if ext in VIDEO_EXTS:
            return ["06_ویدئو", "سایر"]

        if ext in WORD_EXTS:
            return ["07_اسناد", "آفیس", "Word"] if (self._is_focused("documents") or self.quick_transfer) else self._pending_document_parts("آفیس", "Word")
        if ext in EXCEL_EXTS and ext != ".csv":
            return ["07_اسناد", "آفیس", "Excel"] if (self._is_focused("documents") or self.quick_transfer) else self._pending_document_parts("آفیس", "Excel")
        if ext in POWERPOINT_EXTS:
            return ["07_اسناد", "آفیس", "PowerPoint"] if (self._is_focused("documents") or self.quick_transfer) else self._pending_document_parts("آفیس", "PowerPoint")
        if ext in OPENDOCUMENT_EXTS:
            return ["07_اسناد", "آفیس", "OpenDocument"] if (self._is_focused("documents") or self.quick_transfer) else self._pending_document_parts("آفیس", "OpenDocument")

        if ext in PDF_EXTS:
            return ["07_اسناد", "PDF"] if (self._is_focused("documents") or self.quick_transfer) else self._pending_document_parts("PDF_و_کتاب", "PDF")
        if ext in TEXT_EXTS:
            return ["07_اسناد", "متنی"] if (self._is_focused("documents") or self.quick_transfer) else self._pending_document_parts("متنی", "متنی")
        if ext in DATA_EXTS:
            return ["07_اسناد", "داده"] if (self._is_focused("documents") or self.quick_transfer) else self._pending_document_parts("داده", "داده")
        if ext in WEB_EXTS:
            return ["07_اسناد", "وب"] if (self._is_focused("documents") or self.quick_transfer) else self._pending_document_parts("کد", "وب")
        if ext in CODE_EXTS:
            return ["07_اسناد", "کد"] if (self._is_focused("documents") or self.quick_transfer) else self._pending_document_parts("کد", "کد")

        if ext in ZIP_EXTS:
            if self._zip_is_android_package(path):
                return ["09_نرم‌افزار", "02_اندروید", "بسته‌های_فشرده"]
            return ["10_فشرده", "ZIP" if ext == ".zip" else "RAR" if ext == ".rar" else "7ZIP"]
        if ext in LINUX_ARCHIVE_EXTS:
            return ["10_فشرده", "TAR_GZ"]
        if ext in ISO_EXTS:
            return ["10_فشرده", "ISO"]

        if ext in WINDOWS_APP_EXTS:
            subfolder = {".exe": "نصب‌کننده_EXE", ".msi": "نصب‌کننده_MSI", ".bat": "اسکریپت_BAT_CMD", ".cmd": "اسکریپت_BAT_CMD"}[ext]
            return ["09_نرم‌افزار", "01_ویندوز", subfolder]
        if ext in ANDROID_APP_EXTS:
            return ["09_نرم‌افزار", "02_اندروید", "APK"]
        if ext in IOS_APP_EXTS:
            return ["09_نرم‌افزار", "03_iOS", "IPA"]
        if ext in LINUX_APP_EXTS:
            subfolder = {".deb": "DEB", ".rpm": "RPM", ".sh": "Shell_Script"}[ext]
            return ["09_نرم‌افزار", "04_لینوکس", subfolder]
        if ext in MAC_APP_EXTS:
            subfolder = {".dmg": "DMG", ".pkg": "PKG"}[ext]
            return ["09_نرم‌افزار", "05_مک", subfolder]

        if ext in DATABASE_EXTS:
            subfolder = "SQL" if ext == ".sql" else "SQLite" if ext in {".db", ".sqlite", ".sqlite3"} else "Access"
            return ["11_پایگاه‌داده", subfolder]
        if ext in GAME_EXTS:
            subfolder = {".unity": "Unity", ".uproject": "Unreal", ".godot": "Godot", ".sav": "Save", ".rom": "ROM"}[ext]
            return ["12_بازی", subfolder]
        if ext in OTHER_EXTS:
            subfolder = {".torrent": "تورنت", ".log": "لاگ", ".tmp": "موقت", ".bak": "پشتیبان", ".old": "پشتیبان"}[ext]
            return ["99_سایر", subfolder]
        return ["99_سایر", "سایر"]

    def _target_dir(self, parts, add_date=True):
        folder_parts = list(parts)
        date_part = self._date_folder() if add_date else None
        if date_part and not (folder_parts and self._is_date_folder(folder_parts[-1])):
            folder_parts.append(date_part)
        target = self.dest_dir.joinpath(*folder_parts)
        target.mkdir(parents=True, exist_ok=True)
        return target

    def _dest_path(self, path, parts, destination_name=None, add_date=True):
        target = self._target_dir(parts, add_date=add_date)
        filename = destination_name or path.name
        candidate = target / filename
        if not candidate.exists():
            return candidate
        file_name = Path(filename)
        counter = 1
        while True:
            candidate = target / f"{file_name.stem} ({counter}){file_name.suffix}"
            if not candidate.exists():
                return candidate
            counter += 1

    def _preview_path(self, main_parts, image_path):
        return self._dest_path(image_path, list(main_parts) + ["preview"], add_date=False)

    def _duplicate_path(self, path):
        target = self.dest_dir / "13_تکراری‌ها"
        target.mkdir(parents=True, exist_ok=True)
        candidate = target / path.name
        if not candidate.exists():
            return candidate
        counter = 1
        while True:
            candidate = target / f"{path.stem} ({counter}){path.suffix}"
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

    @staticmethod
    def _scan_pairs(files):
        pairs = {}
        for path in files:
            pairs.setdefault(path.stem.casefold(), []).append(path)
        return pairs

    def _is_duplicate(self, sha256):
        return not self.reprocess_archived and self.db.has_sha256(sha256)

    def _handle_duplicate(self, path, sha256, label="Duplicate"):
        self.db.insert_duplicate(str(path), sha256)
        if not self.quarantine_duplicates:
            self.log.emit(f"{label} skipped: {path}")
            return
        try:
            target = self._duplicate_path(path)
            shutil.move(str(path), str(target))
            self.log.emit(f"{label} moved to quarantine: {path.name} -> {target}")
        except Exception as error:
            self.log.emit(f"{label} detected, but could not move it: {path} | {error}")

    def _mark_progress(self, index, total):
        self.progress.emit(int(index * 100 / max(total, 1)))

    def _archive_main_file(self, path, paired_image=None):
        md5, sha256 = FileAnalyzer.hash_file(path)
        metadata = FileAnalyzer.basic_metadata(path)
        if self._is_duplicate(sha256):
            self._handle_duplicate(path, sha256)
            return self._main_folder_for(path, paired_image=paired_image)

        audio_hint = AudioAnalyzer.analyze(path) if path.suffix.lower() in AUDIO_EXTS and self._is_focused("audio") else None
        parts = self._main_folder_for(path, audio_hint=audio_hint, paired_image=paired_image)
        destination_name = AudioAnalyzer.destination_filename(path, audio_hint) if audio_hint else path.name
        destination = self._dest_path(path, parts, destination_name, add_date=False)
        self._copy_or_move(path, destination)
        record = {"type": "main", **metadata}
        if audio_hint:
            record["audio"] = audio_hint
            self.log.emit(f"Archived audio: {path.name} -> {destination} | {audio_hint.get('kind', 'music')}")
        else:
            self.log.emit(f"Archived main: {path.name} -> {destination}")
        self.db.insert_file(str(path), str(destination), md5, sha256, metadata["size"], metadata["mtime"], metadata["mime"], record)
        return parts

    def _archive_paired_image(self, image_path, main_parts, main_file):
        md5, sha256 = FileAnalyzer.hash_file(image_path)
        metadata = FileAnalyzer.basic_metadata(image_path)
        if self._is_duplicate(sha256):
            self._handle_duplicate(image_path, sha256, "Duplicate companion image")
            return

        if main_file.suffix.lower() in VECTOR_EXTS:
            destination = self._dest_path(image_path, main_parts, add_date=False)
            record_type = "paired_graphic_image"
            label = "Archived paired graphic image"
        else:
            destination = self._preview_path(main_parts, image_path)
            record_type = "preview"
            label = "Archived preview"
        self._copy_or_move(image_path, destination)
        self.db.insert_file(str(image_path), str(destination), md5, sha256, metadata["size"], metadata["mtime"], metadata["mime"], {"type": record_type, "paired_with": str(main_file), **metadata})
        self.log.emit(f"{label}: {image_path.name} -> {destination}")

    def _classify_image(self, image_path):
        if not self._is_focused("images"):
            return {"category": "unclassified", "subcategory": "other", "confidence": 0.0, "reason": "Initial transfer: image detail is disabled"}

        filename_hint = self.gemma.quick_classify_image(image_path)
        if float(filename_hint.get("confidence", 0) or 0) >= 0.5:
            return filename_hint
        fast_hint = self.fast_image.analyze(image_path)
        if float(fast_hint.get("confidence", 0) or 0) >= 0.5:
            return fast_hint
        if self.content_analysis and self.gemma_available and "images" in self.focus_types:
            return self.gemma.analyze_image_detailed(image_path)
        return {"category": "unclassified", "subcategory": "other", "confidence": 0.0, "reason": "Fast mode: moved to unclassified"}

    def _archive_image(self, image_path):
        md5, sha256 = FileAnalyzer.hash_file(image_path)
        metadata = FileAnalyzer.basic_metadata(image_path)
        if self._is_duplicate(sha256):
            self._handle_duplicate(image_path, sha256)
            return
        if self.project_config:
            hint = {"reason": "Project mode"}
            parts, add_date = self._project_parts(image_path), False
        else:
            hint = self._classify_image(image_path)
            parts, add_date = self._image_parts(image_path, hint)
        destination = self._dest_path(image_path, parts, add_date=add_date)
        self._copy_or_move(image_path, destination)
        self.db.insert_file(str(image_path), str(destination), md5, sha256, metadata["size"], metadata["mtime"], metadata["mime"], {"type": "image", "analysis": hint, **metadata})
        self.log.emit(f"Archived image: {image_path.name} -> {destination} | {hint.get('reason', '')}")

    def run(self):
        try:
            self._validate_paths()
            mode = "MOVE (source files will be deleted after successful copy)" if self.move_mode else "COPY (source files will be retained)"
            focus = ", ".join(sorted(self.focus_types)) if self.focus_types else "none"
            self.log.emit(f"Processing mode: {mode}")
            if self.project_config:
                self.log.emit(f"Project mode: {self.project_config.get('name', 'پروژه_بدون_نام')}")
            else:
                self.log.emit("Mode: fast transfer to final category headers" if self.quick_transfer else f"Detailed focus: {focus}")
            if self.reprocess_archived:
                self.log.emit("Reprocess mode is enabled: files already in history will be processed again.")
            elif self.quarantine_duplicates:
                self.log.emit("Exact SHA-256 duplicates will be moved to 13_تکراری‌ها.")

            if self.content_analysis and ({"images", "graphics"} & self.focus_types):
                self.log.emit("Checking Gemma Vision service for unclassified images/graphics...")
                self.gemma_available = self.gemma.is_available()
                self.log.emit("Gemma Vision is ready for unclassified images." if self.gemma_available else "Gemma unavailable; unknown images will remain unclassified without waiting.")

            if self.db.legacy_files_table:
                self.log.emit(f"Old database table preserved as {self.db.legacy_files_table}; a new compatible table was created.")

            files = [path for path in self.source_dir.rglob("*") if path.is_file()]
            total = max(len(files), 1)
            processed = set()
            index = 0
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
                        companion = images[0] if main_file.suffix.lower() in VECTOR_EXTS and images else None
                        main_parts = self._archive_main_file(main_file, paired_image=companion)
                        index += 1
                        self._mark_progress(index, total)

                        for image_path in images:
                            if image_path in processed:
                                continue
                            processed.add(image_path)
                            if not self._wait():
                                break
                            self._archive_paired_image(image_path, main_parts, main_file)
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
