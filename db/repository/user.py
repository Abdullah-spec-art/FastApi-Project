from sqlmodel import Session
from db.models.user import  User
from passlib.context import CryptContext
from schemas.user import UserCreate, UserLogin,Response,OTPVerification,UserEmailSchema,Data
from fastapi import HTTPException, status
import random
import smtplib
from sqlmodel import select
from datetime import datetime,timedelta,timezone
from email.mime.text import MIMEText
import uuid
from db.repository.jwt import create_access_token

# Configure Passlib to use bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

#Get user by email   
def by_email(db: Session, email: str):
    stmt = select(User).where(User.email == email)
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
        otp=generate_otp()
        email_verified=False
        db_user = User(name=user.name, email=user.email, password=hashed_password,otp=otp,email_verified=email_verified)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        # Send OTP to user's email 
        send_otp_to_email(db_user.email, db_user.otp)
        data=Data(
            name=user.name,
            email=user.email
        )
        return Response[Data](data=data,message="User created successfully. Please verify the OTP sent to your email.")
    

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
        otp_created=datetime.now(timezone.utc)
        user.otp_created=otp_created
        user.otp=otp
        db.add(user)
        db.commit()
        db.refresh(user)
        send_otp_to_email(user.email, user.otp)
        return Response[Data](data=None,message="Email not verified. The new OTP has been to your email")
    
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=timedelta(minutes=30)
        )
    data=Data(
        name=user.name,
        email=user.email,
        access_token=access_token
    )
    return Response[Data](data=data,message="Login successful")




def send_otp_to_email(email:str, otp: str):
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
    message["To"] = email
    message["Subject"] = "OTP Verification for Your App"
# Connect to Gmail's SMTP server
    with smtplib.SMTP(mail_server, mail_port) as server:
        server.starttls()  # Upgrade the connection to a secure encrypted SSL/TLS connection
        server.login(mail_username, mail_password)  # Login using your email and app-specific password
        server.sendmail(mail_from, email, message.as_string()) 



def verify_otp(db: Session, user:OTPVerification):
    # Find user by email
    db_user = by_email(db,user.email)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found.")

    otp_expires_time = db_user.otp_created + timedelta(minutes=5)
    if datetime.now() > otp_expires_time:
        db_user.otp=None
        db.commit()
        raise HTTPException(status_code=401, detail="OTP has expired")
    
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
def forget_pass(db:Session, user:UserEmailSchema):
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
def new_pass(db:Session, user=UserLogin):
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

# Get a user by ID
def get_user(db: Session, user_id: uuid.UUID):
    stmt = select(User).where(User.id == user_id)
    result = db.exec(stmt).one_or_none()
    return result

#Get user by ID
def get_user_id(db:Session,user_id:uuid.UUID):
    db_user=get_user(db,user_id)
    if db_user is None:
        raise HTTPException(status_code=401, detail="User not found")
    data=Data(
            name=db_user.name,
            email=db_user.email
            )
    return Response[Data](data=data,message="User found successfully")

#Delete user by Email
def delete_user_by_email(db:Session, user:UserEmailSchema):
    db_user=by_email(db, user.email)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found") 
    db.delete(db_user)
    db.commit()
    return {"message":"User deleted successfully."}

#delete user by ID
def delete_user_id(db:Session,user_id:uuid.uuid1):
    db_user=get_user(db,user_id)
    if db_user is None:
        raise HTTPException(status_code=401, detail="User not found")
    db.delete(db_user)
    db.commit()
    return {"message":"User deleted successfully"}