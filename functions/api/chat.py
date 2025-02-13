import os
import json
from openai import OpenAI
from anthropic import Anthropic
import httpx

async def onRequest(context):
    # Get request method
    if context.request.method == "OPTIONS":
        return new_response({"status": "ok"}, 200)
    
    if context.request.method != "POST":
        return new_response({"error": "Method not allowed"}, 405)

    try:
        # Parse request body
        body = await context.request.json()
        message = body.get("message")
        model = body.get("model")

        if not message or not model:
            return new_response({"error": "Missing message or model"}, 400)

        # Handle different models
        if model == "gpt":
            client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": message}]
            )
            return new_response({"response": response.choices[0].message.content})

        elif model == "claude":
            client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
            response = client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=1024,
                messages=[{"role": "user", "content": message}]
            )
            return new_response({"response": response.content[0].text})

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
                return new_response({"response": result["choices"][0]["message"]["content"]})
        else:
            return new_response({"error": "Invalid model specified"}, 400)

    except Exception as e:
        return new_response({"error": str(e)}, 500)

def new_response(body, status=200):
    return Response(
        json.dumps(body),
        status=status,
        headers={
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "https://somefar.com",
            "Access-Control-Allow-Methods": "POST, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type",
        }
    ) 