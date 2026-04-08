"""FastAPI server for SimCity"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
import os
import asyncio
from datetime import datetime
from database import MongoDBService
from config import SCENARIOS

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="SimCity API",
    description="Real-time urban disaster simulation dashboard",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global state
db = None
active_scenario = None
scenario_start_time = None
SCENARIO_DURATION = 60  # seconds
connected_clients = set()

@app.on_event("startup")
async def startup():
    """Initialize database on startup"""
    global db
    try:
        db = MongoDBService()
        logger.info("✅ Backend started successfully")
    except Exception as e:
        logger.error(f"❌ Failed to start backend: {e}")
        raise

@app.on_event("shutdown")
async def shutdown():
    """Close database on shutdown"""
    if db:
        db.close()
        logger.info("Database connection closed")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "ok",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "database": "connected" if db else "disconnected"
    }

@app.post("/ingest")
async def ingest(data: list):
    """Receive data from simulator"""
    if not db:
        raise HTTPException(status_code=503, detail="Database not connected")
    
    if len(data) != 3:
        raise HTTPException(status_code=400, detail="Expected 3 data points")
    
    traffic, hospital, supply = data
    result = db.ingest_data(traffic, hospital, supply)
    return result

@app.get("/status")
async def get_status():
    """Get current system status"""
    if not db:
        raise HTTPException(status_code=503, detail="Database not connected")
    
    return {
        "traffic": db.get_latest_traffic(),
        "hospitals": db.get_latest_hospitals(),
        "supply": db.get_latest_supply(),
        "alerts": db.get_active_alerts(),
        "active_scenario": active_scenario,
        "scenario_remaining": max(0, SCENARIO_DURATION - int((datetime.utcnow() - scenario_start_time).total_seconds())) if scenario_start_time else 0
    }

@app.post("/trigger")
async def trigger_scenario(request: dict):
    """Trigger a disaster scenario"""
    global active_scenario, scenario_start_time
    
    scenario = request.get("scenario")
    if scenario not in SCENARIOS and scenario != "reset":
        raise HTTPException(status_code=400, detail=f"Invalid scenario: {scenario}")
    
    if scenario == "reset":
        active_scenario = None
        scenario_start_time = None
        logger.info("🔄 Scenario reset")
        return {"status": "reset", "active_scenario": None}
    
    active_scenario = scenario
    scenario_start_time = datetime.utcnow()
    logger.info(f"🎯 Scenario triggered: {scenario}")
    
    return {
        "event": scenario,
        "active": True,
        "duration_seconds": SCENARIO_DURATION
    }

@app.get("/alerts")
async def get_alerts(limit: int = 50):
    """Get recent alerts"""
    if not db:
        raise HTTPException(status_code=503, detail="Database not connected")
    
    return {
        "alerts": db.get_alerts(limit),
        "count": len(db.get_alerts(limit))
    }

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket for real-time updates"""
    await websocket.accept()
    connected_clients.add(websocket)
    logger.info(f"🔗 Client connected. Total: {len(connected_clients)}")
    
    try:
        while True:
            # Keep connection alive and send periodic updates
            await asyncio.sleep(5)
            if db:
                status = {
                    "type": "status_update",
                    "data": {
                        "traffic": db.get_latest_traffic(),
                        "hospitals": db.get_latest_hospitals(),
                        "supply": db.get_latest_supply(),
                        "alerts": db.get_active_alerts()
                    }
                }
                try:
                    await websocket.send_json(status)
                except:
                    break
    except WebSocketDisconnect:
        connected_clients.discard(websocket)
        logger.info(f"🔌 Client disconnected. Total: {len(connected_clients)}")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        connected_clients.discard(websocket)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)