import os
import yfinance as yf
from tavily import TavilyClient
from langchain.tools import tool
from app.rag import index_ticker, query_rag
from dotenv import load_dotenv

load_dotenv()

@tool
def get_stock_data(ticker: str) -> str:
    """Get real-time ASX stock data including price, P/E ratio, market cap, 
    52-week high/low, and dividend yield for a given ASX ticker."""
    try:
        asx_ticker = f"{ticker.upper()}.AX"
        stock = yf.Ticker(asx_ticker)
        info = stock.info

        price = info.get("currentPrice") or info.get("regularMarketPrice", "N/A")
        market_cap = info.get("marketCap", "N/A")
        pe_ratio = info.get("trailingPE", "N/A")
        week_high = info.get("fiftyTwoWeekHigh", "N/A")
        week_low = info.get("fiftyTwoWeekLow", "N/A")
        dividend_yield = info.get("dividendYield", "N/A")
        volume = info.get("regularMarketVolume", "N/A")
        sector = info.get("sector", "N/A")
        company_name = info.get("longName", ticker.upper())

        if market_cap != "N/A":
            market_cap = f"AUD {market_cap / 1e9:.2f}B"
        if dividend_yield != "N/A":
            dividend_yield = f"{dividend_yield * 100:.2f}%"

        return f"""
{company_name} ({ticker.upper()}.AX) — Live Market Data
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Current Price:      AUD {price}
Market Cap:         {market_cap}
P/E Ratio:          {pe_ratio}
52-Week High:       AUD {week_high}
52-Week Low:        AUD {week_low}
Dividend Yield:     {dividend_yield}
Volume:             {volume:,} shares
Sector:             {sector}
"""
    except Exception as e:
        return f"Failed to fetch stock data for {ticker}: {str(e)}"


@tool
def get_news(ticker: str) -> str:
    """Search for the latest news and market sentiment for a given ASX ticker 
    using real-time web search."""
    try:
        client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
        query = f"{ticker} ASX stock news analysis 2026"
        
        response = client.search(
            query=query,
            search_depth="advanced",
            max_results=5,
            include_answer=True
        )

        news_items = []
        for result in response.get("results", []):
            title = result.get("title", "")
            content = result.get("content", "")[:300]
            url = result.get("url", "")
            news_items.append(f"• {title}\n  {content}\n  Source: {url}")

        summary = response.get("answer", "")
        news_text = "\n\n".join(news_items)

        return f"""
Latest News for {ticker.upper()} ASX
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Summary: {summary}

Recent Articles:
{news_text}
"""
    except Exception as e:
        return f"Failed to fetch news for {ticker}: {str(e)}"


@tool
def get_announcements(ticker: str) -> str:
    """Retrieve and search through official ASX company announcements 
    for a given ticker using semantic search."""
    try:
        print(f"Indexing ASX announcements for {ticker}...")
        count = index_ticker(ticker)
        
        if count == 0:
            return f"No ASX announcements found for {ticker}."
        
        context = query_rag(
            ticker=ticker,
            question="latest announcements earnings dividends outlook"
        )
        
        return f"""
Official ASX Announcements for {ticker.upper()}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{context}
"""
    except Exception as e:
        return f"Failed to fetch announcements for {ticker}: {str(e)}"