from fastapi import FastAPI, Response, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel

from .flowers_repository import Flower, FlowersRepository, FlowerCreate
from .purchases_repository import Purchase, PurchasesRepository
from .users_repository import User, UsersRepository, UserCreate
from .database import Base, engine, SessionLocal


Base.metadata.create_all(bind=engine)

app = FastAPI()

flowers_repository = FlowersRepository()
purchases_repository = PurchasesRepository()
users_repository = UsersRepository()


class UserCreateRequest(BaseModel):
    email: str
    full_name: str
    password: str


class UserProfileResponse(BaseModel):
    id: int
    email: str
    full_name: str


class FlowerCreateRequest(BaseModel):
    name: str
    count: int
    cost: int


class FlowerResponse(BaseModel):
    id: int
    name: str
    count: int
    cost: int


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/signup")
def post_signup(input: UserCreateRequest, db: Session = Depends(get_db)):
    created_user = users_repository.create_user(db, UserCreate(email=input.email, full_name=input.full_name, password=input.password))
    return RedirectResponse("/login", status_code=303)


@app.post("/login")
def post_login(email: str, password: str, db: Session = Depends(get_db)):
    user = users_repository.get_user_by_email(db, email)
    if user is None:
        raise HTTPException(status_code=400, detail="Incorrect email")
    
    user_password = users_repository.get_user_by_password(db, password)
    if user_password is None:
        raise HTTPException(status_code=400, detail="Incorrect password")

    return RedirectResponse("/profile", status_code=303)


@app.get("/profile", response_model=UserProfileResponse)
def get_profile(user_id: int, db: Session = Depends(get_db)):
    db_user = users_repository.get_user(db, user_id)
    
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")

    return db_user


@app.get("/flowers")
def get_flowers(skip: int=0, limit: int=100, db: Session = Depends(get_db)):
    db_flowers = flowers_repository.get_flowers(db, skip=skip, limit=limit)
    if db_flowers is None:
        raise HTTPException(status_code=404, detail="Flowers not found")

    return db_flowers


@app.post("/flowers")
def post_flowers(input: FlowerCreateRequest, db: Session = Depends(get_db)):
    created_flower = flowers_repository.create_flower(db, flower=input)
    return RedirectResponse("/flowers", status_code=303)


@app.put("/flowers/{flower_id}")
def update_flower(
    flower_id: int,
    new_flower: FlowerCreateRequest,
    db: Session = Depends(get_db)
):
    db_flower = flowers_repository.get_flower(db, flower_id=flower_id)
    updated_flower = flowers_repository.update_flower(db, flower_id=flower_id, new_data=new_flower)
    if db_flower is None:
        raise HTTPException(status_code=404, detail="Flower not found")

    return RedirectResponse("/flowers", status_code=303)


@app.delete("/flowers/{flower_id}")
def delete_flower(flower_id: int, db: Session = Depends(get_db)):
    db_flower = flowers_repository.delete_flower_by_id(db, flower_id=flower_id)
    if db_flower is None:
        raise HTTPException(status_code=404, detail="Flowers not found")
    
    return RedirectResponse("/flowers", status_code=303)
