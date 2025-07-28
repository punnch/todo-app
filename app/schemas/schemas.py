from pydantic import BaseModel, Field, ConfigDict # ConfigDict for Pydantic v2
from datetime import datetime

class TaskBase(BaseModel):
    text: str = Field(min_length=1, max_length=255, strip_whitespace=True)

# The user only provides the "text" for the task
# id, done, created_at're handled by the DB
class TaskCreate(TaskBase):
    pass

class TaskUpdateText(TaskBase):
    pass

# Schema for the API response
class TaskResponse(TaskBase):
    id: int
    done: bool
    created_at: datetime

    # Configuration for Python to work with SQLAlchemy ORM models
    # This tells pydantic read data not from a dict, but from the attributes
    model_config = ConfigDict(from_attributes=True)

# Schema for simple message responses
class TaskMessage(BaseModel):
    message: str