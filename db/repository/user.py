from sqlmodel import Session
from db.models.user import  User
from passlib.context import CryptContext
from schemas.user import UserCreate, UserLogin,PasswordReset,DeleteUser,Response,OTPVerification,Forgetpass,Data
from fastapi import HTTPException, status
import random
import smtplib
from sqlmodel import select
from datetime import datetime,timedelta,timezone
from email.mime.text import MIMEText
import uuid
from db.repository.jwt import ACCESS_TOKEN_EXPIRE_MINUTES,create_access_token

# Configure Passlib to use bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """Hash a plain text password."""
    return pwd_context.hash(password)

 #Get user by email   
def by_email(db: Session, email: str):
    stmt = select(User).where(User.email == email)
    result = db.exec(stmt).one_or_none()
    return result

# Get a user by ID
def get_user(db: Session, user_id: uuid.UUID):
    stmt = select(User).where(User.id == user_id)
    result = db.exec(stmt).one_or_none()
    return result

def generate_otp():
    return str(random.randint(100000, 999999))

#Create user (for signup)
def create_user(db: Session, user: UserCreate): 
        existing_user=by_email(db, user.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User already exists"
            )
        hashed_password = hash_password(user.password)
        otp=str(random.randint(100000, 999999))
        email_verified=False
        db_user = User(name=user.name, email=user.email, password=hashed_password,otp=otp,email_verified=email_verified)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        # Send OTP to user's email  
        send_otp_to_email(user, otp)
        data=Data(
            name=user.name,
            email=user.email
        )
        return Response[Data](data=data,message="User created successfully. Please verify the OTP sent to your email.")
    


#Only for reset password(make a new password)
def reset_password(db: Session, user=PasswordReset):
    db_user = by_email(db, user.email)
    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    db_user.password = hash_password(user.new_password)  
    db.commit()
    db.refresh(db_user)
    return Response(name=db_user.name,email=db_user.email,message="Password reset successfully.")


#for login user
def login_user(db: Session, user_login: UserLogin):
    user = by_email(db, user_login.email)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    if not pwd_context.verify(user_login.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    if user.email_verified is False:
        otp=generate_otp()
        email_verified=False 
        user.otp=otp
        user.email_verified=email_verified
        db.add(user)
        db.commit()
        db.refresh(user)
        send_otp_to_email(user, otp)
        return Response[Data](data=None,message="Email not verified. The new OTP has been to your email")
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=timedelta(minutes=30)
        )
    data=Data(
        name=user.name,
        email=user.email,
        access_token=access_token
    )
    return Response[Data](data=data,message="Login successful")


#Delete user by Email
def delete_user_by_email(db:Session, user:DeleteUser):
    db_user=by_email(db, user.email)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found") 
    db.delete(db_user)
    db.commit()
    return {"message":"User deleted successfully."}
    



def send_otp_to_email(user: UserCreate, otp: str):
    mail_username = "hashbot0@gmail.com"  # Replace with your email (sender's email)
    mail_password = "hplvsvyulxhzzzqt"  # Replace with your app-specific password
    mail_from = "hashbot0@gmail.com"
    mail_from_name = "FastApi Email"
    mail_server = "smtp.gmail.com"
    mail_port = 587  # Gmail SMTP port
    '''MAIL_TLS=True,
    MAIL_SSL=False,
    USE_CREDENTIALS=True'''

    # Create the email content
    message = MIMEText(f"Your OTP is: {otp}")
    message["From"] = mail_from
    message["To"] = user.email
    message["Subject"] = "OTP Verification for Your App"
# Connect to Gmail's SMTP server
    with smtplib.SMTP(mail_server, mail_port) as server:
        server.starttls()  # Upgrade the connection to a secure encrypted SSL/TLS connection
        server.login(mail_username, mail_password)  # Login using your email and app-specific password
        server.sendmail(mail_from, user.email, message.as_string()) 


def is_otp_expired(otp_created: datetime, expiry_duration_minutes: int = 5) -> bool:
    """
    Checks if the OTP is expired. Default expiry is 5 minutes.
    """
    expiry_time = otp_created + timedelta(minutes=expiry_duration_minutes)
    return datetime.now() > expiry_time


def verify_otp(db: Session, user:OTPVerification):
    # Find user by email
    db_user = by_email(db,user.email)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found.")

    # Check if OTP matches
    if db_user.otp != user.otp:
        raise HTTPException(status_code=400, detail="Invalid OTP.")
    db_user.email_verified=True
    db_user.otp = None
    db.commit()
    db.refresh(db_user)
    # Generate access token
    token = create_access_token(
            data={"sub": user.email}, expires_delta=timedelta(minutes=30)
            ) 
    data=Data(
            name=db_user.name,
            email=db_user.email,
            access_token=token
        )

    return Response[Data](data=data,message= "OTP verification completed successfully. Token generated.")
    

#Forget password and generate OTP to make new password
def forget_pass(db:Session, user:Forgetpass):
    db_user = by_email(db,user.email)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found.")
    otp=generate_otp()
    otp_created= datetime.now()  # Save the timestamp of OTP creation
    db_user.otp=otp
    db_user.otp_created=otp_created
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    send_otp_to_email(user, otp)
    data=Data(
            name=db_user.name,
            email=db_user.email
            )
    return Response[Data](data=data,message="OTP has been send to your email.")

#Make a new password after otp verification
def new_pass(db:Session, user=PasswordReset):
    db_user = by_email(db,user.email)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found.")
    old_otp=db_user.otp
    if old_otp is not None:
        raise HTTPException(
            status_code=400, 
            detail="OTP not verified. Please verify your OTP."
            )
    db_user.password = hash_password(user.new_password)  
    db.commit()
    db.refresh(db_user)

    data=Data(
            name=db_user.name,
            email=db_user.email
            )

    return Response[Data](data=data,message="Password reset successfully.")




def authenticate_user(db, email:str,password:str):
    user = by_email(db, email)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    if not pwd_context.verify(password,user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials")
    return user

def generate_access_token(db:Session, form_data:UserLogin):
    user = authenticate_user(db,form_data.email,form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires

    )
    return {"access_token": access_token, "token_type": "bearer"}