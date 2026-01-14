"""
Clerk JWT Authentication for FastAPI
Verifies Clerk session tokens and extracts user_id
"""
import os
from fastapi import Request, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import httpx
from jose import jwt, JWTError
from functools import lru_cache
import time

security = HTTPBearer()

# Clerk configuration
CLERK_SECRET_KEY = os.getenv("CLERK_SECRET_KEY")
CLERK_ISSUER = os.getenv("CLERK_ISSUER")  # Must be set in .env, e.g. https://dear-turtle-59.clerk.accounts.dev

# Cache for Clerk's JWKS (JSON Web Key Set)
_jwks_cache = {"keys": None, "fetched_at": 0}
JWKS_CACHE_TTL = 3600  # 1 hour


async def get_clerk_jwks():
    """Fetch Clerk's public keys for JWT verification."""
    if not CLERK_ISSUER:
        print("ERROR: CLERK_ISSUER not configured in .env file!")
        raise HTTPException(status_code=500, detail="Auth not configured: CLERK_ISSUER missing")
    
    now = time.time()
    if _jwks_cache["keys"] and (now - _jwks_cache["fetched_at"]) < JWKS_CACHE_TTL:
        return _jwks_cache["keys"]
    
    # Clerk's JWKS endpoint
    jwks_url = f"{CLERK_ISSUER}/.well-known/jwks.json"
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(jwks_url)
            response.raise_for_status()
            _jwks_cache["keys"] = response.json()["keys"]
            _jwks_cache["fetched_at"] = now
            return _jwks_cache["keys"]
        except Exception as e:
            print(f"Error fetching JWKS: {e}")
            if _jwks_cache["keys"]:
                return _jwks_cache["keys"]  # Use stale cache if available
            raise HTTPException(status_code=500, detail="Failed to fetch auth keys")


def verify_clerk_token(token: str, jwks: list) -> dict:
    """Verify Clerk JWT token and return payload."""
    try:
        # Get the key ID from the token header
        unverified_header = jwt.get_unverified_header(token)
        kid = unverified_header.get("kid")
        
        # Find the matching key
        rsa_key = None
        for key in jwks:
            if key.get("kid") == kid:
                rsa_key = key
                break
        
        if not rsa_key:
            raise HTTPException(status_code=401, detail="Unable to find matching key")
        
        # Verify and decode the token
        payload = jwt.decode(
            token,
            rsa_key,
            algorithms=["RS256"],
            options={
                "verify_aud": False,
                "leeway": 60  # Tolerate up to 60 seconds of clock skew/delay
            }
        )
        
        return payload
        
    except JWTError as e:
        print(f"JWT verification error: {e}")
        raise HTTPException(status_code=401, detail="Invalid token")


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> str:
    """
    FastAPI dependency to get the current user ID from Clerk JWT.
    
    Usage:
        @app.get("/api/products")
        async def list_products(user_id: str = Depends(get_current_user)):
            return get_products_for_user(user_id)
    """
    token = credentials.credentials
    
    try:
        jwks = await get_clerk_jwks()
        payload = verify_clerk_token(token, jwks)
        
        # Clerk uses 'sub' for user ID
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="User ID not found in token")
        
        return user_id
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Auth error: {e}")
        raise HTTPException(status_code=401, detail="Authentication failed")


async def get_optional_user(request: Request) -> str | None:
    """
    Optional auth - returns user_id if token present, None otherwise.
    Useful for endpoints that work differently for authenticated vs anonymous users.
    """
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return None
    
    try:
        token = auth_header.split(" ")[1]
        jwks = await get_clerk_jwks()
        payload = verify_clerk_token(token, jwks)
        return payload.get("sub")
    except:
        return None
