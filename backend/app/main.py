import os
from fastapi import FastAPI, Depends, Header, HTTPException

from fastapi.staticfiles import StaticFiles

from app.services.negotiation import negotiate_rate
from app.services.fmcsa import verify_carrier_by_mc
from sqlalchemy.orm import Session
from sqlalchemy import func, text
from app.database import engine, SessionLocal
from app.models import Base, Load, CallLog
from pydantic import BaseModel
from typing import Optional
from app.seed_loads import seed_loads_if_empty

Base.metadata.create_all(bind=engine)

# Migrate existing tables — add new columns if they don't exist yet
with engine.connect() as conn:
    try:
        conn.execute(text("ALTER TABLE call_logs ADD COLUMN created_at DATETIME"))
        conn.commit()
    except Exception:
        pass  # Column already exists, skip

seed_loads_if_empty()

app = FastAPI(
    title="Inbound Carrier Sales API",
    description="Backend API for HappyRobot inbound carrier sales automation.",
    version="0.1.0"
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

API_KEY = os.getenv("API_KEY", "dev-api-key")

def verify_api_key(x_api_key: str = Header(None)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid or missing API key")
    return True


# -----------------------------
# DATABASE SESSION
# -----------------------------

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# -----------------------------
# HEALTH CHECK
# -----------------------------

@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "inbound-carrier-sales-api"
    }

# -----------------------------
# SEARCH REQUEST MODEL
# -----------------------------

class LoadSearchRequest(BaseModel):
    origin: Optional[str] = None
    destination: Optional[str] = None
    equipment_type: Optional[str] = None

# ------------------------
# CARRIER REQUEST MODEL
# ------------------------
class CarrierVerifyRequest(BaseModel):
    mc_number: str

# ------------------------
# NEGOTIATION REQUEST MODEL
# ------------------------

class NegotiationRequest(BaseModel):
    load_id: str
    carrier_offer: float
    round_number: int

# -----------------------------
# GET ALL LOADS
# -----------------------------

@app.get("/loads")
def get_loads(db: Session = Depends(get_db), authorized: bool = Depends(verify_api_key)):
    loads = db.query(Load).all()

    return loads

# -----------------------------
# SEARCH LOADS
# -----------------------------

@app.post("/loads/search")
def search_loads(
    request: LoadSearchRequest,
    db: Session = Depends(get_db), authorized: bool = Depends(verify_api_key)
):

    query = db.query(Load)

    if request.origin:
        query = query.filter(
            Load.origin.ilike(f"%{request.origin}%")
        )

    if request.destination:
        query = query.filter(
            Load.destination.ilike(f"%{request.destination}%")
        )

    if request.equipment_type:
        query = query.filter(
            Load.equipment_type.ilike(f"%{request.equipment_type}%")
        )

    results = query.all()

    return {
        "count": len(results),
        "loads": results
    }

@app.post("/carrier/verify")
def verify_carrier(request: CarrierVerifyRequest, authorized: bool = Depends(verify_api_key)):
    result = verify_carrier_by_mc(request.mc_number)

    return result

@app.post("/negotiate")
def negotiate(
    request: NegotiationRequest,
    db: Session = Depends(get_db), authorized: bool = Depends(verify_api_key)
):

    load = db.query(Load).filter(
        Load.load_id == request.load_id
    ).first()

    if not load:
        return {
            "error": "Load not found"
        }

    result = negotiate_rate(
        load=load,
        carrier_offer=request.carrier_offer,
        round_number=request.round_number
    )

    return {
        "load_id": load.load_id,
        "loadboard_rate": load.loadboard_rate,
        **result
    }

# -------------------------
# CALL LOGS REQUEST
# -------------------------
class CallLogRequest(BaseModel):
    carrier_mc: str
    load_id: str
    outcome: str
    negotiated_rate: float
    sentiment: str
    negotiation_rounds: int

@app.post("/calls/log")
def log_call(
    request: CallLogRequest,
    db: Session = Depends(get_db), authorized: bool = Depends(verify_api_key)
):

    log = CallLog(
        carrier_mc=request.carrier_mc,
        load_id=request.load_id,
        outcome=request.outcome,
        negotiated_rate=request.negotiated_rate,
        sentiment=request.sentiment,
        negotiation_rounds=request.negotiation_rounds
    )

    db.add(log)
    db.commit()

    return {
        "message": "Call logged successfully"
    }

# -------------------------
# GET RECENT CALLS
# -------------------------

@app.get("/calls")
def get_calls(
    limit: int = 50,
    db: Session = Depends(get_db),
    authorized: bool = Depends(verify_api_key)
):
    calls = db.query(CallLog).order_by(CallLog.id.desc()).limit(limit).all()
    return {
        "count": len(calls),
        "calls": [
            {
                "id": c.id,
                "carrier_mc": c.carrier_mc,
                "load_id": c.load_id,
                "outcome": c.outcome,
                "negotiated_rate": c.negotiated_rate,
                "sentiment": c.sentiment,
                "negotiation_rounds": c.negotiation_rounds,
            }
            for c in calls
        ]
    }

# -------------------------
# METRICS
# -------------------------

@app.get("/metrics")
def get_metrics(db: Session = Depends(get_db), authorized: bool = Depends(verify_api_key)):

    total_calls = db.query(CallLog).count()

    successful_calls = db.query(CallLog).filter(
        CallLog.outcome == "SUCCESS"
    ).count()

    failed_calls = db.query(CallLog).filter(
        CallLog.outcome != "SUCCESS"
    ).count()

    success_rate = round(successful_calls / total_calls * 100, 1) if total_calls > 0 else 0

    # Breakdown by outcome
    outcome_rows = (
        db.query(CallLog.outcome, func.count(CallLog.outcome))
        .group_by(CallLog.outcome)
        .all()
    )
    outcomes_breakdown = {outcome: count for outcome, count in outcome_rows}

    # Sentiment distribution
    sentiment_rows = (
        db.query(CallLog.sentiment, func.count(CallLog.sentiment))
        .group_by(CallLog.sentiment)
        .all()
    )
    sentiment_distribution = {sentiment: count for sentiment, count in sentiment_rows}

    # Average negotiated rate (successful calls only)
    avg_rate = db.query(func.avg(CallLog.negotiated_rate)).filter(
        CallLog.outcome == "SUCCESS"
    ).scalar()
    avg_negotiated_rate = round(float(avg_rate), 2) if avg_rate else 0

    # Average negotiation rounds (all calls)
    avg_rounds = db.query(func.avg(CallLog.negotiation_rounds)).scalar()
    avg_negotiation_rounds = round(float(avg_rounds), 1) if avg_rounds else 0

    return {
        "total_calls": total_calls,
        "successful_calls": successful_calls,
        "failed_calls": failed_calls,
        "success_rate": success_rate,
        "avg_negotiated_rate": avg_negotiated_rate,
        "avg_negotiation_rounds": avg_negotiation_rounds,
        "outcomes_breakdown": outcomes_breakdown,
        "sentiment_distribution": sentiment_distribution,
    }
