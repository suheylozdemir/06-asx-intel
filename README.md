# ASX Intel 📈

AI-powered Australian stock market analysis agent. Enter any ASX ticker and get a comprehensive analysis powered by real-time data and large language models.

🚀 **[Live Demo](#)** ← updated after Streamlit Cloud deploy

---

## What It Does

A LangGraph ReAct agent combines three real-time data sources into a single structured analysis:

- **Yahoo Finance** — live price, P/E ratio, market cap, 52-week high/low, dividend yield, trading volume
- **Tavily Search** — latest news and market sentiment from across the web, summarised and ranked by relevance
- **RAG Tool** — official ASX company announcements retrieved via Pinecone semantic search

The agent decides which tools to call, in what order, and how many times — then synthesises everything into a structured investment analysis complete with risk disclaimer. No static data, no mock responses. Every analysis is generated from live sources at query time.

---

## Architecture

```
User Input (ASX Ticker)
          │
          ▼
    Streamlit UI
          │
          ▼
   FastAPI /analyze
          │
          ▼
  LangGraph ReAct Agent
          │
    ┌─────┼─────┐
    ▼     ▼     ▼
Yahoo   Tavily  Pinecone
Finance Search  (RAG)
    │     │     │
    └─────┴─────┘
          │
          ▼
    GPT-4.1-mini
    (Synthesis)
          │
          ▼
  Structured Report
  + Risk Disclaimer
```

The agent runs a ReAct loop — Reason, Act, Observe — until it has gathered sufficient information from all three sources. It will not generate a final answer until all tools have been consulted.

---

## Example Output

**Input:** `CBA`

**Output includes:**
- Current price: AUD 165.02
- Market cap: AUD 275.93B
- P/E ratio: 26.62
- 52-week high/low: AUD 192.00 / AUD 146.98
- Dividend yield: 3.00%
- Recent news sentiment: mixed to slightly bearish
- Key announcements: latest trading updates and regulatory filings
- Strengths: dominant retail banking franchise, leading digital banking app
- Risks: exposure to housing market, regulatory pressure, margin compression
- Overall outlook: positive medium-term with near-term headwinds

---

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Agent Framework | LangGraph (ReAct) |
| LLM | OpenAI gpt-4.1-mini |
| Financial Data | Yahoo Finance (yfinance) |
| News Search | Tavily API |
| Vector DB | Pinecone |
| API | FastAPI |
| UI | Streamlit + Plotly |
| CI/CD | GitHub Actions |

---

## Project Structure

```
06-asx-intel/
├── app/
│   ├── agent.py          # LangGraph ReAct agent
│   ├── tools.py          # Yahoo Finance, Tavily, RAG tools
│   ├── rag.py            # Pinecone indexing and semantic search
│   └── main.py           # FastAPI endpoints
├── ui/
│   └── streamlit_app.py  # Streamlit UI with Plotly charts
├── tests/
│   └── test_agent.py     # pytest test suite
├── .github/workflows/
│   └── ci.yml            # GitHub Actions CI
├── .env.example
├── requirements.txt
└── README.md
```

---

## How to Run

**1. Clone the repo**

```bash
git clone https://github.com/suheylozdemir/06-asx-intel
cd 06-asx-intel
```

**2. Install dependencies**

```bash
pip install -r requirements.txt
```

**3. Set up environment variables**

```bash
cp .env.example .env
# Add your keys:
# OPENAI_API_KEY=...
# PINECONE_API_KEY=...
# TAVILY_API_KEY=...
```

**4. Start the API**

```bash
uvicorn app.main:app --reload
```

**5. Start the UI (new terminal)**

```bash
streamlit run ui/streamlit_app.py
```

**6. Run tests**

```bash
pytest tests/ -v
```

---

## Türkçe Açıklama

Avustralya borsasında (ASX) işlem gören şirketler için yapay zeka destekli analiz aracı. Bir ticker kodu giriyorsun, sistem üç farklı gerçek zamanlı kaynaktan veri toplayıp kapsamlı bir analiz sunuyor.

## Nasıl Çalışır?

LangGraph ile kurulmuş bir ReAct agent üç tool'u yönetiyor. Hangi tool'u ne zaman çağıracağına model kendisi karar veriyor — bu klasik RAG pipeline'larından temel farkı.

Yahoo Finance tool'u anlık hisse fiyatı, piyasa değeri, F/K oranı, 52 haftalık yüksek/düşük ve temettü verimi gibi finansal metrikleri çekiyor. Tavily tool'u web genelinde o şirketle ilgili son haberleri ve piyasa duyarlılığını tarıyor, sonuçları önem sırasına göre sıralıyor. RAG tool'u Pinecone vektör veritabanında şirket duyurularında semantik arama yapıyor — kelime eşleşmesi değil, anlam bazlı arama.

Agent tüm kaynaklardan veri toplandıktan sonra GPT-4.1-mini ile sentezleyip risk uyarısıyla birlikte yapılandırılmış bir rapor üretiyor. Statik veri yok, mock response yok — her analiz sorgu anında canlı kaynaklardan üretiliyor.

## Neden Bu Proje?

Sydney fintech ve bankacılık sektörü ASX verisiyle doğrudan ilişkili. İşverenler bu alanda domain bilgisi olan adayları tercih ediyor. Bu proje hem teknik derinliği hem de lokal pazar bilgisini bir arada gösteriyor.

Teknik olarak da portföydeki her şeyi bir araya getiriyor: LangGraph agent mimarisi (4. proje), RAG pipeline (3. proje), Pinecone vektör veritabanı (5. proje), FastAPI, CI/CD. Capstone olarak tüm becerilerin entegrasyonunu göstermek için tasarlandı.

## Teknoloji Stack

- **Agent:** LangGraph ReAct — hangi tool'un ne zaman çağrılacağına model karar veriyor, sabit sıra yok
- **LLM:** OpenAI gpt-4.1-mini — hem tool seçimi hem analiz sentezi için
- **Finansal Veri:** Yahoo Finance — gerçek zamanlı ASX hisse verileri, .AX suffix ile
- **Haber Arama:** Tavily API — web genelinde güncel haberler, advanced search depth
- **Vektör DB:** Pinecone — şirket duyuruları için semantik arama, ticker bazlı filtreleme
- **API:** FastAPI — Streamlit ile agent arasındaki köprü, /analyze ve /health endpoint'leri
- **UI:** Streamlit + Plotly — 6 aylık fiyat grafiği, finansal metrikler tablosu, AI analizi
- **CI/CD:** GitHub Actions — her push'ta otomatik test, Python 3.11