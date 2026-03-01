import os
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from sse_starlette.sse import EventSourceResponse
import uvicorn
import asyncio
from typing import Dict, Any

from src.agent.orchestrator import OpsCommander

app = FastAPI(title="Mistral OpsCommander API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class LogBroker:
    def __init__(self):
        self.listeners = []
        self.history = []

    async def publish(self, message: str):
        self.history.append(message)
        for queue in self.listeners:
            await queue.put(message)

    async def subscribe(self):
        q = asyncio.Queue()
        for msg in self.history:
            await q.put(msg)
        self.listeners.append(q)
        return q

    def unsubscribe(self, q):
        if q in self.listeners:
            self.listeners.remove(q)

broker = LogBroker()
current_incident_task = None

async def run_incident_task(alert_payload):
    commander = OpsCommander()
    stream = commander.handle_incident_stream(alert_payload)
    try:
        async for chunk in stream:
            await broker.publish(chunk)
            await asyncio.sleep(0.5) # Dramatic effect
    except Exception as e:
        await broker.publish(f'{{"type": "error", "model": "System", "content": "Stream error: {str(e)}"}}')
    finally:
        await broker.publish('{"type": "done", "model": "System", "content": "Resolution complete."}')

@app.post("/api/trigger")
async def trigger_incident(payload: Dict[str, Any] | None = None):
    global current_incident_task
    
    simulated_alert = payload or {
        "alert_id": "ALT-9082",
        "title": "High Memory Usage & Crash loop on Auth Service",
        "severity": "CRITICAL",
        "service": "auth-service",
        "timestamp": "2026-02-28T14:40:00Z"
    }
    
    if current_incident_task and not current_incident_task.done():
        current_incident_task.cancel()
        
    broker.history.clear()
    current_incident_task = asyncio.create_task(run_incident_task(simulated_alert))
    
    return {"status": "Incident triggered. Connect to /api/stream to view logs."}

@app.get("/api/stream")
async def stream_logs(request: Request):
    async def event_generator():
        q = await broker.subscribe()
        try:
            # Yield history first if any immediately
            if not broker.history:
                yield {"data": '{"type": "info", "model": "System", "content": "No active incident. Awaiting trigger..."}'}
            
            while True:
                if await request.is_disconnected():
                    break
                
                chunk = await q.get()
                yield {"data": chunk}
        finally:
            broker.unsubscribe(q)

    return EventSourceResponse(event_generator())

@app.on_event("startup")
async def startup_event():
    from src.bot.discord_bot import run_discord_bot
    asyncio.create_task(run_discord_bot())

if __name__ == "__main__":
    uvicorn.run("src.main:app", host="0.0.0.0", port=8001, reload=True)
