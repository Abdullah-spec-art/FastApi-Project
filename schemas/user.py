from pydantic import BaseModel, EmailStr
from typing import Optional,Generic
from typing import Generic, TypeVar, Optional
# Define a generic type variable
T = TypeVar("T")

class Response(BaseModel, Generic[T]):
    data: Optional[T]
    message: str

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    name: str

class UserResponse(BaseModel):
    email: EmailStr
    name: str
    
class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Data(BaseModel):
    name: Optional[str]=None
    email: Optional[str]=None
    access_token: Optional[str]=None
'''
class Response(BaseMod,):
    data: Data
    message:str'''
    
class PasswordReset(BaseModel):
    email: EmailStr
    new_password: str

class UserUpdate(BaseModel): 
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None

class DeleteUser(BaseModel):
    email: str

class Forgetpass(BaseModel):
    email: str

class OTPVerification(BaseModel):
    email: EmailStr
    otp: str
    
'''class Response(BaseModel):
    name: str
    email: str
    message:str'''

class NewPassword(BaseModel):
    new_password: str

class tokenallinfo(BaseModel):
    name: str
    email: EmailStr
    message:str
    access_token:str
    token_type:str

class Usertoken(BaseModel):
    name: str
    email: str

class TokenData(BaseModel):
    email: str

class tokeninf(BaseModel):
    access_token:str
    token_type:str


    class Config:
        arbitrary_types_allowed = True
