import os
import requests
from openai import OpenAI
from pinecone import Pinecone, ServerlessSpec
from dotenv import load_dotenv

load_dotenv()

INDEX_NAME = "asx-intel"

def get_pinecone_index():
    pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
    existing = [i.name for i in pc.list_indexes()]
    if INDEX_NAME not in existing:
        pc.create_index(
            name=INDEX_NAME,
            dimension=1536,
            metric="cosine",
            spec=ServerlessSpec(cloud="aws", region="us-east-1")
        )
    return pc.Index(INDEX_NAME)

def get_embedding(text: str) -> list:
    client = OpenAI()
    response = client.embeddings.create(
        input=text,
        model="text-embedding-3-small"
    )
    return response.data[0].embedding

def fetch_asx_announcements(ticker: str, limit: int = 10) -> list:
    url = f"https://asx.com.au/asx/1/company/{ticker.upper()}/announcements"
    params = {"count": limit, "market_sensitive": "false"}
    headers = {"User-Agent": "Mozilla/5.0"}
    
    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        announcements = []
        for item in data.get("data", []):
            title = item.get("header", "")
            date = item.get("document_release_date", "")
            url_pdf = item.get("url", "")
            announcements.append({
                "id": f"{ticker}_{item.get('id', '')}",
                "ticker": ticker.upper(),
                "title": title,
                "date": date,
                "content": f"{ticker.upper()} ASX Announcement — {date}: {title}",
                "url": url_pdf
            })
        return announcements
    except Exception as e:
        print(f"Failed to fetch announcements for {ticker}: {e}")
        return []

def index_ticker(ticker: str):
    index = get_pinecone_index()
    announcements = fetch_asx_announcements(ticker)
    
    if not announcements:
        print(f"No announcements found for {ticker}")
        return 0
    
    vectors = []
    for ann in announcements:
        embedding = get_embedding(ann["content"])
        vectors.append({
            "id": ann["id"],
            "values": embedding,
            "metadata": {
                "ticker": ann["ticker"],
                "title": ann["title"],
                "date": ann["date"],
                "content": ann["content"],
                "url": ann["url"]
            }
        })
    
    index.upsert(vectors=vectors)
    print(f"Indexed {len(vectors)} announcements for {ticker}")
    return len(vectors)

def query_rag(ticker: str, question: str, top_k: int = 3) -> str:
    index = get_pinecone_index()
    query_text = f"{ticker} {question}"
    embedding = get_embedding(query_text)
    
    results = index.query(
        vector=embedding,
        top_k=top_k,
        include_metadata=True,
        filter={"ticker": ticker.upper()}
    )
    
    if not results["matches"]:
        return f"No ASX announcements found for {ticker}."
    
    context = "\n\n".join([
        f"[{m['metadata']['date']}] {m['metadata']['title']}\n{m['metadata']['content']}"
        for m in results["matches"]
    ])
    
    return context