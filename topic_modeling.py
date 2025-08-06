from bertopic import BERTopic
from sklearn.feature_extraction.text import CountVectorizer
import spacy
import json
from typing import List, Dict

# Load English NLP model for preprocessing
nlp = spacy.load("en_core_web_sm")

def preprocess_text(text: str) -> str:
    """
    Basic text cleaning: lemmatization and stopword removal.
    """
    doc = nlp(text.lower())
    tokens = [
        token.lemma_ 
        for token in doc 
        if not token.is_stop and token.is_alpha and len(token) > 3
    ]
    return " ".join(tokens)

def extract_texts_for_topic_model(papers: List[Dict]) -> List[str]:
    """
    Collect summaries or abstracts for topic modeling.
    """
    texts = []
    for paper in papers:
        text = paper.get("summary") or paper.get("abstract", "")
        if text:
            texts.append(preprocess_text(text))
    return texts

def build_topic_model(texts: List[str]) -> BERTopic:
    """
    Fit BERTopic model on summaries/abstracts.
    """
    vectorizer = CountVectorizer(ngram_range=(1, 2), stop_words="english")
    topic_model = BERTopic(vectorizer_model=vectorizer, verbose=True)
    topic_model.fit(texts)
    return topic_model

if __name__ == "__main__":
    with open("summaries.json", "r", encoding="utf-8") as f:
        papers = json.load(f)
    
    texts = extract_texts_for_topic_model(papers)
    
    print(f"✅ Preprocessed {len(texts)} documents for topic modeling")

    topic_model = build_topic_model(texts)
    
    # Save model and topics
    topic_model.save("bertopic_model")
    
    topics, _ = topic_model.transform(texts)
    
    # Assign topics to papers
    for i, paper in enumerate(papers):
        paper["topic"] = int(topics[i]) if i < len(topics) else None

    with open("papers_with_topics.json", "w", encoding="utf-8") as f:
        json.dump(papers, f, indent=4, ensure_ascii=False)

    # Export topic info
    topic_info = topic_model.get_topic_info()
    topic_info.to_csv("topic_info.csv", index=False)

    print("✅ Topic modeling completed. Results saved to papers_with_topics.json and topic_info.csv")
