# backend/retrieval.py
from typing import List, Dict
import re

from chromadb import Client
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer

import config


def simple_bm25_like_score(query: str, doc: str) -> float:
    q = set(re.findall(r"\w+", query.lower()))
    d = set(re.findall(r"\w+", doc.lower()))
    if not q or not d:
        return 0.0
    inter = len(q & d)
    # light BM25-ish score (no IDF), good enough for re-rank boost
    return inter / (len(q) ** 0.5)


class Retriever:
    def __init__(self):
        # Must match ingest settings so we read the same persisted DB
        self.client = Client(
            Settings(
                persist_directory=str(config.DATA_DIR),
                allow_reset=True,
                is_persistent=True,
            )
        )
        self.collection = self.client.get_or_create_collection("edumate")
        # Use SAME embedding lib/model as ingest
        self.embedder = SentenceTransformer(config.EMBEDDING_MODEL)

    def expand_queries(self, q: str, model_call) -> List[str]:
        # Keep simple (no LLM calls) while stabilising
        return [q]

    def retrieve(self, query: str, model_call) -> List[Dict]:
        queries = self.expand_queries(query, model_call)

        candidates: List[Dict] = []
        for q in queries:
            e = self.embedder.encode(q).tolist()
            res = self.collection.query(
                query_embeddings=[e],
                n_results=max(1, config.TOP_K),
                include=["documents", "metadatas"],
            )
            ids = res.get("ids", [[]])[0]
            docs = res.get("documents", [[]])[0]
            metas = res.get("metadatas", [[]])[0]

            for i, d in enumerate(docs):
                # guard against empty returns
                if i < len(ids) and i < len(metas):
                    candidates.append({"id": ids[i], "doc": d, "meta": metas[i]})

        # Deduplicate by id
        seen, dedup = set(), []
        for r in candidates:
            if r["id"] in seen:
                continue
            seen.add(r["id"])
            dedup.append(r)

        # Light BM25-like re-rank
        for r in dedup:
            r["bm25"] = simple_bm25_like_score(query, r["doc"])
            r["score"] = r["bm25"] * config.BM25_WEIGHT

        dedup.sort(key=lambda x: x["score"], reverse=True)
        results = dedup[: config.TOP_K]
        
        # In Fast Mode, trim context to MAX_CONTEXT_CHARS
        if config.FAST_MODE and config.MAX_CONTEXT_CHARS:
            total_chars = 0
            trimmed_results = []
            for r in results:
                doc_len = len(r["doc"])
                if total_chars + doc_len <= config.MAX_CONTEXT_CHARS:
                    trimmed_results.append(r)
                    total_chars += doc_len
                elif total_chars < config.MAX_CONTEXT_CHARS:
                    # Partial include to reach limit
                    remaining = config.MAX_CONTEXT_CHARS - total_chars
                    r["doc"] = r["doc"][:remaining]
                    trimmed_results.append(r)
                    break
            return trimmed_results
        
        return results


