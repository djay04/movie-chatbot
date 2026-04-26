from fastapi import FastAPI
from pydantic import BaseModel
from gemini_wrapper.client import MovieBot
from database import init_db


class ChatRequest(BaseModel):
    user_message: str
    user_id: int

app = FastAPI()

@app.on_event("startup")
def startup():

    init_db()


@app.get("/")
def root():

    return {"Success": "Root is working"}

@app.post("/chat")
def chat(req: ChatRequest):

    bot = MovieBot()

    response = bot.send_message(req.user_message)

    return response