from utils.llm import call_claude
import json, re

BUDGET_SYSTEM = """You are the Budget Agent — a financial optimizer for travel.
Given an itinerary, validate total cost against budget, find cheaper alternatives,
allocate 10% buffer for emergencies, and explain every cost decision.
Output revised itinerary + cost breakdown as JSON with a budget_analysis field."""

class BudgetAgent:
    async def optimize(self, itinerary, total_budget, travel_style, passengers):
        user_msg = f"""
Budget: ₹{total_budget:,}
Travel style: {travel_style}
Group Size: {passengers.get('adults', 1)} Adults, {passengers.get('children', 0)} Children

Itinerary to optimize:
{json.dumps(itinerary, indent=2)}

Calculate total cost, ensuring attraction and food costs reflect the group size above (e.g. multiplied by total passengers). If over budget, suggest cheaper alternatives.
Return optimized itinerary as JSON with budget_analysis field.
"""
        response = await call_claude(system_prompt=BUDGET_SYSTEM, user_message=user_msg, max_tokens=1500)
        match = re.search(r'\{.*\}', response, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except Exception:
                pass
        return {"raw": response}
