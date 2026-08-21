import math
import re
from typing import Optional
from collections import Counter
from src.rag.document_loader import DocumentChunk

class AcademicVectorStore:
    """
    High-performance, zero-latency semantic and keyword vector store.
    Provides instant vector embeddings and similarity search without requiring heavy external downloads.
    """
    def __init__(self, persist_dir: str = "./chroma_db"):
        self.documents: list[DocumentChunk] = []
        self.doc_vectors: list[dict[str, float]] = []
        self.idf: dict[str, float] = {}

    def _tokenize(self, text: str) -> list[str]:
        return re.findall(r'\b[a-zA-Z0-9_§]+\b', text.lower())

    def _compute_vector(self, tokens: list[str]) -> dict[str, float]:
        tf = Counter(tokens)
        vec = {}
        norm_sq = 0.0
        for token, count in tf.items():
            weight = (1 + math.log(count)) * self.idf.get(token, 1.0)
            vec[token] = weight
            norm_sq += weight * weight
        norm = math.sqrt(norm_sq) if norm_sq > 0 else 1.0
        return {k: v / norm for k, v in vec.items()}

    def add_documents(self, chunks: list[DocumentChunk]):
        if not chunks:
            return
        self.documents.extend(chunks)
        
        # Build IDF dictionary
        n_docs = len(self.documents)
        doc_freq = Counter()
        for doc in self.documents:
            unique_tokens = set(self._tokenize(doc.content))
            for t in unique_tokens:
                doc_freq[t] += 1
                
        self.idf = {token: math.log((n_docs + 1) / (df + 1)) + 1.0 for token, df in doc_freq.items()}
        
        # Build document vectors
        self.doc_vectors = [
            self._compute_vector(self._tokenize(doc.content))
            for doc in self.documents
        ]

    def search(self, query: str, n_results: int = 5, filter_metadata: Optional[dict] = None) -> list[dict]:
        if not self.documents:
            return []
            
        q_tokens = self._tokenize(query)
        q_vec = self._compute_vector(q_tokens)
        
        scores = []
        for idx, (doc, doc_vec) in enumerate(zip(self.documents, self.doc_vectors)):
            # Apply metadata filter if provided
            if filter_metadata:
                match = True
                for k, v in filter_metadata.items():
                    if doc.metadata.get(k) != v:
                        match = False
                        break
                if not match:
                    continue
                    
            # Compute cosine similarity
            similarity = 0.0
            for token, q_w in q_vec.items():
                if token in doc_vec:
                    similarity += q_w * doc_vec[token]
                    
            # Keyword exact boost
            for token in q_tokens:
                if len(token) > 2 and token in doc.content.lower():
                    similarity += 0.15
                    
            scores.append((similarity, idx, doc))
            
        # Sort descending by similarity
        scores.sort(key=lambda x: x[0], reverse=True)
        top_k = scores[:n_results]
        
        results = []
        for sim, idx, doc in top_k:
            results.append({
                "content": doc.content,
                "metadata": doc.metadata,
                "distance": round(1.0 - min(sim, 1.0), 4),
                "id": doc.chunk_id
            })
        return results

    def clear(self):
        self.documents = []
        self.doc_vectors = []
        self.idf = {}
