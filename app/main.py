from fastapi import Cookie, FastAPI, Form, Request, Response, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
from fastapi.security import OAuth2PasswordBearer

from .flowers_repository import Flower, FlowersRepository
from .purchases_repository import Purchase, PurchasesRepository
from .users_repository import User, UsersRepository, UserCreate
from .database import Base, engine, SessionLocal


Base.metadata.create_all(bind=engine)

app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

flowers_repository = FlowersRepository()
purchases_repository = PurchasesRepository()
users_repository = UsersRepository()


class UserCreateRequest(BaseModel):
    email: str
    full_name: str
    password: str


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


class UserProfileResponse(BaseModel):
    id: int
    email: str
    full_name: str


@app.get("/profile", response_model=UserProfileResponse)
def get_profile(user_id: int, db: Session = Depends(get_db)):
    user = users_repository.get_user(db, user_id)
    return user
