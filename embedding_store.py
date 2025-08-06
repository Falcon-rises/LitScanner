import faiss
import numpy as np
from transformers import AutoTokenizer, AutoModel
from sqlalchemy.orm import Session
from models import Paper

# Load sentence embedding model
tokenizer = AutoTokenizer.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")
model = AutoModel.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")

def compute_embedding(text: str) -> np.ndarray:
    """
    Compute embedding for a given text.
    """
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True)
    with torch.no_grad():
        outputs = model(**inputs)
    embedding = outputs.last_hidden_state.mean(dim=1).squeeze().numpy()
    return embedding.astype("float32")

def build_faiss_index(db: Session):
    """
    Build FAISS index for all papers.
    """
    papers = db.query(Paper).filter(Paper.summary != None).all()
    if not papers:
        return None, None

    embeddings = []
    ids = []

    for paper in papers:
        if paper.embedding:
            vec = np.frombuffer(paper.embedding, dtype=np.float32)
        else:
            vec = compute_embedding(paper.summary or paper.abstract)
            paper.embedding = vec.tobytes()
        embeddings.append(vec)
        ids.append(paper.id)

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
    results = [{"paper_id": ids[i], "score": float(dist)} for dist, i in zip(distances[0], indices[0])]
    return results
