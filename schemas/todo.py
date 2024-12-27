from pydantic import BaseModel, EmailStr
from typing import Optional


class Addtodo(BaseModel):
    title:str
    description:str

class ResponseToDo(BaseModel):
    title: str
    description: str

class TodoUpdateData(BaseModel):
    title: Optional[str]=None
    description: Optional[str]=None