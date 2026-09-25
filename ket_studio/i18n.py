"""Shared, offline language catalogues; preferences never modify learning data."""

import json
import re
from functools import lru_cache
from pathlib import Path
from .paths import PACKAGE_DIR

LOCALES = ("en", "zh-CN", "zh-HK")
LANGUAGE_NAMES = {"en": "English", "zh-CN": "简体中文", "zh-HK": "繁体中文"}


@lru_cache(maxsize=3)
def catalogue(locale):
    return json.loads(
        (PACKAGE_DIR.parent / "site/locales" / f"{locale}.json").read_text(
            encoding="utf-8"
        )
    )


class Translator:
    def __init__(self, locale="en", preferences=None):
        self.preferences = Path(preferences) if preferences else None
        if self.preferences:
            try:
                locale = json.loads(self.preferences.read_text(encoding="utf-8")).get(
                    "language", "en"
                )
            except (OSError, ValueError, AttributeError):
                locale = "en"
        self.locale = locale if locale in LOCALES else "en"

    def text(self, message, *args):
        message = str(message)
        data = catalogue(self.locale)
        translated = data["messages"].get(message, data["categories"].get(message))
        if translated is None and not args:
            for source, target in data["messages"].items():
                if "{0}" not in source:
                    continue
                pattern = "".join(
                    "(.+?)" if re.fullmatch(r"\{\d+\}", part) else re.escape(part)
                    for part in re.split(r"(\{\d+\})", source)
                )
                match = re.fullmatch(pattern, message, re.DOTALL)
                if match:
                    translated = target
                    args = tuple(
                        data["messages"].get(value, value) for value in match.groups()
                    )
                    break
        translated = (
            translated
            if translated is not None
            else catalogue("en")["messages"].get(message, message)
        )
        return re.sub(
            r"\{(\d+)\}",
            lambda m: str(args[int(m[1])]) if int(m[1]) < len(args) else m[0],
            translated,
        )

    def category(self, value):
        return catalogue(self.locale)["categories"].get(value, value)

    def meaning(self, value):
        return catalogue(self.locale)["prompts"].get(value, value)

    def select(self, locale):
        if locale not in LOCALES:
            raise ValueError("Unsupported locale")
        self.locale = locale
        if self.preferences:
            try:
                self.preferences.parent.mkdir(parents=True, exist_ok=True)
                temporary = self.preferences.with_suffix(".json.tmp")
                temporary.write_text(json.dumps({"language": locale}), encoding="utf-8")
                temporary.replace(self.preferences)
            except OSError:
                return False
        return True
