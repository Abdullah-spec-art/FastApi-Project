from db.models.table_model import TableModel
from sqlmodel import Field, Relationship, String
from datetime import datetime, timezone
import uuid
from typing import TYPE_CHECKING
from sqlalchemy import event

class ToDo(TableModel, table=True):  # Inherit from TableModel
    __tablename__ = 'ToDos'
    title: str = Field(nullable=False)  # Title of the To-Do
    description: str = Field(nullable=True)  # Optional description
    created_at: datetime = Field(default=datetime.now(timezone.utc))  # Timestamp when created
    updated_at: datetime = Field(default=datetime.now(timezone.utc),)  # Timestamp updated on modification
    created_by: uuid.UUID = Field(foreign_key="Users.id",ondelete="CASCADE", nullable=False)
    
# Add Listener for Automatically Updating `updated_at`
@event.listens_for(ToDo, "before_update")
def update_updated_at(mapper, connection, target):
     target.updated_at = datetime.now(timezone.utc)

