from fastapi import APIRouter, HTTPException, status

router = APIRouter(prefix="/auth", tags=["Auth"])

HARDCODED_USERS = {"demo": "demo123"}


@router.post("/login")
async def login(username: str, password: str):
    """
    Simple hardcoded login endpoint.
    Expected credentials: username="demo", password="demo123"
    """
    if username in HARDCODED_USERS and HARDCODED_USERS[username] == password:
        return {"access_token": "demo-token-123"}
    
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid credentials"
    )


@router.post("/logout")
async def logout():
    """
    Simple logout endpoint (stateless).
    """
    return {"message": "logged out"}
