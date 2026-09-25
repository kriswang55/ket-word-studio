"""Validated word bank and shared answer normalization."""

import json
import unicodedata
from .paths import PACKAGE_DIR


def normalize(value: str) -> str:
    return " ".join(unicodedata.normalize("NFKC", value).casefold().split())


class Vocabulary:
    def __init__(self, path=None, words=None):
        self.words = (
            words
            if words is not None
            else json.loads(
                (path or PACKAGE_DIR.parent / "site/data/words.json").read_text(
                    encoding="utf-8"
                )
            )
        )
        self.by_id = {}
        for word in self.words:
            if not all(
                isinstance(word.get(k), str) and word[k].strip()
                for k in ("id", "english", "chinese", "category")
            ):
                raise ValueError("词库存在空字段或无效词条")
            if word["id"] in self.by_id:
                raise ValueError("词库 ID 重复")
            self.by_id[word["id"]] = word
        self.categories = list(dict.fromkeys(w["category"] for w in self.words))

    def search(self, query="", category="全部主题"):
        query = normalize(query)
        return [
            w
            for w in self.words
            if (category == "全部主题" or w["category"] == category)
            and (not query or query in normalize(w["english"] + " " + w["chinese"]))
        ]

    @staticmethod
    def matches(word, answer):
        return normalize(answer) in {
            normalize(x) for x in [word["english"], *word.get("aliases", [])]
        }
