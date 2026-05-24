import os
from fastapi import FastAPI, Depends, Header, HTTPException

from app.services.negotiation import negotiate_rate
from app.services.fmcsa import verify_carrier_by_mc
from sqlalchemy.orm import Session
from app.database import engine, SessionLocal
from app.models import Base, Load, CallLog
from pydantic import BaseModel
from typing import Optional

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Inbound Carrier Sales API",
    description="Backend API for HappyRobot inbound carrier sales automation.",
    version="0.1.0"
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

@app.get("/metrics")
def get_metrics(db: Session = Depends(get_db), authorized: bool = Depends(verify_api_key)):

    total_calls = db.query(CallLog).count()

    successful_calls = db.query(CallLog).filter(
        CallLog.outcome == "BOOKED"
    ).count()

    failed_calls = db.query(CallLog).filter(
        CallLog.outcome == "FAILED"
    ).count()

    return {
        "total_calls": total_calls,
        "successful_calls": successful_calls,
        "failed_calls": failed_calls
    }
