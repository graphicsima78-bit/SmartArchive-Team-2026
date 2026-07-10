# ArchivePro Image Analyzer Module
# Developed by Majid Dehaki

from typing import List, Dict

class ImageAnalyzer:
    """تحلیل برچسب‌های هوش مصنوعی و انتخاب بهترین دسته برای پوشه‌بندی [165، 180]"""

    # کلمات کلیدی برای نگاشت هوشمند برچسب‌ها به پوشه‌ها [179، 180]
    MATERIAL_KEYWORDS = ['wood', 'stone', 'metal', 'fabric', 'glass', 'brick', 'plaster', 'wallpaper', 'texture']
    FOOD_KEYWORDS = ['food', 'dish', 'meal', 'pizza', 'burger', 'cake', 'ice_cream', 'sweet', 'fruit', 'vegetable']
    BUILDING_KEYWORDS = ['building', 'skyscraper', 'house', 'mosque', 'church', 'temple', 'palace', 'castle', 'bridge']
    VEHICLE_KEYWORDS = ['car', 'motorcycle', 'truck', 'bus', 'plane', 'helicopter', 'boat', 'ship', 'bicycle']
    
    # نقشه‌ی خانواده‌های برچسب برای دسته‌بندی دقیق‌تر [180، 206]
    FAMILY_MAP = {
        'animal': ['dog', 'cat', 'horse', 'cow', 'lion', 'bird', 'fish', 'dolphin', 'insect', 'butterfly', 'ant'],
        'landscape': ['sea', 'mountain', 'forest', 'desert', 'river', 'waterfall', 'cityscape', 'nature', 'sky', 'night'],
        'objects': ['plate', 'cup', 'bowl', 'spoon', 'fork', 'table', 'chair', 'phone', 'computer', 'book', 'toy', 'clothing']
    }

    @staticmethod
    def get_best_category(top_labels: List[str]) -> str:
        """
        دریافت ۵ برچسب برتر از ResNet50 و تعیین بهترین دسته‌ی فارسی [1]
        """
        # تبدیل تمام برچسب‌ها به حروف کوچک برای جستجوی دقیق
        labels = [label.lower() for label in top_labels]
        
        # ۱. بررسی دسته‌ی انسان (در صورت وجود کلمات مرتبط)
        if any(word in labels for word in ['person', 'man', 'woman', 'child', 'face']):
            return "تصاویر/انسان"

        # ۲. بررسی دسته‌ی حیوانات
        for label in labels:
            if any(animal in label for animal in ImageAnalyzer.FAMILY_MAP['animal']):
                return "تصاویر/حیوان"

        # ۳. بررسی دسته‌ی غذا
        for label in labels:
            if any(food in label for food in ImageAnalyzer.FOOD_KEYWORDS):
                return "تصاویر/غذا"

        # ۴. بررسی دسته‌ی خودرو و وسایل نقلیه
        for label in labels:
            if any(v in label for v in ImageAnalyzer.VEHICLE_KEYWORDS):
                return "تصاویر/خودرو"

        # ۵. بررسی دسته‌ی ساختمان و معماری
        for label in labels:
            if any(b in label for b in ImageAnalyzer.BUILDING_KEYWORDS):
                return "تصاویر/ساختمان"

        # ۶. بررسی دسته‌ی مناظر
        for label in labels:
            if any(land in label for land in ImageAnalyzer.FAMILY_MAP['landscape']):
                return "تصاویر/منظره"

        # ۷. بررسی دسته‌ی تکسچر و متریال
        for label in labels:
            if any(m in label for m in ImageAnalyzer.MATERIAL_KEYWORDS):
                return "تصاویر/تکسچر"

        # ۸. بررسی دسته‌ی اشیاء
        for label in labels:
            if any(obj in label for obj in ImageAnalyzer.FAMILY_MAP['objects']):
                return "تصاویر/اشیاء"

        # اگر هیچکدام پیدا نشد
        return "تصاویر/سایر"
