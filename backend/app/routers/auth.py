from fastapi import APIRouter, HTTPException
from app.models.schemas import LoginRequest, LoginResponse
import hashlib
import secrets
router=APIRouter()
USERS={
    "admin": hashlib.sha256("adminpass".encode()).hexdigest(),
    "user1": hashlib.sha256("paasword1".encode()).hexdigest(),
}
active_tokens ={}
def hash_password(password:str)->str:
    return hashlib.sha256(password.encode()).haxdigit()
def verify_token(token:str)->str|None:
    return active_tokens.get(token)

@router.post("/login",response_model=LoginResponse)
async def login(request: LoginRequest):
    username =request.username.strip()
    password=request.password.strip()

    if not username or not password:
        raise HTTPException(status_code=400,detail="Username and password required")

    if username not in USERS:
        raise HTTPException(status_code=401,detail="Invalid credentials")

    token = secrets.token_hex(32)
    active_tokens[token] = username
    return LoginResponse(
         success =True,
         message=f"Welcome, {username}!",
         token=token    
        
     )
@router.post("/logout")
async def logout(token:str):
    if token in active_tokens:
         del active_tokens[token]
    return {"message":"Logged out successfully"}
