"""
knowledge/kb_retriever.py

Real, working retrieval using TF-IDF + cosine similarity (scikit-learn) --
this needs no downloaded model and no internet access, so unlike the ASR/
vision legs, this is NOT simulated. For a production system with a much
larger knowledge base you'd upgrade to dense embeddings + pgvector (see the
full 12-week guide), but TF-IDF retrieval over a small, real corpus is a
legitimate, honest baseline that genuinely works.
"""
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from knowledge.kb_docs import KB_DOCS

_topics = list(KB_DOCS.keys())
_texts = list(KB_DOCS.values())
_vectorizer = TfidfVectorizer(stop_words="english")
_doc_matrix = _vectorizer.fit_transform(_texts)


def retrieve(query: str, top_k: int = 1) -> list[dict]:
    """Returns the top-k KB matches with a genuine cosine-similarity confidence score."""
    query_vec = _vectorizer.transform([query])
    sims = cosine_similarity(query_vec, _doc_matrix)[0]
    ranked = sorted(zip(_topics, _texts, sims), key=lambda x: -x[2])[:top_k]
    return [{"topic": topic, "text": text, "confidence": round(float(sim), 3)}
            for topic, text, sim in ranked]
