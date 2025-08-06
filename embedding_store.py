import faiss
import numpy as np
import torch
from transformers import AutoTokenizer, AutoModel
from sqlalchemy.orm import Session
from model import Paper  # Ensure this matches your file name (model.py)

# Load sentence embedding model
tokenizer = AutoTokenizer.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")
model = AutoModel.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")
model.eval()  # Set model to evaluation mode

def compute_embedding(text: str) -> np.ndarray:
    """
    Compute embedding for a given text using MiniLM.
    """
    if not text:
        text = " "  # Prevent tokenizer errors
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True)
    with torch.no_grad():
        outputs = model(**inputs)
    embedding = outputs.last_hidden_state.mean(dim=1).squeeze().numpy()
    return embedding.astype("float32")

def build_faiss_index(db: Session):
    """
    Build FAISS index for all summarized papers.
    """
    papers = db.query(Paper).filter(Paper.summary != None).all()
    if not papers:
        return None, None

    embeddings = []
    ids = []

    for paper in papers:
        try:
            if paper.embedding:
                vec = np.frombuffer(paper.embedding, dtype=np.float32)
            else:
                vec = compute_embedding(paper.summary or paper.abstract)
                paper.embedding = vec.tobytes()
            embeddings.append(vec)
            ids.append(paper.id)
        except Exception as e:
            print(f"⚠️ Skipping paper {paper.id} due to error: {e}")

    if not embeddings:
        return None, None

    db.commit()

    embeddings = np.vstack(embeddings)
    index = faiss.IndexFlatL2(embeddings.shape[1])
    index.add(embeddings)

    return index, ids

def semantic_search(index, ids, query: str, top_k: int = 5):
    """
    Perform semantic search for similar papers.
    """
    query_vec = compute_embedding(query).reshape(1, -1)
    distances, indices = index.search(query_vec, top_k)

    results = []
    for dist, i in zip(distances[0], indices[0]):
        if i < len(ids):  # Safety check
            results.append({"paper_id": ids[i], "score": float(dist)})

    return results

