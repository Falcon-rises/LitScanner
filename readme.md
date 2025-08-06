# LitScanner – Research Review Engine

LitScanner is a web app that automatically crawls, summarizes, and analyzes thousands of research papers using NLP and visualization tools.

---

## 🚀 Features
- ✅ Crawl papers from Google Scholar and Arxiv  
- ✅ Summarize using Pegasus + GPT hybrid  
- ✅ Semantic search with FAISS embeddings  
- ✅ Topic modeling with BERTopic  
- ✅ Citation graph visualization  
- ✅ React + Tailwind frontend  

---

## 🛠️ Backend Setup

```bash
pip install -r requirements.txt
python -m spacy download en_core_web_sm
createdb research_db
uvicorn main:app --reload
