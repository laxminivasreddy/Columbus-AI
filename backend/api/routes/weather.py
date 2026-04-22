from fastapi import APIRouter
from pydantic import BaseModel
import httpx
from config import get_settings

router = APIRouter()
settings = get_settings()

@router.get("/current")
async def get_weather(city: str):
    async with httpx.AsyncClient() as client:
        try:
            current = await client.get(
                f"https://api.openweathermap.org/data/2.5/weather",
                params={"q": city, "appid": settings.weather_api_key, "units": "metric"}
            )
            forecast = await client.get(
                f"https://api.openweathermap.org/data/2.5/forecast",
                params={"q": city, "appid": settings.weather_api_key, "units": "metric"}
            )
            if current.status_code != 200:
                return {"error": "City not found"}
            return {
                "current": current.json(),
                "forecast": forecast.json()
            }
        except Exception as e:
            return {"error": str(e)}
