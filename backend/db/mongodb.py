from motor.motor_asyncio import AsyncIOMotorClient
from config import get_settings

_client = None
_db = None

async def connect_db():
    global _client, _db
    settings = get_settings()
    _client = AsyncIOMotorClient(settings.mongodb_url)
    _db = _client.columbus_ai
    print("✅ MongoDB connected")

async def disconnect_db():
    if _client:
        _client.close()

async def get_db():
    return _db
