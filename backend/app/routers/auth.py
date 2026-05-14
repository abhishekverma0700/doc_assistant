from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from app.services.database import authenticate_user, register_user

router = APIRouter(prefix="/auth", tags=["Auth"])

class LoginRequest(BaseModel):
    username: str
    password: str

class RegisterRequest(BaseModel):
    username: str
    password: str

DEMO_TOKEN = "demo-token-123"

@router.post("/register")
async def register(request: RegisterRequest):
    if len(request.username) < 3:
        raise HTTPException(status_code=400, detail="Username must be at least 3 characters")
    if len(request.password) < 4:
        raise HTTPException(status_code=400, detail="Password must be at least 4 characters")
    
    success = register_user(request.username, request.password)
    if not success:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    return {"message": "Registration successful"}

@router.post("/login")
async def login(request: LoginRequest):
    if not authenticate_user(request.username, request.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    
    return {"access_token": DEMO_TOKEN, "username": request.username}

@router.post("/logout")
async def logout():
    return {"message": "logged out"}