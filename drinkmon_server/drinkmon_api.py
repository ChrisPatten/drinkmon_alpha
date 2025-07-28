"""
FastAPI backend for drinkmon session management.
Stores active sessions, assigns GUIDs, and allows closing sessions.
"""
VERSION = "0.0.2"


import logging
from logging.config import dictConfig
import sys
import json
from datetime import datetime
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from uuid import uuid4

# Custom JSON formatter for structured logs
class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "module": record.module,
            "line": record.lineno,
            "message": record.getMessage(),
        }
        if record.exc_info:
            log_record["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_record)

# Logging configuration
log_config = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "json": {"()": JsonFormatter},
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "DEBUG",
            "formatter": "json",
            "stream": "ext://sys.stdout",
        },
        "rotating_file": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "DEBUG",
            "formatter": "json",
            "filename": "drinkmon_api.log",
            "maxBytes": 10485760,  # 10 MB
            "backupCount": 5,
        },
    },
    "loggers": {
        "drinkmon": {
            "handlers": ["console", "rotating_file"],
            "level": "DEBUG",
            "propagate": False,
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "DEBUG",
    },
}
dictConfig(log_config)
logger = logging.getLogger("drinkmon")

app = FastAPI()
logger.info(f"Started drinkmon API server version {VERSION}")

class Color(BaseModel):
    r: int = Field(..., ge=0, le=255)
    g: int = Field(..., ge=0, le=255)
    b: int = Field(..., ge=0, le=255)

class SessionStartRequest(BaseModel):
    color: Color

class SessionStartResponse(BaseModel):
    guid: str

class SessionCloseRequest(BaseModel):
    guid: str

class Session(BaseModel):
    guid: str
    color: Color
    started: datetime
    closed: Optional[datetime] = None

sessions: Dict[str, Session] = {}

@app.post("/api/start_session", response_model=SessionStartResponse)
def start_session(req: SessionStartRequest) -> SessionStartResponse:
    """
    Start a new session, assign a GUID, and store it as active.
    """
    guid = str(uuid4())
    session = Session(guid=guid, color=req.color, started=datetime.utcnow())
    sessions[guid] = session
    logger.info(f"Session started: guid={guid}, color={req.color.dict()}")
    return SessionStartResponse(guid=guid)

@app.post("/api/close_session")
def close_session(req: SessionCloseRequest):
    """
    Close an active session by GUID.
    """
    session = sessions.get(req.guid)
    if not session:
        logger.warning(f"Attempt to close non-existent session: guid={req.guid}")
        raise HTTPException(status_code=404, detail="Session not found")
    if session.closed:
        logger.warning(f"Attempt to close already closed session: guid={req.guid}")
        raise HTTPException(status_code=400, detail="Session already closed")
    session.closed = datetime.utcnow()
    logger.info(f"Session closed: guid={req.guid}")
    return {"status": "closed"}

@app.get("/api/friend_sessions", response_model=List[Dict[str, Color]])
def get_active_sessions() -> List[Dict[str, Color]]:
    """
    Return a list of active (open) sessions and their colors.
    """
    active = [{"color": s.color} for s in sessions.values() if not s.closed]
    logger.debug(f"Active sessions requested. Count: {len(active)}")
    return active
  
@app.post("/api/clear_sessions")
def clear_sessions():
    """
    Clear all active and closed sessions from the server.
    
    Returns:
        dict: Status message indicating sessions were cleared.
    """
    # Clear all sessions (active and closed)
    count = len(sessions)
    sessions.clear()
    logger.info(f"All sessions cleared. Previous count: {count}")
    return {"status": "sessions cleared", "cleared_count": count}
