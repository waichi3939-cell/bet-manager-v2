import os
from datetime import datetime, timezone

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from models import HealthResponse, OddsItem, OddsResponse

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
def get_odds(raceId: str):
    items = [
        OddsItem(combination="2-3-5", odds=45.0),
        OddsItem(combination="2-5-3", odds=62.0),
        OddsItem(combination="3-2-5", odds=38.0),
        OddsItem(combination="3-5-2", odds=71.0),
    ]
    return OddsResponse(
        raceId=raceId,
        items=items,
        fetchedAt=datetime.now(timezone.utc).isoformat(),
    )


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000)
