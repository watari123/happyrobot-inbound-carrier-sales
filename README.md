# HappyRobot Inbound Carrier Sales Automation

AI-powered inbound carrier sales workflow built as part of the HappyRobot FDE Technical Challenge.

This project simulates a freight brokerage workflow where carriers call in to:
- verify operational eligibility
- search available freight loads
- negotiate pricing
- finalize load bookings
- log call outcomes and operational metrics

The system is designed as a modular backend architecture that separates:
- carrier verification
- load search
- negotiation logic
- call logging
- analytics/metrics

---

# Overview

Freight brokerages handle large volumes of inbound carrier calls daily.  
This project automates portions of that workflow using structured APIs and deterministic business logic layered underneath an AI conversational interface.

The backend exposes APIs that can be orchestrated by HappyRobot voice agents to:
1. Verify carriers using MC numbers
2. Search loads by lane/equipment
3. Negotiate pricing with operational guardrails
4. Escalate edge cases
5. Capture structured operational data

---

# Architecture

```txt
HappyRobot Voice Agent
          ↓
    FastAPI Backend
          ↓
------------------------------------------------
| Carrier Verification Service                 |
| Load Search Service                          |
| Negotiation Engine                           |
| Call Logging Service                         |
| Metrics & Analytics Service                  |
------------------------------------------------
          ↓
      SQLite Database
```

---

# Features

## Carrier Verification
- Verifies carriers using MC numbers
- Simulates FMCSA eligibility checks
- Checks:
  - authority status
  - insurance validity
  - safety rating
- Returns structured eligibility responses

---

## Load Search
Supports load search filtering by:
- origin
- destination
- equipment type

Supports multiple freight profiles:
- Dry Van
- Reefer
- Flatbed
- Box Truck

---

## Negotiation Engine
Implements deterministic negotiation logic with:
- target pricing
- maximum approved pricing
- escalation thresholds
- transfer conditions

Negotiation outcomes:
- Accept
- Counter
- Reject
- Escalate to sales rep

The system intentionally separates business logic from conversational AI to improve:
- reliability
- explainability
- operational control

---

## Call Logging & Metrics
Captures:
- negotiated rate
- outcome
- sentiment
- negotiation rounds
- carrier MC number

Metrics endpoint supports:
- total calls
- successful bookings
- failed bookings

---

# API Endpoints

| Endpoint | Description |
|---|---|
| `GET /health` | Health check |
| `GET /loads` | Retrieve all loads |
| `POST /loads/search` | Search available loads |
| `POST /carrier/verify` | Verify carrier eligibility |
| `POST /negotiate` | Negotiate load pricing |
| `POST /calls/log` | Log completed calls |
| `GET /metrics` | Retrieve operational metrics |

---

# Example Workflow

```txt
Carrier calls in
      ↓
Carrier verification
      ↓
Load search
      ↓
AI pitches matching load
      ↓
Carrier negotiates pricing
      ↓
Accept / Counter / Reject
      ↓
Transfer to sales rep
      ↓
Call outcome logged
```

---

# Tech Stack

## Backend
- Python
- FastAPI
- SQLAlchemy
- SQLite

## DevOps
- Docker
- GitHub

## AI Orchestration
- HappyRobot platform

---

# Local Development

## Clone Repository

```bash
git clone https://github.com/watari123/happyrobot-inbound-carrier-sales.git
cd happyrobot-inbound-carrier-sales
```

## Setup Virtual Environment

```bash
cd backend

python3 -m venv venv
source venv/bin/activate
```

## Install Dependencies

```bash
pip install -r requirements.txt
```

## Run Backend

```bash
uvicorn app.main:app --reload
```

Backend available at:

```txt
http://127.0.0.1:8000
```

Swagger docs:

```txt
http://127.0.0.1:8000/docs
```

---

# Sample Test Cases

## Verify Carrier

```json
{
  "mc_number": "123456"
}
```

---

## Search Loads

```json
{
  "origin": "Dallas",
  "equipment_type": "Dry Van"
}
```

---

## Negotiate Rate

```json
{
  "load_id": "LOAD001",
  "carrier_offer": 2250,
  "round_number": 1
}
```

---

# Screenshots

## Swagger API Documentation
<img width="2930" height="1628" alt="image" src="https://github.com/user-attachments/assets/39aea94e-010c-48ac-b1ac-f388a9934f91" />

## Load Search
<img width="2240" height="1208" alt="image" src="https://github.com/user-attachments/assets/b533c7f6-a05b-45cf-946e-a46f4d980059" />
<img width="2254" height="952" alt="image" src="https://github.com/user-attachments/assets/c34da9ac-f838-45e9-b694-80eda0ec0ef8" />

## Negotiation Flow
<img width="2208" height="1486" alt="image" src="https://github.com/user-attachments/assets/a9752cd1-83e5-4be5-b494-269e2e2baaba" />
<img width="2160" height="1494" alt="image" src="https://github.com/user-attachments/assets/bcafdc83-b205-42c8-aabb-4b5c27d7e232" />

## Metrics Dashboard
https://happyrobot-inbound-carrier-sales-production.up.railway.app/static/dashboard.html
<img width="2918" height="1656" alt="image" src="https://github.com/user-attachments/assets/79071d6c-a290-4fa2-b57d-f4d002e22a7f" />


# Author

Built by Ash Tamgadge as part of the HappyRobot FDE Technical Challenge.
