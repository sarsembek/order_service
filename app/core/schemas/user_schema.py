from pydantic import BaseModel, EmailStr

class UserSchema(BaseModel):
    user_id: int
    username: str
    email: EmailStr
    is_admin: bool
    
    model_config = {
        "from_attributes": True
    }

class UserCreateSchema(BaseModel):
    username: str
    email: EmailStr
    password: str

class AdminSchema(UserSchema):
    is_admin: bool = True
    
class LoginSchema(BaseModel):
    username: str
    password: str
    
class Token(BaseModel):
    access_token: str
    token_type: str
    
class RefreshSchema(BaseModel):
    token: str
