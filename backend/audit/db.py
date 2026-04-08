import sqlite3
import time
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "audit.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS audit_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            agent_id TEXT,
            action TEXT,
            ticker TEXT,
            allowed INTEGER,
            violations TEXT,
            timestamp REAL
        )
    """)
    conn.commit()
    conn.close()

def log_action(agent_id, action, ticker, allowed, violations):
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        INSERT INTO audit_log (agent_id, action, ticker, allowed, violations, timestamp)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (agent_id, action, ticker, int(allowed), str(violations), time.time()))
    conn.commit()
    conn.close()

def get_recent_logs(limit=50):
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute(
        "SELECT * FROM audit_log ORDER BY timestamp DESC LIMIT ?", (limit,)
    ).fetchall()
    conn.close()
    return [
        {
            "id": r[0],
            "agent_id": r[1],
            "action": r[2],
            "ticker": r[3],
            "allowed": bool(r[4]),
            "violations": r[5],
            "timestamp": r[6]
        }
        for r in rows
    ]
