from attrs import define
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import Session

from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    full_name = Column(String)
    password = Column(String)


@define
class UserCreate:
    email: str
    full_name: str
    password: str


class UsersRepository:
    def get_user(self, db: Session, user_id: int) -> User | None:
        return db.query(User).filter(User.id == user_id).first()

    def get_user_by_email(self, db: Session, email: str) -> User | None:
        return db.query(User).filter(User.email == email).first()

    def get_user_by_password(self, db: Session, password: str) -> User | None:
        return db.query(User).filter(User.password == password).first()

    def get_users(self, db: Session, skip: int = 0, limit: int = 100) -> list[User]:
        return db.query(User).offset(skip).limit(limit).all()

    def create_user(self, db: Session, user: UserCreate) -> User:
        db_user = User(email=user.email, full_name=user.full_name, password=user.password)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
