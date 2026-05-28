from fastapi import Request, HTTPException, status
from .jwt_handler import decode_access_token

async def get_current_user(request: Request) -> dict:
    """Retrieve and validate the JWT from the request cookies or authorization header.
    
    Raises 401 Unauthorized if authentication fails.
    """
    token = request.cookies.get("access_token")
    
    # Fallback to Authorization header if cookies are not used (e.g. CLI or API clients)
    if not token:
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
            
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication token is missing. Please log in."
        )
        
    payload = decode_access_token(token)
    if not payload or "sub" not in payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session has expired or token is invalid. Please log in again."
        )
        
    return {
        "username": payload["sub"],
        "role": payload.get("role", "network_operator")
    }
