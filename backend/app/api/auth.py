from fastapi import APIRouter, Response, HTTPException, status
from ..auth.schemas import LoginRequest, UserResponse
from ..auth.jwt_handler import create_access_token

router = APIRouter(prefix="/auth", tags=["Authentication"])

# Mock credentials
MOCK_USERS = {
    "admin": {"password": "admin123", "role": "admin"},
    "nocuser": {"password": "noc123", "role": "network_operator"}
}

@router.post("/login")
async def login(payload: LoginRequest, response: Response):
    """Authenticate user credentials and set an httpOnly JWT cookie."""
    user = MOCK_USERS.get(payload.username)
    if not user or user["password"] != payload.password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid username or password"
        )
    
    # Create token
    token = create_access_token(data={"sub": payload.username, "role": user["role"]})
    
    # Set secure httpOnly cookie
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        secure=False,  # Set to True in production (requires HTTPS)
        samesite="lax",
        max_age=28800,  # 8 hours in seconds
        path="/"
    )
    
    return {
        "user": {
            "username": payload.username,
            "role": user["role"]
        }
    }

@router.post("/logout")
async def logout(response: Response):
    """Clear the access token cookie to log out the user."""
    response.delete_cookie(
        key="access_token",
        path="/",
        samesite="lax"
    )
    return {"message": "Logged out successfully"}
