from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional


# 💡 Base settings shared by all Post schemas (things needed for input/output)
class PostBase(BaseModel):
    title: str               # ✅ Added missing title field
    content: str 
    published: bool = True


# 💡 Used STRICTLY for creating posts (No ID or timestamps allowed here)
class PostCreate(PostBase):
    pass 


class UserOut(BaseModel):
    id: int 
    email: EmailStr 
    created_at: datetime

    # ✅ Updated to Pydantic V2 standard configuration
    model_config = {"from_attributes": True}


# 💡 Used for fully reading a single Post back from the database
class Post(PostBase):
    id: int                  # ✅ Moved ID here because database generates it
    created_at: datetime 
    owner_id: int 
    owner: UserOut

    model_config = {"from_attributes": True}


class PostOut(BaseModel):
    Post: Post 
    votes: int 

    model_config = {"from_attributes": True}


class UserCreate(BaseModel):
    email: EmailStr
    password: str 


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str 
    token_type: str 


class TokenData(BaseModel):
    id: Optional[int] = None


class Vote(BaseModel):
    post_id: int 
    dir: int = Field(..., le=1)  # ✅ Updated conint syntax safely for Pydantic V2
