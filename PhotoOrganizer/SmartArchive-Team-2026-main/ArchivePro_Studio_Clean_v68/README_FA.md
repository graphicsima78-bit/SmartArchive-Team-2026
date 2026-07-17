# ArchivePro Studio v68 — ساختار یکپارچه

این بسته، کد اصلی پراکندهٔ ArchivePro را به یک ساختار واحد تبدیل می‌کند.

## کد اصلی واحد

- `main.py` — رابط کاربری Tab‌بندی‌شده
- `archiver.py` — موتور واحد دسته‌بندی
- `audio_analyzer.py` — تحلیل صوت
- `fast_image_analyzer.py` — تحلیل سبک تصویر و OCR
- `gemma_connector.py` — تحلیل محتوای دقیق با Gemma
- `taxonomy.py` و `taxonomy.json` — دسته‌بندی هوشمند و قابل ویرایش
- `photo_analyzer.py` — EXIF، Screenshot و عکس خانوادگی
- `styles.py` — چهار تم نرم‌افزار

## نکات مهم

- فایل‌های Update و Workerهای قدیمی حذف نمی‌شوند؛ به `Legacy_Updates` منتقل می‌شوند.
- `taxonomy.json` فعلی کاربر حفظ می‌شود.
- `Output`، `dist` و فایل‌های دادهٔ کاربر جابه‌جا نمی‌شوند.
- پیش از اجرا، برنامه ArchivePro را ببندید.

## اعمال

روی فایل زیر دابل‌کلیک کنید:

`Apply_ArchivePro_Studio_v68.bat`

بعد از اعمال، AutoSync تغییرات را خودکار Commit و Push می‌کند.
