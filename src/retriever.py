"""
Hybrid Knowledge Retriever for AppleSupport Historical Resolutions.
Implements fast BM25 / TF-IDF scoring with intent pre-filtering using standard library.
"""

import json
import math
import re
from typing import List, Dict, Tuple, Optional
from src.models import HistoricalResolution

def tokenize(text: str) -> List[str]:
    """Tokenize and normalize text."""
    text = text.lower()
    tokens = re.findall(r'\b[a-z0-9_]+\b', text)
    stopwords = {
        "a", "an", "and", "are", "as", "at", "be", "by", "for", "from",
        "has", "he", "in", "is", "it", "its", "of", "on", "that", "the",
        "to", "was", "were", "will", "with", "my", "me", "i", "you", "your"
    }
    return [t for t in tokens if t not in stopwords]

class ResolutionRetriever:
    def __init__(self, data_path: str = "data/historical_resolutions.jsonl"):
        self.resolutions: List[HistoricalResolution] = []
        self.doc_tokens: List[List[str]] = []
        self.doc_freq: Dict[str, int] = {}
        self.avg_doc_len: float = 0.0
        self.k1 = 1.5
        self.b = 0.75
        self._load_and_index(data_path)

    def _load_and_index(self, data_path: str):
        with open(data_path, "r", encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                d = json.loads(line)
                res = HistoricalResolution(
                    resolution_id=d["resolution_id"],
                    customer_query=d["customer_query"],
                    brand_reply=d["brand_reply"],
                    intent=d["intent"],
                    action_type=d["action_type"],
                    official_link=d.get("official_link")
                )
                self.resolutions.append(res)
                
                # Index both query and reply tokens
                tokens = tokenize(res.customer_query + " " + res.brand_reply)
                self.doc_tokens.append(tokens)
                
                seen = set(tokens)
                for term in seen:
                    self.doc_freq[term] = self.doc_freq.get(term, 0) + 1

        total_docs = len(self.doc_tokens)
        if total_docs > 0:
            self.avg_doc_len = sum(len(d) for d in self.doc_tokens) / total_docs

    def retrieve(self, query: str, intent_filter: Optional[str] = None, top_k: int = 3) -> List[Tuple[HistoricalResolution, float]]:
        """
        Retrieves top_k relevant historical resolutions using BM25 scoring.
        Applies intent pre-filtering or intent score boosting.
        """
        query_tokens = tokenize(query)
        if not query_tokens:
            return [(self.resolutions[0], 0.1)] if self.resolutions else []

        scores: List[Tuple[int, float]] = []
        total_docs = len(self.resolutions)

        for i, (res, tokens) in enumerate(zip(self.resolutions, self.doc_tokens)):
            # Optional intent matching boost
            intent_boost = 1.3 if (intent_filter and res.intent == intent_filter) else 1.0
            
            score = 0.0
            doc_len = len(tokens)
            for qt in query_tokens:
                if qt not in self.doc_freq:
                    continue
                df = self.doc_freq[qt]
                idf = math.log((total_docs - df + 0.5) / (df + 0.5) + 1.0)
                tf = tokens.count(qt)
                numerator = tf * (self.k1 + 1.0)
                denominator = tf + self.k1 * (1.0 - self.b + self.b * (doc_len / (self.avg_doc_len or 1.0)))
                score += idf * (numerator / denominator)

            total_score = score * intent_boost
            scores.append((i, total_score))

        scores.sort(key=lambda x: x[1], reverse=True)
        results = []
        for idx, s in scores[:top_k]:
            results.append((self.resolutions[idx], s))
        return results
