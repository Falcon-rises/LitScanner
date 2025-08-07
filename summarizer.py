from transformers import pipeline
import openai
import json
from typing import List, Dict
import os

# ---------- ENV: Set your OpenAI key ----------
openai.api_key = os.getenv("OPENAI_API_KEY")  # Make sure this is set

# ---------- Pegasus Summarizer ----------
pegasus_summarizer = pipeline(
    "summarization",
    model="google/pegasus-xsum",
    tokenizer="google/pegasus-xsum",
    framework="pt",
    device=-1  # CPU, change to 0 if using GPU
)

def summarize_with_pegasus(text: str, max_len: int = 150) -> str:
    """
    Summarize individual paper using Pegasus.
    """
    if len(text.split()) < 50:
        return text
    summary = pegasus_summarizer(
        text,
        max_length=max_len,
        min_length=50,
        do_sample=False
    )[0]["summary_text"]
    return summary

def batch_summarize_with_pegasus(papers: List[Dict]) -> List[Dict]:
    """
    Batch summarization of multiple papers using Pegasus.
    """
    summarized = []
    for paper in papers:
        summarized.append({
            **paper,
            "summary": summarize_with_pegasus(paper.get("abstract", ""))
        })
    return summarized

def generate_meta_review(summaries: List[str]) -> str:
    """
    Combine Pegasus summaries into a high-level GPT meta-review.
    """
    combined_text = "\n".join(summaries[:100])  # Keep under token limit
    prompt = (
        "You are an expert research reviewer. Based on the following summaries "
        "of research papers, generate a comprehensive systematic literature review. "
        "Include main themes, methodologies, key findings, and gaps.\n\n"
        f"{combined_text}\n\n"
        "Meta-Review:"
    )

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a professional academic summarizer."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3,
        max_tokens=2000
    )

    return response.choices[0]["message"]["content"]

if __name__ == "__main__":
    # Load crawled papers
    with open("papers.json", "r", encoding="utf-8") as f:
        papers = json.load(f)

    # Step 1: Pegasus summarization
    summarized_papers = batch_summarize_with_pegasus(papers)

    with open("summaries.json", "w", encoding="utf-8") as f:
        json.dump(summarized_papers, f, indent=4, ensure_ascii=False)

    print(f"✅ Pegasus summarized {len(summarized_papers)} papers. Saved to summaries.json")

    # Step 2: GPT Meta-Review
    summaries = [p["summary"] for p in summarized_papers]
    meta_review = generate_meta_review(summaries)

    with open("meta_review.txt", "w", encoding="utf-8") as f:
        f.write(meta_review)

    print("✅ GPT Meta-Review generated and saved to meta_review.txt")
