"""Controlled, editable taxonomy for ArchivePro.

Folders are created only from known rules or user-approved rules in taxonomy.json.
"""

import json
from pathlib import Path


DEFAULT_RULES = [
    {"domain": "images", "aliases": ["sandwich", "ساندویچ", "club sandwich"], "path": ["01_تصاویر", "غذا", "فست‌فود", "ساندویچ"]},
    {"domain": "images", "aliases": ["pizza", "پیتزا"], "path": ["01_تصاویر", "غذا", "فست‌فود", "پیتزا"]},
    {"domain": "images", "aliases": ["burger", "hamburger", "برگر", "همبرگر"], "path": ["01_تصاویر", "غذا", "فست‌فود", "برگر"]},
    {"domain": "images", "aliases": ["hot dog", "hotdog", "هات داگ"], "path": ["01_تصاویر", "غذا", "فست‌فود", "هات‌داگ"]},
    {"domain": "images", "aliases": ["kebab", "کباب"], "path": ["01_تصاویر", "غذا", "ایرانی", "کباب"]},
    {"domain": "images", "aliases": ["cake", "کیک"], "path": ["01_تصاویر", "غذا", "شیرینی", "کیک"]},
    {"domain": "images", "aliases": ["coffee", "cafe", "قهوه", "کافی شاپ"], "path": ["01_تصاویر", "غذا", "نوشیدنی", "قهوه"]},
    {"domain": "images", "aliases": ["flower", "گل", "rose", "رز", "tulip", "لاله"], "path": ["01_تصاویر", "گیاه", "گل"]},
    {"domain": "images", "aliases": ["tree", "درخت"], "path": ["01_تصاویر", "گیاه", "درخت"]},
    {"domain": "images", "aliases": ["copper", "مس"], "path": ["01_تصاویر", "اشیاء", "فلزات", "مس"]},
    {"domain": "images", "aliases": ["gold", "طلا"], "path": ["01_تصاویر", "اشیاء", "فلزات", "طلا"]},
    {"domain": "images", "aliases": ["3d icon", "3d-icon", "آیکون سه بعدی"], "path": ["01_تصاویر", "سه‌بعدی", "آیکون‌های_سه‌بعدی"]},
    {"domain": "images", "aliases": ["isometric", "ایزومتریک"], "path": ["01_تصاویر", "سه‌بعدی", "ایزومتریک"]},
    {"domain": "images", "aliases": ["render", "رندر"], "path": ["01_تصاویر", "سه‌بعدی", "رندرهای_مستقل"]},
]

BROAD_FALLBACKS = {
    "food": ["01_تصاویر", "غذا", "دسته‌بندی_نشده"],
    "plant": ["01_تصاویر", "گیاه", "دسته‌بندی_نشده"],
    "animal": ["01_تصاویر", "حیوان", "دسته‌بندی_نشده"],
    "animals": ["01_تصاویر", "حیوان", "دسته‌بندی_نشده"],
    "building": ["01_تصاویر", "ساختمان", "دسته‌بندی_نشده"],
    "vehicle": ["01_تصاویر", "خودرو", "دسته‌بندی_نشده"],
    "objects": ["01_تصاویر", "اشیاء", "دسته‌بندی_نشده"],
    "object": ["01_تصاویر", "اشیاء", "دسته‌بندی_نشده"],
    "logo": ["01_تصاویر", "اشیاء", "لوگو"],
}


class TaxonomyManager:
    def __init__(self, file_path=None):
        self.file_path = Path(file_path or Path(__file__).with_name("taxonomy.json"))
        self.rules = []
        self.load()

    def load(self):
        if self.file_path.is_file():
            try:
                payload = json.loads(self.file_path.read_text(encoding="utf-8"))
                self.rules = payload.get("rules", [])
            except Exception:
                self.rules = list(DEFAULT_RULES)
        else:
            self.rules = list(DEFAULT_RULES)
            self.save()
        self._merge_defaults()

    def _merge_defaults(self):
        existing = {(rule.get("domain"), tuple(rule.get("path", []))) for rule in self.rules}
        for rule in DEFAULT_RULES:
            key = (rule["domain"], tuple(rule["path"]))
            if key not in existing:
                self.rules.append(dict(rule))

    def save(self):
        self.file_path.write_text(
            json.dumps({"version": 1, "rules": self.rules}, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    @staticmethod
    def _normalize(text):
        return " ".join(str(text or "").casefold().replace("_", " ").replace("-", " ").split())

    def resolve_image_path(self, category, terms):
        searchable = self._normalize(terms)
        matches = []
        for rule in self.rules:
            if rule.get("domain") != "images":
                continue
            for alias in rule.get("aliases", []):
                normalized_alias = self._normalize(alias)
                if normalized_alias and normalized_alias in searchable:
                    matches.append((len(normalized_alias), rule["path"]))
        if matches:
            return max(matches, key=lambda item: item[0])[1]
        return BROAD_FALLBACKS.get(str(category).lower())

    def add_rule(self, domain, path_text, aliases_text):
        path = [part.strip() for part in path_text.replace("/", "\\").split("\\") if part.strip()]
        aliases = [item.strip() for item in aliases_text.replace("؛", ",").split(",") if item.strip()]
        if not path or not aliases:
            raise ValueError("مسیر و حداقل یک نام مشابه لازم است.")
        rule = {"domain": domain, "path": path, "aliases": aliases}
        if rule not in self.rules:
            self.rules.append(rule)
            self.save()

    def tree_paths(self, domain="images"):
        return [rule["path"] for rule in self.rules if rule.get("domain") == domain]
