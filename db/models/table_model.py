from sqlmodel import SQLModel, Field
import uuid
 
class TableModel(SQLModel):
    id: uuid.UUID = Field(
        default_factory=uuid.uuid4, 
        primary_key=True, 
        nullable=False, 
        index=True, 
        unique=True
    )
