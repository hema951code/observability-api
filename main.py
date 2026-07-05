from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================
# EDIT THIS ONE LINE: put your logged-in email here
# ============================================================
YOUR_EMAIL = "22f1000951@ds.study.iitm.ac.in"

API_KEY = "ak_kahe05fn30iv65kf24ga6d17"


class Event(BaseModel):
    user: str
    amount: float
    ts: Optional[int] = None


class AnalyticsRequest(BaseModel):
    events: List[Event]


@app.post("/analytics")
def analytics(payload: AnalyticsRequest, x_api_key: Optional[str] = Header(None)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Missing or invalid API key")

    events = payload.events

    total_events = len(events)
    unique_users = len({e.user for e in events})

    positive_events = [e for e in events if e.amount > 0]
    revenue = sum(e.amount for e in positive_events)

    totals_by_user = {}
    for e in positive_events:
        totals_by_user[e.user] = totals_by_user.get(e.user, 0) + e.amount

    top_user = max(totals_by_user, key=totals_by_user.get) if totals_by_user else None

    return {
        "email": YOUR_EMAIL,
        "total_events": total_events,
        "unique_users": unique_users,
        "revenue": revenue,
        "top_user": top_user,
    }
