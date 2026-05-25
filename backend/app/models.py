from sqlalchemy import Column, Integer, String, Float, DateTime
from datetime import datetime, timezone

from app.database import Base

class Load(Base):
    __tablename__ = "loads"

    id = Column(Integer, primary_key=True, index=True)

    load_id = Column(String, unique=True, index=True)

    origin = Column(String)
    destination = Column(String)

    pickup_datetime = Column(String)
    delivery_datetime = Column(String)

    equipment_type = Column(String)

    loadboard_rate = Column(Float)

    min_acceptable_rate = Column(Float)
    target_rate = Column(Float)
    max_rate = Column(Float)

    notes = Column(String)

    weight = Column(Float)

    commodity_type = Column(String)

    num_of_pieces = Column(Integer)

    miles = Column(Float)

    dimensions = Column(String)

    status = Column(String, default="AVAILABLE")

class CallLog(Base):
    __tablename__ = "call_logs"

    id = Column(Integer, primary_key=True, index=True)

    carrier_mc = Column(String)

    load_id = Column(String)

    outcome = Column(String)

    negotiated_rate = Column(Float)

    sentiment = Column(String)

    negotiation_rounds = Column(Integer)
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
