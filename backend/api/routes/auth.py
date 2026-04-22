from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, EmailStr
import bcrypt
import uuid
from db.mongodb import get_db

router = APIRouter()

class UserSignup(BaseModel):
    name: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

@router.post("/signup")
async def signup(user: UserSignup):
    db = await get_db()
    existing_user = await db.users.find_one({"email": user.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_pwd = bcrypt.hashpw(user.password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    new_user = {
        "user_id": str(uuid.uuid4()),
        "name": user.name,
        "email": user.email,
        "password": hashed_pwd
    }
    
    await db.users.insert_one(new_user)
    return {"message": "Account created successfully"}

@router.post("/login")
async def login(user: UserLogin):
    db = await get_db()
    db_user = await db.users.find_one({"email": user.email})
    
    if not db_user:
        raise HTTPException(status_code=400, detail="Invalid email or password")
        
    if not bcrypt.checkpw(user.password.encode('utf-8'), db_user["password"].encode('utf-8')):
        raise HTTPException(status_code=400, detail="Invalid email or password")
    
    # Return user data without password
    return {
        "message": "Login successful",
        "user": {
            "id": db_user["user_id"],
            "name": db_user["name"],
            "email": db_user["email"]
        }
    }
