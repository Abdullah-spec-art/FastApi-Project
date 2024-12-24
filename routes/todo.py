from db.repository.todo import add_todo,update_todo,get_todo,get_all_todo,del_todo
from typing import List
from sqlmodel import Session
from db.repository.jwt import get_current_user
from db.session import get_db
from schemas.todo import addtodo,ResponseToDo,UpdateTodo
from db.models.user import User
from fastapi import APIRouter, Depends
import uuid
from typing import Optional
from schemas.user import Response

router = APIRouter()

@router.post("/add-todo",response_model=Response)
def create_todo(todo:addtodo,db:Session=Depends(get_db),user=Depends(get_current_user),):
    return add_todo(todo=todo, db=db, user=user)

@router.put("/todo-update/{todo_id}",response_model=Response)
def update_todo_route(todo_id:uuid.UUID,todo:UpdateTodo,db:Session=Depends(get_db),user=Depends(get_current_user),):
    return update_todo(todo_id=todo_id,todo=todo, db=db, user=user)

@router.get("/get-todo/{todo_id}",response_model=Response)
def get_todo_route(todo_id:uuid.UUID,db:Session=Depends(get_db),user=Depends(get_current_user),):
    return get_todo(todo_id=todo_id, db=db, user=user)

@router.get("/get-all-todos", response_model=List[ResponseToDo])
def get_all_todos_route(search:Optional[str],db:Session = Depends(get_db), user=Depends(get_current_user)):
    return get_all_todo(search=search,db=db, user=user)

@router.delete("/delete-todo/{todo_id}", response_model=None)
def delete_todo_route(todo_id:uuid.UUID,db:Session=Depends(get_db),user=Depends(get_current_user)):
    return del_todo(todo_id=todo_id,db=db,user=user)
