from pydantic import BaseModel, EmailStr
from typing import Optional


class addtodo(BaseModel):
    title:str
    description:str

class ResponseToDo(BaseModel):
    title: str
    description: str

class UpdateTodo(BaseModel):
    title: Optional[str]=None
    description: Optional[str]=None

class TodoData(BaseModel):
    title: Optional[str]=None
    description: Optional[str]=None