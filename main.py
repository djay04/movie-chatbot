from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from fastapi.security import OAuth2PasswordBearer
from auth import verify_token
import re
from gemini_wrapper.client import MovieBot
from database import init_db, create_user, get_user_by_email
from auth import hash_password, create_token, verify_password, verify_token


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def get_current_user(token: str = Depends(oauth2_scheme)):

    print(f"Received token: {token}")
    user_id = verify_token(token)
    return user_id

class ChatRequest(BaseModel):
    user_message: str

class signupRequest(BaseModel):

    email: str
    password: str

class loginRequest(BaseModel):

    email: str
    password: str

app = FastAPI()

@app.on_event("startup")
def startup():

    init_db()


@app.get("/")
def root():

    return {"Success": "Root is working"}

@app.post("/signup")
def signup(req: signupRequest):

    # Validates w/ regex, hashes password, saves user, returns token

    email_format = r"^[\w\.-]+@[\w\.-]+\.\w+$"

    if not re.match(email_format, req.email):
        raise HTTPException(status_code=400, detail="Email must be proper email format")

    password_format = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*[0-9]).{8,}$"

    if not re.match(password_format, req.password):
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters with one uppercase and one digit")
    
    hash = hash_password(req.password)

    user_id = create_user(req.email, hash)

    token = create_token(user_id)

    return {"access_token": token, "token_type": "bearer"}



@app.post("/login")
def login(req: loginRequest):

    # looks up user, verifies password, returns token

    try:

        user, password = get_user_by_email(req.email)

        if not verify_password(req.password, password):
            raise ValueError(f"Password is incorrect")
        
        token = create_token(user)
        return {"access_token": token, "token_type": "bearer"}
         
    except HTTPException:
        raise
    
    except Exception as e:

        raise HTTPException(status_code=500, detail=f"Error logging in: {str(e)}")




@app.post("/chat")
def chat(req: ChatRequest, user_id: int = Depends(get_current_user)):

    bot = MovieBot()

    response = bot.send_message(req.user_message)

    return response