# backend/retrieval.py
from typing import List, Dict
import re
from difflib import SequenceMatcher

from chromadb import Client
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer

import config


def fuzzy_similarity(s1: str, s2: str) -> float:
    """
    Calculate fuzzy similarity between two strings (0.0 to 1.0).
    Uses SequenceMatcher for quick fuzzy matching.
    """
    return SequenceMatcher(None, s1.lower(), s2.lower()).ratio()


def simple_bm25_like_score(query: str, doc: str) -> float:
    """
    Enhanced BM25-like score with fuzzy matching support.
    """
    q_terms = re.findall(r"\w+", query.lower())
    d_terms = re.findall(r"\w+", doc.lower())
    
    if not q_terms or not d_terms:
        return 0.0
    
    # Exact matches
    q_set = set(q_terms)
    d_set = set(d_terms)
    exact_matches = len(q_set & d_set)
    
    # Fuzzy matches for terms not exactly matched
    fuzzy_score = 0.0
    unmatched_q = q_set - d_set
    
    for q_term in unmatched_q:
        # Find best fuzzy match in doc
        best_match = 0.0
        for d_term in d_set:
            if len(q_term) >= 4 and len(d_term) >= 4:  # Only fuzzy match longer terms
                similarity = fuzzy_similarity(q_term, d_term)
                if similarity > 0.8:  # High threshold for fuzzy matches
                    best_match = max(best_match, similarity * 0.5)  # Weight fuzzy matches lower
        fuzzy_score += best_match
    
    # Combined score
    total_score = (exact_matches + fuzzy_score) / (len(q_set) ** 0.5)
    return total_score


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
        """
        Expand query with common synonyms and variations.
        This helps with semantic matching without calling the LLM.
        """
        expanded = [q]
        
        # Common educational synonyms mapping
        synonym_map = {
            'learn': ['study', 'understand', 'grasp'],
            'study': ['learn', 'review', 'practice'],
            'exam': ['test', 'assessment', 'quiz'],
            'test': ['exam', 'assessment', 'quiz'],
            'homework': ['assignment', 'task', 'work'],
            'assignment': ['homework', 'task', 'work'],
            'explain': ['describe', 'clarify', 'define'],
            'describe': ['explain', 'clarify', 'define'],
            'help': ['assist', 'support', 'aid'],
            'understand': ['comprehend', 'grasp', 'learn'],
        }
        
        # Extract key terms from query
        q_lower = q.lower()
        q_terms = re.findall(r"\w+", q_lower)
        
        # Check if any synonym triggers exist
        for term in q_terms:
            if term in synonym_map:
                # Create a variant with the first synonym
                synonyms = synonym_map[term]
                if synonyms:
                    # Replace first occurrence only
                    variant = re.sub(r'\b' + re.escape(term) + r'\b', synonyms[0], q_lower, count=1)
                    if variant != q_lower and variant not in expanded:
                        expanded.append(variant)
                        break  # Only add one variant to keep it fast
        
        return expanded

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


