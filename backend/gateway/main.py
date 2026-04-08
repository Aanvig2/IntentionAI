import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../"))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
import jwt
import time
from dotenv import load_dotenv

load_dotenv()

from backend.shared.tokens import decode_token
from backend.audit.db import init_db, log_action, get_recent_logs

app = FastAPI(title="ArmorClaw Gateway")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

OPA_URL = os.getenv("OPA_URL", "http://localhost:8181") + "/v1/data/financial"

init_db()

class ActionRequest(BaseModel):
    agent_id: str
    token: str
    action: str
    ticker: str = ""
    qty: int = 0
    destination: str = "internal"
    metadata: dict = {}

@app.get("/health")
def health():
    return {"status": "ok", "timestamp": time.time()}

@app.post("/validate")
def validate_action(req: ActionRequest):
    # 1. Decode and verify JWT
    try:
        token_data = decode_token(req.token)
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {e}")

    # 2. Send to OPA
    opa_input = {
        "input": {
            "action": req.action,
            "ticker": req.ticker,
            "qty": req.qty,
            "destination": req.destination,
            "token": token_data,
        }
    }

    try:
        opa_resp = requests.post(OPA_URL, json=opa_input, timeout=5).json()
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"OPA unreachable: {e}")

    result = opa_resp.get("result", {})
    allowed = result.get("allow", False)
    violations = list(result.get("violation", []))

    # 3. Write audit log
    log_action(req.agent_id, req.action, req.ticker, allowed, violations)

    return {
        "allowed": allowed,
        "violations": violations,
        "agent_id": req.agent_id,
        "action": req.action,
        "ticker": req.ticker,
    }

@app.get("/logs")
def get_logs(limit: int = 50):
    return get_recent_logs(limit)
