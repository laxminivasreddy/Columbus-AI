import asyncio
import sys
import os
sys.path.append(os.path.join(os.getcwd(), 'backend'))
from utils.llm import client

async def test_models():
    models = ["llama-3.1-8b-instant", "gemma2-9b-it", "mixtral-8x7b-32768", "llama3-8b-8192", "llama-3.3-70b-versatile"]
    for model in models:
        try:
            res = await client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": "hi"}],
                max_tokens=10
            )
            print(f"{model}: Success")
        except Exception as e:
            print(f"{model}: {e}")

asyncio.run(test_models())
