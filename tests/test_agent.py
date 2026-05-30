import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_analyze_endpoint_missing_ticker():
    response = client.post("/analyze", json={"ticker": ""})
    assert response.status_code == 400

def test_analyze_endpoint_success():
    with patch("app.main.analyze_stock") as mock_analyze:
        mock_analyze.return_value = "CBA is a strong banking stock with solid fundamentals."
        response = client.post("/analyze", json={"ticker": "CBA"})
        assert response.status_code == 200
        assert "ticker" in response.json()
        assert "analysis" in response.json()
        assert response.json()["ticker"] == "CBA"

def test_analyze_endpoint_with_question():
    with patch("app.main.analyze_stock") as mock_analyze:
        mock_analyze.return_value = "CBA dividend yield is 3%."
        response = client.post("/analyze", json={
            "ticker": "CBA",
            "question": "What is the dividend outlook?"
        })
        assert response.status_code == 200
        assert response.json()["ticker"] == "CBA"

def test_stock_data_tool_returns_string():
    with patch("yfinance.Ticker") as mock_ticker:
        mock_info = {
            "currentPrice": 165.02,
            "marketCap": 275000000000,
            "trailingPE": 26.62,
            "fiftyTwoWeekHigh": 192.0,
            "fiftyTwoWeekLow": 146.98,
            "dividendYield": 0.03,
            "regularMarketVolume": 5000000,
            "sector": "Financial Services",
            "longName": "Commonwealth Bank of Australia"
        }
        mock_ticker.return_value.info = mock_info
        from app.tools import get_stock_data
        result = get_stock_data.invoke("CBA")
        assert isinstance(result, str)
        assert "CBA" in result or "Commonwealth" in result

def test_calculate_cost_format():
    with patch("yfinance.Ticker") as mock_ticker:
        mock_ticker.return_value.info = {
            "currentPrice": 45.50,
            "marketCap": 50000000000,
            "trailingPE": 15.0,
            "fiftyTwoWeekHigh": 50.0,
            "fiftyTwoWeekLow": 35.0,
            "dividendYield": 0.04,
            "regularMarketVolume": 1000000,
            "sector": "Mining",
            "longName": "BHP Group"
        }
        from app.tools import get_stock_data
        result = get_stock_data.invoke("BHP")
        assert "AUD" in result