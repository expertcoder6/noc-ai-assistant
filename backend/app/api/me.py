from fastapi import APIRouter, Depends
from ..auth.middleware import get_current_user

router = APIRouter()

@router.get("/me")
async def read_me(current_user: dict = Depends(get_current_user)):
    """Return info about the currently authenticated user."""
    return current_user
