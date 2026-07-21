# ArchivePro v3.0

نرم‌افزار دسکتاپ آفلاین برای بایگانی و دسته‌بندی هوشمند فایل‌ها (ویندوز، PySide6).
A desktop app for smart, offline file archiving/classification (Windows, PySide6).

## اجرا / Run

```bash
pip install -r requirements.txt
python main.py
```

روی ویندوز برای OCR باید Tesseract-OCR جداگانه نصب شود و مسیرش در صورت نیاز در
`pytesseract.pytesseract.tesseract_cmd` تنظیم شود (مثلاً
`C:\Program Files\Tesseract-OCR\tesseract.exe`).

## ساخت فایل اجرایی (exe) / Build EXE

```bash
pyinstaller --noconfirm --onefile --windowed --name ArchivePro main.py
```

## ساختار پروژه / Project layout

```
main.py         رابط کاربری اصلی (۵ تب) / main UI, 5 tabs
translator.py   ترجمه فارسی/انگلیسی (پیش‌فرض انگلیسی) / i18n, default English
styles.py       تم مدرن مینیمال طوسی تیره / dark-gray minimal theme
database.py     مدیریت SQLite (تشخیص تکراری با هش) / SQLite + dedupe by hash
utils.py        هش، پاک‌سازی نام، نگاشت خواننده‌ها، پسوندها، taxonomy
classifiers.py  منطق دسته‌بندی عکس/گرافیک/صوت/نرم‌افزار
workers.py      اجرای عملیات در QThread با Pause/Safe-Stop
```

## تب‌ها / Tabs (in order)

1. **General** – Mirrors files from source(s) to destination, unchanged names/structure.
2. **Images** – Family (Shamsi date + location) / Work-content (OCR + keywords) / Combined.
3. **Graphics / Vectors** – Classifies AI/EPS/SVG/PSD/CDR/... by software, and by visual
   content using a same-name preview image (sidecar). Optional checkbox generates a small
   local preview for SVG files that lack one (AI/EPS/CDR require a dedicated renderer that
   isn't bundled, so those fall back to `Unknown_Graphics` unless a preview already exists).
4. **Audio** – Cleans track numbers & junk text, groups all songs of an artist into one
   folder (+ album sub-folder if detected). Persian/English artist naming is independent
   of the UI language (default English).
5. **Software** – Classifies installers by platform (Windows/Android/macOS/Linux/iOS) then
   by world-standard category (2D/3D design, Architecture/CAD, Microsoft/Office, ...).

## نکات مهم / Notes

- Every tab defaults to **Copy**; **Move** is copy-then-verify-then-delete-source for safety.
- **Stop** is a *safe stop*: it finishes the file currently being copied, then halts.
- Duplicate files (by SHA-256 hash) are detected against the database and skipped.
- Reports are exported as CSV into the destination folder per tab.
- Online preview-generation / online app-detection are provided as UI checkboxes (default
  off) but no network call is wired in this build — they are safe extension points if you
  later want to plug in your own vision/OCR API key.
