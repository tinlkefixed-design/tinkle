from __future__ import annotations
import math
import re
from collections import Counter, defaultdict
from dataclasses import dataclass

@dataclass(frozen=True)
class RetrievalHit:
    item_id: str
    score: float

class BM25Index:
    """Small dependency-free lexical retrieval index.

    This is the deterministic baseline. It is intentionally not mislabeled as
    semantic embeddings; a vector backend can be attached through the same
    interface later.
    """
    def __init__(self) -> None:
        self._docs: dict[str, list[str]] = {}
        self._df: Counter[str] = Counter()
        self._avgdl = 0.0

    @staticmethod
    def tokens(text: str) -> list[str]:
        return re.findall(r"\b[\w-]+\b", text.lower())

    def upsert(self, item_id: str, text: str) -> None:
        if item_id in self._docs:
            old = self._docs.pop(item_id)
            for token in set(old):
                self._df[token] -= 1
        tokens = self.tokens(text)
        self._docs[item_id] = tokens
        for token in set(tokens):
            self._df[token] += 1
        self._avgdl = sum(map(len, self._docs.values())) / max(len(self._docs), 1)

    def search(self, query: str, limit: int = 5) -> list[RetrievalHit]:
        q = self.tokens(query)
        if not q or not self._docs:
            return []
        n = len(self._docs)
        k1, b = 1.5, 0.75
        results: list[RetrievalHit] = []
        for item_id, tokens in self._docs.items():
            tf = Counter(tokens)
            score = 0.0
            dl = len(tokens)
            for term in q:
                if term not in tf:
                    continue
                df = self._df[term]
                idf = math.log(1.0 + (n - df + 0.5) / (df + 0.5))
                denom = tf[term] + k1 * (1 - b + b * dl / max(self._avgdl, 1.0))
                score += idf * tf[term] * (k1 + 1) / denom
            if score > 0:
                results.append(RetrievalHit(item_id, score))
        results.sort(key=lambda x: (-x.score, x.item_id))
        return results[:limit]
