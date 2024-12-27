from db.models.table_model import TableModel
from sqlmodel import Field, Relationship
from datetime import datetime, timezone
from typing import List, TYPE_CHECKING



class User(TableModel, table=True):
    __tablename__ = 'Users'
    name: str = Field(nullable=False)  # Directly using str
    email: str = Field(nullable=False, unique=True, index=True)  # Directly using str
    password: str = Field(nullable=False)  # Directly using str
    otp: str = Field(nullable=True)  # Directly using str
    otp_created: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))  # Directly using datetime
    email_verified: bool = Field(default=False)  # Directly using bool



