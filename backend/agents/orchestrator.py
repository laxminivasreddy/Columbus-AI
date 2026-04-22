import asyncio, json
from agents.planner_agent import PlannerAgent
from agents.budget_agent import BudgetAgent
from agents.explorer_agent import ExplorerAgent
from agents.safety_agent import SafetyAgent
from agents.memory_agent import MemoryAgent
from rag.pipeline import RAGPipeline
from utils.llm import call_claude

SYNTHESIS_SYSTEM = """You are Columbus AI — an expert travel assistant.
You have outputs from 5 specialized AI agents. Synthesize into one coherent travel plan:
- Day-by-day plan with times
- Full cost breakdown
- Hidden gems section
- Safety briefing
- Personalized tips
For EVERY recommendation explain: Why this place? Why this order? Why this cost?
Use warm, enthusiastic tone."""

class ColumbusOrchestrator:
    def __init__(self):
        self.planner = PlannerAgent()
        self.budget = BudgetAgent()
        self.explorer = ExplorerAgent()
        self.safety = SafetyAgent()
        self.memory = MemoryAgent()
        self.rag = RAGPipeline()

    async def plan_trip(self, user_id, query, origin, destination, days, budget, passengers, interests, travel_style="mid-range", travel_dates=None, accommodation_type=None, food_preferences=None):
        yield json.dumps({"status": "retrieving_context", "message": "🔍 Retrieving travel knowledge..."})

        rag_context, user_history, user_prefs = await asyncio.gather(
            self.rag.retrieve_and_synthesize(query, destination),
            self.rag.retrieve_user_history(user_id, query),
            self.memory.load_preferences(user_id),
        )

        if user_prefs.get("preferred_style"):
            travel_style = user_prefs["preferred_style"]
        if user_prefs.get("interests"):
            interests = list(set(interests + user_prefs["interests"]))
        if not accommodation_type and user_prefs.get("accommodation_type"):
            accommodation_type = user_prefs["accommodation_type"]
        if not food_preferences and user_prefs.get("food_preferences"):
            food_preferences = user_prefs["food_preferences"]

        yield json.dumps({"status": "running_agents", "message": "🤖 Running specialized agents..."})

        initial_itinerary = await self.planner.plan(
            origin=origin, destination=destination, days=days, budget=budget, passengers=passengers,
            interests=interests, travel_style=travel_style,
            user_history=user_history, rag_context=rag_context,
            accommodation_type=accommodation_type, food_preferences=food_preferences
        )

        yield json.dumps({"status": "optimizing", "message": "💰 Optimizing budget..."})

        optimized_itinerary, hidden_gems, safety_report = await asyncio.gather(
            self.budget.optimize(initial_itinerary, budget, travel_style, passengers),
            self.explorer.find_hidden_gems(destination, interests, initial_itinerary),
            self.safety.assess(destination, travel_dates or {}),
        )

        yield json.dumps({"status": "synthesizing", "message": "✨ Synthesizing final plan..."})

        synthesis_input = f"""
User query: {query}
Trip: {origin} to {destination} | Days: {days} | Budget: ₹{budget:,}
Passengers: {passengers.get('adults', 1)} Adults, {passengers.get('children', 0)} Children, {passengers.get('women', 0)} Women
Travel style: {travel_style} | Interests: {', '.join(interests)}
Accommodation: {accommodation_type or 'Any'} | Food: {food_preferences or 'Any'}

PLANNER OUTPUT:
{json.dumps(optimized_itinerary, indent=2)}

HIDDEN GEMS:
{json.dumps(hidden_gems, indent=2)}

SAFETY REPORT:
{json.dumps(safety_report, indent=2)}

USER PREFERENCES:
{json.dumps(user_prefs, indent=2)}

Create the final comprehensive travel plan. Make sure to consider the logistics from the origin location and activities mapping to the specific ages/interests of the passenger demographic.
"""
        full_response = await call_claude(
            system_prompt=SYNTHESIS_SYSTEM,
            user_message=synthesis_input,
            max_tokens=2500,
        )

        for chunk in full_response.split(". "):
            yield json.dumps({"status": "streaming", "chunk": chunk + ". "})
            await asyncio.sleep(0.03)

        # Update user's persistent memory profiles in the background
        asyncio.create_task(self.memory.update_preferences(user_id, {
            "latest_destination": destination,
            "latest_budget": budget,
            "travel_style": travel_style,
            "interests": interests,
            "passengers": passengers,
            "accommodation_type": accommodation_type,
            "food_preferences": food_preferences
        }))

        yield json.dumps({
            "status": "complete",
            "itinerary": optimized_itinerary,
            "hidden_gems": hidden_gems,
            "safety": safety_report,
            "full_text": full_response,
        })
