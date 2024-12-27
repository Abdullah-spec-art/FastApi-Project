from pydantic import BaseModel, EmailStr
from typing import Optional,Generic, TypeVar

# Define a generic type variable
T = TypeVar("T")

class Response(BaseModel, Generic[T]):
    data: Optional[T]
    message: str

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    name: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Data(BaseModel):
    name: Optional[str]=None
    email: Optional[str]=None
    access_token: Optional[str]=None

class UserEmailSchema(BaseModel):
    email: EmailStr

class OTPVerification(BaseModel):
    email: EmailStr
    otp: str

class NewPassword(BaseModel):
    new_password: str



    class Config:
        arbitrary_types_allowed = True
