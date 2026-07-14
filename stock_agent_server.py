import os
import requests
import markdown
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse

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

@app.get("/stock-verdict", response_class=HTMLResponse)
async def get_verdict(ticker: str, extra_query: str = ""):
    if not API_KEY:
        raise HTTPException(status_code=500, detail="PERPLEXITY_API_KEY not set")

    user_msg = f"Analyze the stock: {ticker}."
    if extra_query:
        user_msg += f" Additional context: {extra_query}"

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "sonar",
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_msg}
        ]
    }

    response = requests.post("https://api.perplexity.ai/chat/completions", json=payload, headers=headers)
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=response.text)

    data = response.json()
    analysis_md = data["choices"][0]["message"]["content"]
    analysis_html = markdown.markdown(analysis_md, extensions=["extra", "nl2br"])

    html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Stock Verdict: {ticker.upper()}</title>
        <style>
            * {{ box-sizing: border-box; margin: 0; padding: 0; }}
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                background: #0f1117;
                color: #e2e8f0;
                padding: 2rem;
                line-height: 1.7;
            }}
            .container {{
                max-width: 860px;
                margin: 0 auto;
                background: #1a1d27;
                border-radius: 16px;
                padding: 2.5rem;
                border: 1px solid #2d3148;
                box-shadow: 0 4px 32px rgba(0,0,0,0.4);
            }}
            .header {{
                display: flex;
                align-items: center;
                gap: 1rem;
                margin-bottom: 2rem;
                padding-bottom: 1.5rem;
                border-bottom: 1px solid #2d3148;
            }}
            .ticker-badge {{
                background: linear-gradient(135deg, #6366f1, #8b5cf6);
                color: white;
                font-size: 1.4rem;
                font-weight: 700;
                padding: 0.4rem 1.2rem;
                border-radius: 8px;
                letter-spacing: 1px;
            }}
            h1 {{ font-size: 1.5rem; color: #a5b4fc; font-weight: 600; }}
            h2, h3 {{
                color: #818cf8;
                margin-top: 1.8rem;
                margin-bottom: 0.6rem;
                font-size: 1.1rem;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }}
            p {{ margin-bottom: 0.8rem; color: #cbd5e1; }}
            ul, ol {{
                padding-left: 1.5rem;
                margin-bottom: 1rem;
            }}
            li {{ margin-bottom: 0.4rem; color: #cbd5e1; }}
            strong {{ color: #f1f5f9; }}
            hr {{
                border: none;
                border-top: 1px solid #2d3148;
                margin: 1.5rem 0;
            }}
            code {{
                background: #2d3148;
                padding: 0.1rem 0.4rem;
                border-radius: 4px;
                font-size: 0.9em;
            }}
            .footer {{
                margin-top: 2rem;
                padding-top: 1rem;
                border-top: 1px solid #2d3148;
                font-size: 0.8rem;
                color: #475569;
                text-align: center;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <span class="ticker-badge">{ticker.upper()}</span>
                <h1>Stock Verdict Agent Analysis</h1>
            </div>
            <div class="analysis">
                {analysis_html}
            </div>
            <div class="footer">Powered by Perplexity AI &bull; Stock Verdict Agent</div>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html)
