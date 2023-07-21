from attrs import define
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship, Session

from .database import Base


class Flower(Base):
    __tablename__ = "flowers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    count = Column(Integer, index=True)
    cost = Column(Integer, index=True)


@define
class FlowerCreate:
    name: str
    count: int
    cost: int


class FlowersRepository:
    def get_flower(self, db: Session, flower_id: int) -> Flower | None:
        return db.query(Flower).filter(Flower.id == flower_id).first()

    def get_flower_by_name(self, db: Session, name: str) -> Flower | None:
        return db.query(Flower).filter(Flower.name == name).first()

    def get_flowers(self, db: Session, skip: int = 0, limit: int = 100) -> list[Flower]:
        return db.query(Flower).offset(skip).limit(limit).all()

    def create_flower(self, db: Session, flower: FlowerCreate) -> Flower:
        db_flower = Flower(name=flower.name, count=flower.count, cost=flower.cost)
        db.add(db_flower)
        db.commit()
        db.refresh(db_flower)
        return db_flower

    def update_flower(self, db: Session, flower_id: int, new_data: Flower) -> Flower:
        db_flower = db.query(Flower).filter(Flower.id == flower_id).update(new_data)
        db.commit()
        
    def delete_flower_by_id(self, db: Session, flower_id: int):
        db_flower = db.query(Flower).filter(Flower.id == flower_id).delete()
        db.commit()
