import requests
from bs4 import BeautifulSoup
from scholarly import scholarly
import arxiv
import json
from typing import List, Dict

# ---------- GOOGLE SCHOLAR SCRAPER ----------
def crawl_google_scholar(query: str, limit: int = 20) -> List[Dict]:
    """
    Search Google Scholar using scholarly library.
    """
    results = []
    search = scholarly.search_pubs(query)
    
    for i in range(limit):
        try:
            paper = next(search)
            results.append({
                "title": paper.get("bib", {}).get("title", ""),
                "authors": paper.get("bib", {}).get("author", ""),
                "abstract": paper.get("bib", {}).get("abstract", ""),
                "url": paper.get("pub_url", ""),
                "source": "Google Scholar"
            })
        except StopIteration:
            break
    return results

# ---------- ARXIV SCRAPER ----------
def crawl_arxiv(query: str, limit: int = 20) -> List[Dict]:
    """
    Search arXiv for research papers.
    """
    results = []
    search = arxiv.Search(
        query=query,
        max_results=limit,
        sort_by=arxiv.SortCriterion.Relevance
    )
    
    for paper in search.results():
        results.append({
            "title": paper.title,
            "authors": [author.name for author in paper.authors],
            "abstract": paper.summary,
            "url": paper.entry_id,
            "source": "arXiv"
        })
    return results

# ---------- GENERIC WEBSITE CRAWLER (optional) ----------
def crawl_generic_site(url: str) -> str:
    """
    Basic crawler to fetch raw HTML text (for future extensions).
    """
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    return soup.get_text(separator="\n")

# ---------- MAIN FUNCTION ----------
def crawl_papers(query: str, limit: int = 20) -> List[Dict]:
    """
    Combined crawler fetching from multiple sources.
    """
    google_results = crawl_google_scholar(query, limit)
    arxiv_results = crawl_arxiv(query, limit)
    
    # Combine and remove duplicates
    all_results = google_results + arxiv_results
    seen_titles = set()
    unique_results = []
    
    for paper in all_results:
        if paper["title"] not in seen_titles:
            seen_titles.add(paper["title"])
            unique_results.append(paper)
    
    return unique_results

if __name__ == "__main__":
    query = "vertical restraints Indian pharmaceutical sector"
    papers = crawl_papers(query, limit=10)
    
    with open("papers.json", "w", encoding="utf-8") as f:
        json.dump(papers, f, indent=4, ensure_ascii=False)
    
    print(f"✅ Crawled {len(papers)} papers. Saved to papers.json")
