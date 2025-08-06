from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import uvicorn
import os
import networkx as nx

from model import Base, Paper
from crawler import crawl_papers
from summarizer import batch_summarize_with_pegasus, generate_meta_review
from topic_modeling import extract_texts_for_topic_model, build_topic_model
from citation_graph import build_citation_graph
from embedding_store import build_faiss_index, semantic_search

# Environment variables for database
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg2://username:password@localhost/research_db"
)

# Create engine and session
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Ensure tables exist
Base.metadata.create_all(bind=engine)

# Ensure data folder exists
os.makedirs("data", exist_ok=True)

# Initialize FastAPI app
app = FastAPI(title="Research Review Engine", version="2.0")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"message": "Welcome to Research Review Engine API v2"}

@app.get("/crawl")
def crawl(query: str = Query(...), limit: int = 20):
    """
    Crawl papers and store them in DB.
    """
    with SessionLocal() as db:
        papers = crawl_papers(query, limit)
        for paper in papers:
            db_paper = Paper(
                title=paper["title"],
                authors=str(paper["authors"]),
                abstract=paper["abstract"],
                url=paper["url"],
                source=paper["source"]
            )
            db.add(db_paper)
        db.commit()
        return {"message": f"Crawled and saved {len(papers)} papers"}

@app.get("/summarize")
def summarize():
    """
    Summarize papers in DB and generate a GPT meta-review.
    """
    with SessionLocal() as db:
        papers = db.query(Paper).all()
        if not papers:
            raise HTTPException(status_code=404, detail="No papers found")

        paper_dicts = [p.to_dict() for p in papers]
        summarized = batch_summarize_with_pegasus(paper_dicts)

        for i, p in enumerate(papers):
            p.summary = summarized[i]["summary"]
        db.commit()

        summaries = [p.summary for p in papers]
        meta_review = generate_meta_review(summaries)

        return {"summarized_count": len(summarized), "meta_review": meta_review}

@app.get("/topics")
def topics():
    """
    Run topic modeling and assign topics to papers.
    """
    with SessionLocal() as db:
        papers = db.query(Paper).filter(Paper.summary != None).all()
        if not papers:
            raise HTTPException(status_code=404, detail="No summarized papers found")

        texts = extract_texts_for_topic_model([p.to_dict() for p in papers])
        topic_model = build_topic_model(texts)

        topics, _ = topic_model.transform(texts)
        for i, p in enumerate(papers):
            p.topic = int(topics[i])
        db.commit()

        topic_info = topic_model.get_topic_info()
        return {"topics_count": len(topic_info), "topic_info": topic_info.to_dict()}

@app.get("/search")
def search_papers(query: str):
    """
    Semantic search for related papers.
    """
    with SessionLocal() as db:
        index, ids = build_faiss_index(db)
        if index is None:
            return {"message": "No papers available for search"}
        
        results = semantic_search(index, ids, query)
        papers = []
        for res in results:
            paper = db.get(Paper, res["paper_id"])
            if paper:
                papers.append({**paper.to_dict(), "score": res["score"]})
        return {"query": query, "results": papers}

@app.get("/citation-graph")
def citation_graph():
    """
    Generate citation graph JSON.
    """
    with SessionLocal() as db:
        papers = db.query(Paper).all()
        if not papers:
            raise HTTPException(status_code=404, detail="No papers found")

        G = build_citation_graph([p.to_dict() for p in papers])
        nodes = [{"id": n, **G.nodes[n]} for n in G.nodes()]
        edges = [{"source": u, "target": v} for u, v in G.edges()]
        nx.write_gexf(G, "data/citation_graph.gexf")

        return {"nodes": nodes, "edges": edges}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
