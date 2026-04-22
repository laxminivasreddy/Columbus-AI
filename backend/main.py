from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from api.routes import chat, hotels, weather, auth
from agents.orchestrator import ColumbusOrchestrator
from db.mongodb import connect_db, disconnect_db
import json

app = FastAPI(title="Columbus AI", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/auth")
app.include_router(chat.router, prefix="/api/chat")
app.include_router(hotels.router, prefix="/api/hotels")
app.include_router(weather.router, prefix="/api/weather")

@app.on_event("startup")
async def startup():
    await connect_db()

@app.on_event("shutdown")
async def shutdown():
    await disconnect_db()

@app.get("/health")
async def health():
    return {"status": "ok", "service": "Columbus AI"}

@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    await websocket.accept()
    orchestrator = ColumbusOrchestrator()
    try:
        while True:
            data = await websocket.receive_json()
            async for event in orchestrator.plan_trip(
                user_id=user_id,
                query=data["query"],
                origin=data.get("origin", "Unknown"),
                destination=data["destination"],
                days=data["days"],
                budget=data["budget"],
                passengers=data.get("passengers", {"adults": 1, "children": 0, "women": 0}),
                interests=data.get("interests", []),
                travel_style=data.get("travel_style", "mid-range"),
                travel_dates=data.get("travel_dates"),
                accommodation_type=data.get("accommodation_type"),
                food_preferences=data.get("food_preferences"),
            ):
                await websocket.send_text(event)
    except WebSocketDisconnect:
        pass
    except Exception as e:
        await websocket.send_json({"status": "error", "message": str(e)})
