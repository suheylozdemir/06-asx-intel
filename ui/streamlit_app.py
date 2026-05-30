import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd
from app.agent import analyze_stock

st.set_page_config(
    page_title="ASX Intel",
    page_icon="📈",
    layout="wide"
)

st.title("📈 ASX Intel")
st.caption("AI-powered Australian Stock Market Analysis")

with st.sidebar:
    st.header("Stock Analysis")
    ticker = st.text_input("ASX Ticker", placeholder="e.g. CBA, BHP, CSL").upper()
    question = st.text_area("Specific Question (optional)", placeholder="e.g. What is the dividend outlook?")
    analyze_btn = st.button("Analyze", type="primary", use_container_width=True)
    st.divider()
    st.caption("Data sources: ASX, Yahoo Finance, Tavily")

if analyze_btn and ticker:
    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("📊 Market Data")
        with st.spinner("Fetching market data..."):
            try:
                stock = yf.Ticker(f"{ticker}.AX")
                info = stock.info

                price = info.get("currentPrice") or info.get("regularMarketPrice", "N/A")
                market_cap = info.get("marketCap", "N/A")
                pe = info.get("trailingPE", "N/A")
                week_high = info.get("fiftyTwoWeekHigh", "N/A")
                week_low = info.get("fiftyTwoWeekLow", "N/A")
                div_yield = info.get("dividendYield", "N/A")

                if market_cap != "N/A":
                    market_cap = f"AUD {market_cap / 1e9:.2f}B"
                if div_yield != "N/A":
                    div_yield = f"{div_yield * 100:.2f}%"

                metrics_df = pd.DataFrame({
                    "Metric": ["Current Price", "Market Cap", "P/E Ratio", "52W High", "52W Low", "Dividend Yield"],
                    "Value": [f"AUD {price}", market_cap, pe, f"AUD {week_high}", f"AUD {week_low}", div_yield]
                })
                st.dataframe(metrics_df, use_container_width=True, hide_index=True)

            except Exception as e:
                st.error(f"Failed to load market data: {e}")

        st.subheader("📉 Price History (6 Months)")
        with st.spinner("Loading chart..."):
            try:
                hist = stock.history(period="6mo")
                if not hist.empty:
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(
                        x=hist.index,
                        y=hist["Close"],
                        mode="lines",
                        name=ticker,
                        line=dict(color="#00C49F", width=2)
                    ))
                    fig.update_layout(
                        height=300,
                        margin=dict(l=0, r=0, t=0, b=0),
                        paper_bgcolor="rgba(0,0,0,0)",
                        plot_bgcolor="rgba(0,0,0,0)",
                        xaxis=dict(showgrid=False),
                        yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.1)")
                    )
                    st.plotly_chart(fig, use_container_width=True)
            except Exception as e:
                st.error(f"Failed to load chart: {e}")

    with col2:
        st.subheader("🤖 AI Analysis")
        with st.spinner("Agent is analyzing... this may take 30-60 seconds."):
            try:
                analysis = analyze_stock(
                    ticker=ticker,
                    question=question if question else None
                )
                st.markdown(analysis)
            except Exception as e:
                st.error(f"Analysis failed: {e}")

elif analyze_btn and not ticker:
    st.warning("Please enter an ASX ticker.")
else:
    st.info("Enter an ASX ticker in the sidebar and click Analyze to get started.")