from db.repository.jwt import get_current_user
from db.session import get_db
from sqlmodel import Session
from fastapi import HTTPException, status,Depends
from schemas.todo import Addtodo,ResponseToDo,TodoUpdateData
from schemas.user import Response
from db.models.todo import ToDo
import uuid
from sqlmodel import select,or_
from typing import Optional

#Create a new Todo
def add_todo(todo:Addtodo, db:Session=Depends(get_db),user=Depends(get_current_user)):
        created_by=user.id
        new_todo = ToDo(title=todo.title, description=todo.description,created_by=created_by)
        db.add(new_todo)
        db.commit()
        db.refresh(new_todo)
        data=TodoUpdateData(
            title=new_todo.title,
            description=new_todo.description
        )
        print(f"created at: {new_todo.created_at}")
        return Response[TodoUpdateData](data=data,message="Todo created successfully")

#Get todo user by ID
def get_todo_user(db: Session, todo_id: uuid.UUID,user_id: uuid.UUID):
    stmt = select(ToDo).where(ToDo.id == todo_id,ToDo.created_by==user_id)
    result = db.exec(stmt).one_or_none()
    return result

#update todo 
def update_todo(todo_id:uuid.UUID,todo:TodoUpdateData, db:Session=Depends(get_db),user=Depends(get_current_user)):
    db_todo=get_todo_user(db,todo_id,user.id)
    if not db_todo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found or unauthorized.")
    if todo.title is not None:
        db_todo.title = todo.title
    if todo.description is not None:
        db_todo.description = todo.description
    db.commit()
    db.refresh(db_todo)
    data=TodoUpdateData(
            title=db_todo.title,
            description=db_todo.description
        )
    print(f"Updated at: {db_todo.updated_at}")
    return Response[TodoUpdateData](data=data,message="Todo updated successfully")
    

#Get todo by ID
def get_todo(todo_id:uuid.UUID, db:Session=Depends(get_db),user=Depends(get_current_user)):
    db_todo=get_todo_user(db,todo_id,user.id)
    if not db_todo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found or unauthorized.")
    data=TodoUpdateData(
            title=db_todo.title,
            description=db_todo.description
        )
    return Response[TodoUpdateData](data=data,message="Find ToDo successful")

#Get all todo and do search
def get_all_todo(search:Optional[str],db:Session=Depends(get_db),user=Depends(get_current_user)):
    stmt = select(ToDo).where(ToDo.created_by == user.id)
    if search:
        stmt = stmt.where(or_(ToDo.title.ilike(f"%{search}%"), ToDo.description.ilike(f"%{search}%")))
    todos = db.exec(stmt).all()
    return [ResponseToDo(title=todo.title,description=todo.description)for todo in todos]


#Delete todo by ID
def del_todo(todo_id:uuid.UUID,db:Session=Depends(get_db),user=Depends(get_current_user)):
    db_todo=get_todo_user(db,todo_id,user.id)
    if db_todo is None:
        raise HTTPException(status_code=404, detail="todo not found") 
    db.delete(db_todo)
    db.commit()
    return {"message":"ToDo deleted successfully."}
