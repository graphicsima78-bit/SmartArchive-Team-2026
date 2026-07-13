# ArchivePro Text Analyzer Module
# Developed by Majid Dehaki

class TextAnalyzer:
    """تحلیل متون استخراج شده از اسناد و تشخیص نوع دقیق سند برای پوشه‌بندی [165، 180]"""

    # دیکشنری کلمات کلیدی برای تشخیص هوشمند نوع سند [180، 208]
    DOC_TYPES = {
        'فاکتور': ['فاکتور', 'صورتحساب', 'invoice', 'bill', 'receipt', 'مبلغ کل', 'قیمت واحد', 'شرح کالا'],
        'قرارداد': ['قرارداد', 'تعهدنامه', 'تفاهم‌نامه', 'contract', 'agreement', 'طرف اول', 'ماده', 'تبصره'],
        'نامه': ['نامه', 'احتراماً', 'به استحضار می‌رساند', 'جناب آقای', 'سرکار خانم', 'letter', 'subject'],
        'مدارک': ['کارت ملی', 'شناسنامه', 'گواهینامه', 'پاسپورت', 'passport', 'id card', 'melli'],
        'گزارش': ['گزارش نهایی', 'تحلیل', 'نتیجه بررسی', 'report', 'analysis', 'summary', 'آمار']
    }

    @staticmethod
    def classify(text: str) -> str:
        """
        بررسی متن دریافتی و تعیین بهترین زیرشاخه در پوشه اسناد [1]
        """
        if not text:
            return "اسناد/متنی"

        # تبدیل متن به حروف کوچک برای بررسی کلمات کلیدی انگلیسی
        text_content = text.lower()

        # بررسی وجود کلمات کلیدی هر دسته در متن [2]
        for category, keywords in TextAnalyzer.DOC_TYPES.items():
            if any(keyword in text_content for keyword in keywords):
                # بر اساس ساختار درختی درخواستی شما در پوشه تصاویر/اسناد [2]
                return f"تصاویر/اسناد/{category}"

        # اگر کلمه‌ی خاصی پیدا نشد، در پوشه عمومی اسناد قرار بگیرد
        return "اسناد/متنی"
