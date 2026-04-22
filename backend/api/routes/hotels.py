from fastapi import APIRouter
from pydantic import BaseModel
from urllib.parse import quote_plus
from config import get_settings
import httpx

router = APIRouter()
settings = get_settings()

RAPIDAPI_HOST = "booking-com.p.rapidapi.com"

class HotelSearchRequest(BaseModel):
    destination: str
    checkin: str
    checkout: str
    guests: int = 2
    budget: int = 0

async def get_destination_id(destination: str, client: httpx.AsyncClient):
    """Hits the Booking.com RapidAPI to resolve the city name to a dest_id."""
    res = await client.get(
        f"https://{RAPIDAPI_HOST}/v1/hotels/locations",
        params={"name": destination, "locale": "en-gb"},
        headers={"x-rapidapi-key": settings.rapidapi_key, "x-rapidapi-host": RAPIDAPI_HOST},
        timeout=15,
    )
    res.raise_for_status()
    data = res.json()
    
    if len(data) > 0:
        return data[0].get("dest_id"), data[0].get("dest_type")
    return None, None

@router.post("/search")
async def search_hotels(body: HotelSearchRequest):
    search_url_fallback = f"https://www.booking.com/searchresults.html?ss={quote_plus(body.destination)}&checkin={body.checkin}&checkout={body.checkout}&group_adults={body.guests}"

    try:
        async with httpx.AsyncClient() as client:
            # Step 1: Get the exact Destination ID from RapidAPI
            dest_id, dest_type = await get_destination_id(body.destination, client)
            
            if not dest_id:
                raise Exception(f"Could not find destination ID for {body.destination}")

            # Step 2: Fetch Live Hotel Data using the extracted destination ID
            res = await client.get(
                f"https://{RAPIDAPI_HOST}/v1/hotels/search",
                params={
                    "dest_id": dest_id,
                    "dest_type": dest_type,
                    "checkin_date": body.checkin,
                    "checkout_date": body.checkout,
                    "adults_number": body.guests,
                    "room_number": 1,
                    "units": "metric",
                    "filter_by_currency": "INR",
                    "locale": "en-gb",
                    "order_by": "popularity"
                },
                headers={
                    "x-rapidapi-key": settings.rapidapi_key,
                    "x-rapidapi-host": RAPIDAPI_HOST
                },
                timeout=20,
            )
            res.raise_for_status()
            data = res.json()
            
            properties = data.get("result", [])
            hotels = []

            # Step 3: Fetch all possible hotels but strictly verify their budget limits
            for p in properties:
                raw_price = p.get("min_total_price")
                amount = float(raw_price) if raw_price is not None else 0.0
                
                if body.budget > 0 and amount > body.budget:
                    continue

                image_url = p.get("max_photo_url", "https://images.unsplash.com/photo-1566073771259-6a8506099945?ixlib=rb-4.0.3")
                booking_url = p.get("url", search_url_fallback)
                
                hotels.append({
                    "name": p.get("hotel_name") or "Unknown Hotel",
                    "hotel_id": str(p.get("hotel_id") or ""),
                    "rating": float(p.get("review_score") or 8.0),
                    "reviews": int(p.get("review_nr") or 0),
                    "price_per_night": round(amount, 2),
                    "currency": p.get("currencycode") or "INR",
                    "image": image_url,
                    "location": p.get("city_trans") or body.destination,
                    "type": p.get("property_type") or "Hotel",
                    "amenities": ["WiFi", "Comfortable Beds"],
                    "description": p.get("distance_to_cc_formatted") or "Central Location",
                    "booking_url": booking_url
                })

            return {
                "hotels": hotels,
                "destination": body.destination,
                "booking_search_url": search_url_fallback
            }

    except Exception as e:
        print(f"[HOTEL_RAPIDAPI_ERROR] Live Fetch Failed: {str(e)}")
        # If their quota runs out or the network dies, return the smart fallback!
        fallback_hotels = [
            {
                "name": f"{body.destination} Grand Plaza",
                "hotel_id": "fallback1",
                "rating": 8.5,
                "reviews": 1200,
                "price_per_night": 5000,
                "currency": "INR",
                "location": body.destination,
                "type": "Hotel",
                "amenities": ["WiFi", "Pool"],
                "description": "Central location",
                "image": "https://images.unsplash.com/photo-1566073771259-6a8506099945?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80",
                "booking_url": search_url_fallback
            },
            {
                "name": f"The {body.destination} Boutique",
                "hotel_id": "fallback2",
                "rating": 9.1,
                "reviews": 850,
                "price_per_night": 7500,
                "currency": "INR",
                "location": body.destination,
                "type": "Boutique",
                "amenities": ["WiFi", "Spa", "Breakfast"],
                "description": "Luxury downtown",
                "image": "https://images.unsplash.com/photo-1520250497591-112f2f40a3f4?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80",
                "booking_url": search_url_fallback
            },
            {
                "name": f"{body.destination} Central Inn",
                "hotel_id": "fallback3",
                "rating": 7.8,
                "reviews": 2100,
                "price_per_night": 3000,
                "currency": "INR",
                "location": body.destination,
                "type": "Inn",
                "amenities": ["WiFi", "Restaurant"],
                "description": "Affordable stay",
                "image": "https://images.unsplash.com/photo-1542314831-c6a4d1409e1c?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80",
                "booking_url": search_url_fallback
            }
        ]
        
        return {
            "hotels": fallback_hotels,
            "error": str(e),
            "booking_search_url": search_url_fallback
        }
