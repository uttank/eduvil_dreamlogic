from fastapi import FastAPI, Request
from pydantic import BaseModel
from openai import OpenAI
from typing import Dict, List
# python-dotenv를 사용하여 환경변수 로드
from dotenv import load_dotenv
import os
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles


app = FastAPI()
# .env 파일에서 OpenAI API 키를 로드
load_dotenv()
_key = os.getenv("OPENAI_API_KEY")
if not _key:
    raise ValueError("OPENAI_API_KEY 환경 변수가 설정되어 있지 않습니다.")
else:
    client = OpenAI(api_key=_key) # Or it will pick from environment variable

# 세션별 대화 저장용 (메모리 기반 예시)
from openai.types.chat import ChatCompletionMessageParam

session_store: Dict[str, List[ChatCompletionMessageParam]] = {}

class ChatRequest(BaseModel):
    session_id: str
    user_input: str

@app.post("/chat")
async def chat(req: ChatRequest):
    session_id = req.session_id
    user_input = req.user_input

    if session_id not in session_store:
        session_store[session_id] = [
            {"role": "system", "content": "You are a helpful assistant."}  # type: ChatCompletionMessageParam
        ]

    messages = session_store[session_id]
    messages.append({"role": "user", "content": user_input})  # type: ChatCompletionMessageParam

    # GPT 응답 생성
    response = client.chat.completions.create(
        model="gpt-4.1",
        messages=messages
    )

    assistant_reply = response.choices[0].message.content
    messages.append({"role": "assistant", "content": assistant_reply})  # type: ChatCompletionMessageParam

    return {"reply": assistant_reply}

templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/chat-ui", response_class=HTMLResponse)
async def chat_ui(request: Request):
    return templates.TemplateResponse("chat.html", {"request": request})

@app.get("/")
async def root():
    return HTMLResponse('<script>window.location.replace("/chat-ui");</script>', status_code=307)
