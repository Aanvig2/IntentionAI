import jwt
import time
from dataclasses import dataclass
from typing import List, Optional

JWT_SECRET = "your-secret-here"
ALGORITHM = "HS256"

@dataclass
class CapabilityToken:
    agent_id: str
    allowed_actions: List[str]   # ["BUY"], ["READ"], ["LOG"]
    ticker_scope: List[str]      # ["AAPL"] or ["*"]
    max_qty: int                 # 0 = unlimited for non-trade agents
    destination_scope: str       # "internal" or "external"
    expires_in: int = 300        # seconds

def mint_token(token: CapabilityToken) -> str:
    payload = {
        "agent_id": token.agent_id,
        "allowed_actions": token.allowed_actions,
        "ticker_scope": token.ticker_scope,
        "max_qty": token.max_qty,
        "destination_scope": token.destination_scope,
        "exp": time.time() + token.expires_in,
        "iat": time.time(),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=ALGORITHM)

def decode_token(token_str: str) -> dict:
    return jwt.decode(token_str, JWT_SECRET, algorithms=[ALGORITHM])