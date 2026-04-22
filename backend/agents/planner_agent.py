from utils.llm import call_claude
from rag.pipeline import RAGPipeline
import json, re

PLANNER_SYSTEM = """You are the Planner Agent for Columbus AI — an expert travel itinerary architect.
Create detailed day-by-day itineraries with exact time slots.
Sequence activities logically (no backtracking routes).
Include travel time between venues.
Always explain WHY each activity is in its slot.
CRITICAL: Restrict the itinerary strictly to the provided origin, destination, and logical transit points. Do NOT hallucinate or include other random cities from the context or your memory.
 
Output ONLY valid JSON in this format:
{
  "days": [
    {
      "day": 1,
      "theme": "...",
      "slots": [
        {
          "time": "09:00",
          "activity": "...",
          "location": "...",
          "duration_hrs": 2,
          "why": "...",
          "cost_inr": 500
        }
      ]
    }
  ],
  "reasoning": "overall trip logic explanation"
}"""

class PlannerAgent:
    def __init__(self):
        self.rag = RAGPipeline()

    async def plan(self, origin, destination, days, budget, passengers, interests, travel_style, user_history, rag_context, accommodation_type=None, food_preferences=None):
        user_msg = f"""
Plan a {days}-day trip from {origin} to {destination}.
Passengers: {passengers.get('adults', 1)} Adults, {passengers.get('children', 0)} Children, {passengers.get('women', 0)} Women
Budget: ₹{budget:,}
Interests: {', '.join(interests)}
Travel style: {travel_style}
Accommodation Preference: {accommodation_type or 'Any'}
Food Preference: {food_preferences or 'Any'}

Retrieved travel guide context:
{rag_context}

User past travel patterns:
{user_history}

Create a complete day-by-day itinerary. Ensure Day 1 accounts for travel logistics from {origin}. Make sure activities are appropriate for the passenger demographic (e.g., kid-friendly if children are present). Explain every choice. Output only JSON.
"""
        response = await call_claude(system_prompt=PLANNER_SYSTEM, user_message=user_msg, max_tokens=2000)
        match = re.search(r'\{.*\}', response, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except Exception:
                pass
        return {"raw": response, "days": [], "reasoning": response}
