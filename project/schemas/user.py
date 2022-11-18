from pydantic import BaseModel, Field


class User(BaseModel):
    chat_id: str = Field(...)
