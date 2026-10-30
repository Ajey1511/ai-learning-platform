from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.db import get_db
from app.models import User
from app.security import decode_access_token

oauth2 = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def current_user(token: str = Depends(oauth2), db: Session = Depends(get_db)) -> User:
    subject = decode_access_token(token)
    user = db.get(User, int(subject)) if subject and subject.isdigit() else None
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="Invalid or expired access token")
    return user


def admin_user(user: User = Depends(current_user)) -> User:
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Administrator access required")
    return user
