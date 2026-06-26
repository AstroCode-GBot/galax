import datetime
from typing import Optional
import bcrypt  # সরাসরি নেটিভ এবং ফাস্ট মডার্ন লাইব্রেরি
import jwt
from fastapi import Request, HTTPException, status
from app.config import settings

def hash_password(password: str) -> str:
    # স্ট্রিংকে বাইটে কনভার্ট করে সল্ট দিয়ে হ্যাশ করা
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return bcrypt.checkpw(
            plain_password.encode('utf-8'), 
            hashed_password.encode('utf-8')
        )
    except Exception:
        return False

def create_admin_token(username: str) -> str:
    current_time = datetime.datetime.now(datetime.timezone.utc)
    payload = {
        "sub": username,
        "exp": current_time + datetime.timedelta(hours=8),
        "iat": current_time
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")

def verify_admin_token(token: str) -> Optional[str]:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        return payload.get("sub")
    except jwt.PyJWTError:
        return None

async def get_current_admin(request: Request) -> str:
    token = request.cookies.get("admin_session")
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Access Denied: No active administrative session."
        )
    username = verify_admin_token(token)
    if not username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Access Denied: Invalid or expired security token."
        )
    return username
