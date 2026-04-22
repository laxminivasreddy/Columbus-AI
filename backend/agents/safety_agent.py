from utils.llm import call_claude
import re, json

SAFETY_SYSTEM = """You are the Safety Agent. Assess travel safety and provide:
1. Safety level (1-5, 5=safest)
2. Specific risks for destination and time of year
3. Health precautions
4. Emergency contacts
5. Areas to avoid
6. Safe transport recommendations
Format as JSON with fields: safety_score, risks, precautions,
emergency_contacts, areas_to_avoid, transport_advice, why_this_score"""

class SafetyAgent:
    async def assess(self, destination, travel_dates):
        response = await call_claude(
            system_prompt=SAFETY_SYSTEM,
            user_message=f"""
Destination: {destination}
Travel period: {travel_dates.get('from', 'not specified')} to {travel_dates.get('to', 'not specified')}
Provide comprehensive safety assessment as JSON.
""",
            max_tokens=1000
        )
        match = re.search(r'\{.*\}', response, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except Exception:
                pass
        return {"raw": response, "safety_score": 3}
