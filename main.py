from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import uvicorn

from models import Base, Paper
from crawler import crawl_papers
from summarizer import batch_summarize_with_pegasus, generate_meta_review
from topic_modeling import extract_texts_for_topic_model, build_topic_model
from citation_graph import build_citation_graph
import networkx as nx

import json
import os

DATABASE_URL = "postgresql+psycopg2://username:password@localhost/research_db"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

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
    db = SessionLocal()
    try:
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
    finally:
        db.close()

@app.get("/summarize")
def summarize():
    """
    Summarize papers in DB and generate a GPT meta-review.
    """
    db = SessionLocal()
    try:
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
    finally:
        db.close()

@app.get("/topics")
def topics():
    """
    Run topic modeling and assign topics to papers.
    """
    db = SessionLocal()
    try:
        papers = db.query(Paper).filter(Paper.summary != None).all()
        texts = extract_texts_for_topic_model([p.to_dict() for p in papers])
        topic_model = build_topic_model(texts)

        topics, _ = topic_model.transform(texts)
        for i, p in enumerate(papers):
            p.topic = int(topics[i])
        db.commit()

        topic_info = topic_model.get_topic_info()
        return {"topics_count": len(topic_info), "topic_info": topic_info.to_dict()}
    finally:
        db.close()

@app.get("/citation-graph")
def citation_graph():
    """
    Generate citation graph JSON.
    """
    db = SessionLocal()
    try:
        papers = db.query(Paper).all()
        G = build_citation_graph([p.to_dict() for p in papers])
        nodes = [{"id": n, **G.nodes[n]} for n in G.nodes()]
        edges = [{"source": u, "target": v} for u, v in G.edges()]
        nx.write_gexf(G, "data/citation_graph.gexf")

        return {"nodes": nodes, "edges": edges}
    finally:
        db.close()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
