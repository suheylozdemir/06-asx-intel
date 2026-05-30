from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from app.agent import analyze_stock

app = FastAPI(
    title="ASX Intel API",
    description="AI-powered ASX stock analysis agent",
    version="1.0.0"
)

class AnalyzeRequest(BaseModel):
    ticker: str
    question: str = None

class AnalyzeResponse(BaseModel):
    ticker: str
    analysis: str

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/analyze", response_model=AnalyzeResponse)
def analyze(request: AnalyzeRequest):
    if not request.ticker:
        raise HTTPException(status_code=400, detail="Ticker is required")
    
    try:
        analysis = analyze_stock(
            ticker=request.ticker.upper(),
            question=request.question
        )
        return AnalyzeResponse(
            ticker=request.ticker.upper(),
            analysis=analysis
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))