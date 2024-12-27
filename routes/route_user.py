from fastapi import APIRouter, Depends
from sqlmodel import Session
from db.repository.user import create_user, get_user,login_user,delete_user_by_email,verify_otp,forget_pass,new_pass,delete_user_id,get_user_id
from db.session import get_db
from schemas.user import UserCreate,UserLogin,Response,OTPVerification,UserEmailSchema
import uuid

router = APIRouter()


@router.get("/users/{user_id}", response_model=Response)
def get_user_by_id(user_id: uuid.UUID, db: Session = Depends(get_db)):
    db_user = get_user_id(db=db, user_id=user_id)
    return db_user

@router.post("/signup", response_model=Response)
def signup(user: UserCreate, db: Session = Depends(get_db)):
    db_user=create_user(db=db, user=user)
    return db_user

@router.post("/login",response_model=Response)
def login(user_login:UserLogin, db:Session=Depends(get_db)):
    user=login_user(db=db, user_login=user_login)
    return user

@router.post("/verify-otp",response_model=Response)
def otp_verification(user:OTPVerification, db:Session=Depends(get_db)):
    db_user=verify_otp(db=db, user=user)
    return db_user

@router.post("/forget-pass",response_model=Response)
def forget_password(user:UserEmailSchema, db:Session=Depends(get_db)):
    db_user=forget_pass(db=db, user=user)
    return db_user

@router.post("/new-password",response_model=Response)
def new_password(user:UserLogin, db:Session=Depends(get_db)):
    db_user=new_pass(db=db, user=user)
    return db_user

@router.delete("/delete-user-by-id/{user_id}",response_model=None)
def delete_user_by_id(user_id:uuid.UUID,db:Session=Depends(get_db)):
    db_user=delete_user_id(user_id=user_id,db=db)
    return db_user

@router.delete("/delete-user-by-email",response_model=None)
def delete_user(user:UserEmailSchema, db:Session=Depends(get_db)):
    db_user=delete_user_by_email(db=db,user=user)
    return db_user