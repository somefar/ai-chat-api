from fastapi import FastAPI, HTTPException
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

# Initialize API clients
def get_openai_client():
    return openai.Client(api_key=os.environ.get("OPENAI_API_KEY"))

def get_anthropic_client():
    return Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

@app.post("/api/chat")
async def chat(request: ChatRequest):
    try:
        if request.model == "gpt":
            client = get_openai_client()
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": request.message}]
            )
            return {"response": response.choices[0].message.content}
            
        elif request.model == "claude":
            client = get_anthropic_client()
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
            raise HTTPException(status_code=400, detail="Invalid model specified")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/health")
async def health_check():
    return {"status": "healthy"}

def onRequest(context):
    return app 