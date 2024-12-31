from fastapi import HTTPException, status,Depends
from core.config import ALGORITHM,SECRET_KEY
from fastapi.security import HTTPBearer,HTTPBasicCredentials
from jose import jwt, JWTError,ExpiredSignatureError
from passlib.context import CryptContext
from datetime import datetime,timedelta,timezone
from sqlmodel import Session
from db.session import get_db
from typing import Union
from sqlmodel import select
from db.models.user import  User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


#jwt implement
REFRESH_SECRET_KEY =""
ACCESS_TOKEN_EXPIRE_MINUTES = 30  # Token validity duration
REFRESH_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7 # 7 days
# Define the OAuth2PasswordBearer scheme
security=HTTPBearer()

def create_access_token(data: dict, expires_delta: Union[timedelta, None] = None):
    encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta if expires_delta else timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    encode.update({"exp": expire})  # Add expiry to the token
    encoded_jwt=jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(db:Session=Depends(get_db),credentials:HTTPBasicCredentials=Depends(security) ):
    token=credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email:str=payload.get("sub")
        if email is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Email not found")
    except ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has expired")
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    stmt = select(User).where(User.email == email)
    user = db.exec(stmt).one_or_none()
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid user or token")
    print(f"User ID: {user.id}") 
    return user
