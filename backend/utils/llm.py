import groq
from groq import AsyncGroq
from config import get_settings
import logging

logger = logging.getLogger(__name__)
settings = get_settings()
client = AsyncGroq(api_key=settings.anthropic_api_key)

async def call_claude(
    system_prompt: str,
    user_message: str,
    max_tokens: int = 1500,
    conversation_history: list = None,
    model: str = "llama-3.1-8b-instant",
) -> str:
    messages = [{"role": "system", "content": system_prompt}]
    if conversation_history:
        messages.extend(conversation_history)
    messages.append({"role": "user", "content": user_message})

    # Define a cascading sequence of models to try in case of 429 rate limit
    model_cascade = [
        model,
        "llama-3.3-70b-versatile"
    ]
    
    # ensure uniqueness while preserving order
    try_models = []
    for m in model_cascade:
        if m not in try_models:
            try_models.append(m)

    last_exception = None
    
    for current_model in try_models:
        try:
            # We enforce a strict upper bound of 1024 max_tokens to prevent 413 limits during concurrent calls
            safe_max_tokens = min(max_tokens, 1024)
            
            response = await client.chat.completions.create(
                model=current_model,
                messages=messages,
                max_tokens=safe_max_tokens,
            )
            if current_model != model:
                logger.info(f"Successfully fell back to model {current_model} after errors.")
            return response.choices[0].message.content
            
        except Exception as e:
            error_msg = str(e).lower()
            if "rate limit" in error_msg or "too large" in error_msg or "rate_limit_exceeded" in error_msg or "413" in error_msg or "429" in error_msg:
                logger.warning(f"Capacity limit hit for {current_model}. Attempting fallback. Error: {e}")
                last_exception = e
                continue
            else:
                logger.error(f"Fatal error calling Groq API with {current_model}: {e}")
                last_exception = e
                break

    # If all cascade models failed, raise the last exception
    raise last_exception

