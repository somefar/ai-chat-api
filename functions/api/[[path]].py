from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import os
import openai
from anthropic import Anthropic
import httpx

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://somefar.com", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str
    model: str  # "gpt", "claude", or "deepseek"
    conversation_id: Optional[str] = None

async def handle_chat(request: ChatRequest):
    try:
        if request.model == "gpt":
            client = openai.Client(api_key=os.environ.get("OPENAI_API_KEY"))
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": request.message}]
            )
            return {"response": response.choices[0].message.content}
            
        elif request.model == "claude":
            client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
            response = client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=1024,
                messages=[{"role": "user", "content": request.message}]
            )
            return {"response": response.content[0].text}
            
        elif request.model == "deepseek":
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.deepseek.com/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {os.environ.get('DEEPSEEK_API_KEY')}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "deepseek-chat",
                        "messages": [{"role": "user", "content": request.message}]
                    }
                )
                result = response.json()
                return {"response": result["choices"][0]["message"]["content"]}
        else:
            return {"error": "Invalid model specified"}, 400
            
    except Exception as e:
        return {"error": str(e)}, 500

@app.get("/api/health")
async def health_check():
    return {"status": "healthy"}

@app.post("/api/chat")
async def chat_endpoint(request: Request):
    try:
        data = await request.json()
        chat_request = ChatRequest(**data)
        return await handle_chat(chat_request)
    except Exception as e:
        return {"error": str(e)}, 400

async def onRequest(context):
    return app 