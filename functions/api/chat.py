from typing import Dict, Any
import os
import json
from openai import OpenAI
from anthropic import Anthropic
import httpx

def create_response(body: Dict[str, Any], status: int = 200) -> Dict[str, Any]:
    return {
        "body": json.dumps(body),
        "statusCode": status,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "https://somefar.com",
            "Access-Control-Allow-Methods": "POST, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type",
        }
    }

async def onRequest(context):
    # Handle preflight requests
    if context.request.method == "OPTIONS":
        return create_response({"status": "ok"}, 200)
    
    # Only allow POST requests
    if context.request.method != "POST":
        return create_response({"error": "Method not allowed"}, 405)

    try:
        # Parse request body
        body = await context.request.json()
        message = body.get("message")
        model = body.get("model")

        if not message or not model:
            return create_response({"error": "Missing message or model"}, 400)

        # Handle different models
        if model == "gpt":
            client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": message}]
            )
            return create_response({"response": response.choices[0].message.content})

        elif model == "claude":
            client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
            response = client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=1024,
                messages=[{"role": "user", "content": message}]
            )
            return create_response({"response": response.content[0].text})

        elif model == "deepseek":
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.deepseek.com/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {os.environ.get('DEEPSEEK_API_KEY')}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "deepseek-chat",
                        "messages": [{"role": "user", "content": message}]
                    }
                )
                result = response.json()
                return create_response({"response": result["choices"][0]["message"]["content"]})
        else:
            return create_response({"error": "Invalid model specified"}, 400)

    except Exception as e:
        return create_response({"error": str(e)}, 500) 