from typing import List

from pydantic import BaseModel


class OddsItem(BaseModel):
    combination: str
    odds: float


class OddsResponse(BaseModel):
    raceId: str
    items: List[OddsItem]
    fetchedAt: str


class HealthResponse(BaseModel):
    status: str
