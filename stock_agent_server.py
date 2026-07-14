import os
import requests
from fastapi import FastAPI, HTTPException

app = FastAPI()
API_KEY = os.getenv("PERPLEXITY_API_KEY")

SYSTEM_PROMPT = """You are a No-BS stock analysis agent for an Indian investor with a long-term horizon, high risk appetite, and 2-5% position sizing.

For any given stock ticker, provide analysis in this exact structure:
[BUSINESS QUALITY] - What the company does, moat, competitive position, sector tailwinds/headwinds
[GROWTH & FINANCIALS] - Revenue/EBIT/PAT trend, margins, ROE/ROCE, key efficiency metrics
[VALUATION TODAY] - Market cap, PE, PB, yield vs peers; is it cheap/fair/rich?
[KEY POSITIVES] - 4-6 bullets for a long-term high-risk investor: structural drivers, moat, scalability
[KEY RISKS & RED FLAGS] - 4-6 bullets: valuation risk, leverage, governance, cyclicality, regulation
[HOW I'D PLAY IT] - Entry strategy, staggered entries or breakout, sizing, buy on dips or chase?
[BOTTOM LINE] - One clear yes/no/maybe recommendation paragraph in plain language. No fluff."""

@app.get("/")
async def root():
    return {"status": "Stock Verdict Agent is live", "usage": "/stock-verdict?ticker=INFY"}

@app.get("/stock-verdict")
async def get_verdict(ticker: str, extra_query: str = ""):
    if not API_KEY:
        raise HTTPException(status_code=500, detail="PERPLEXITY_API_KEY not configured")

    user_msg = f"Analyze the stock: {ticker}."
    if extra_query:
        user_msg += f" Additional context: {extra_query}"

    response = requests.post(
        "https://api.perplexity.ai/chat/completions",
        headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
        json={
            "model": "sonar-pro",
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_msg}
            ]
        },
        timeout=60
    )

    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=response.text)

    data = response.json()
    analysis = data["choices"][0]["message"]["content"]
    return {"ticker": ticker.upper(), "analysis": analysis}
