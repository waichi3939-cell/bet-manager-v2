import os
from datetime import datetime, timezone

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from models import HealthResponse, OddsItem, OddsResponse
from scraper import fetch_odds

load_dotenv()

app = FastAPI()

origins_env = os.getenv("ALLOWED_ORIGINS")
origins = origins_env.split(",") if origins_env else ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", response_model=HealthResponse)
def health():
    return HealthResponse(status="ok")


@app.get("/odds", response_model=OddsResponse)
def get_odds(raceId: str, combinations: str | None = None):
    combo_set = set(combinations.split(",")) if combinations else None
    raw = fetch_odds(raceId, combo_set)
    if not raw:
        raise HTTPException(status_code=503, detail="オッズ取得失敗")
    items = [OddsItem(**item) for item in raw]
    return OddsResponse(
        raceId=raceId,
        items=items,
        fetchedAt=datetime.now(timezone.utc).isoformat(),
    )


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000)
