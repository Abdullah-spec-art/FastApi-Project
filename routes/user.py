from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from db.repository.user import create_user, get_user,reset_password,login_user,delete_user_by_email,verify_otp,forget_pass,new_pass,generate_access_token
from db.repository.jwt import get_current_user
from db.session import get_db
from schemas.user import UserCreate, UserResponse,PasswordReset,UserLogin,Response,DeleteUser,OTPVerification,Forgetpass,Usertoken,tokeninf
import uuid

router = APIRouter()


@router.get("/users/{user_id}", response_model=UserResponse)
def get_user_by_id(user_id: uuid.UUID, db: Session = Depends(get_db)):
    db_user = get_user(db=db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@router.post("/signup", response_model=Response)
def signup(user: UserCreate, db: Session = Depends(get_db)):
    return create_user(db=db, user=user)
    
@router.put("/update-password", response_model=Response)
def password_reset(data:PasswordReset, db:Session=Depends(get_db)):
    updated_user=reset_password(db=db, user=data)
    return updated_user

@router.post("/login",response_model=Response)
def login(user_login:UserLogin, db:Session=Depends(get_db)):
    user=login_user(db=db, user_login=user_login)
    return user

@router.delete("/delete-user",response_model=None)
def delete_user(user:DeleteUser, db:Session=Depends(get_db)):
    return delete_user_by_email(db=db,user=user)

@router.post("/verify-otp",response_model=Response)
def otp_verification(user:OTPVerification, db:Session=Depends(get_db)):
    db_user=verify_otp(db=db, user=user)
    return db_user

@router.post("/forget-pass",response_model=Response)
def forget_password(user:Forgetpass, db:Session=Depends(get_db)):
    db_user=forget_pass(db=db, user=user)
    return db_user

@router.post("/new-password",response_model=Response)
def new_password(user:PasswordReset, db:Session=Depends(get_db)):
    db_user=new_pass(db=db, user=user)
    return db_user

@router.get("/secure-endpoint",response_model=Usertoken)
def secure_endpoint(user:Usertoken=Depends(get_current_user), db: Session = Depends(get_db)):
    return user


@router.post("/token", response_model=tokeninf)
def login_for_access_token(form_data: UserLogin, db: Session = Depends(get_db)):
    return generate_access_token(db=db, form_data=form_data)


