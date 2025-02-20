from pydantic import BaseModel


class UserSchema(BaseModel):
    user_id: int
    username: str
    email: str
    is_admin: bool
    
    class Config:
        from_attributes = True

class UserCreateSchema(BaseModel):
    username: str
    email: str
    password: str

class AdminSchema(UserSchema):
    is_admin: bool = True