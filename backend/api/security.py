from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from pydantic import BaseModel

from core.config import settings
from domain.entities import User
from domain.repositories import UserRepository
from .dependencies import get_user_repository

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/token")

class TokenData(BaseModel):
    email: str | None = None
    tenant_id: str | None = None

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    user_repo: UserRepository = Depends(get_user_repository)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        tenant_id: str = payload.get("tenant_id")
        if email is None or tenant_id is None:
            raise credentials_exception
        token_data = TokenData(email=email, tenant_id=tenant_id)
    except JWTError:
        raise credentials_exception
    
    user = await user_repo.get_by_email(email=token_data.email)
    if user is None:
        raise credentials_exception
    
    if str(user.tenant_id) != token_data.tenant_id:
        raise credentials_exception
        
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

