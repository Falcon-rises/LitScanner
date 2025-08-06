import networkx as nx
import json
from typing import List, Dict

def build_citation_graph(papers: List[Dict]) -> nx.DiGraph:
    """
    Builds a directed graph of citations from paper metadata.
    Each node = paper title, each edge = citation relationship.
    """
    G = nx.DiGraph()

    for paper in papers:
        title = paper.get("title")
        if not title:
            continue

        # Add paper as a node
        G.add_node(title, authors=paper.get("authors"), url=paper.get("url"))

        # Add citation edges if present
        citations = paper.get("citations", [])
        for cited in citations:
            G.add_edge(title, cited)

    return G

def save_graph(G: nx.DiGraph, output_file: str = "citation_graph.gexf"):
    """
    Saves graph to GEXF format for visualization (Gephi or web).
    """
    nx.write_gexf(G, output_file)
    print(f"✅ Citation graph saved to {output_file}")

if __name__ == "__main__":
    with open("papers_with_topics.json", "r", encoding="utf-8") as f:
        papers = json.load(f)

    G = build_citation_graph(papers)
    save_graph(G)
