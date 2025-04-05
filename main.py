# main.py
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from sqlalchemy import create_engine, Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from passlib.context import CryptContext
import secrets

app = FastAPI()
security = HTTPBasic()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# БД
DATABASE_URL = "sqlite:///./shopping_list.db"
Base = declarative_base()
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)

# Модели
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)

class Item(Base):
    __tablename__ = "items"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    is_bought = Column(Boolean, default=False)
    is_deleted = Column(Boolean, default=False)
    user_id = Column(Integer, ForeignKey("users.id"))

Base.metadata.create_all(bind=engine)

# Утилиты
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(credentials: HTTPBasicCredentials = Depends(security), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == credentials.username).first()
    if user and pwd_context.verify(credentials.password, user.hashed_password):
        return user
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

# Роуты
@app.post("/register")
def register_user(credentials: HTTPBasicCredentials = Depends(security), db: Session = Depends(get_db)):
    if db.query(User).filter(User.username == credentials.username).first():
        raise HTTPException(status_code=400, detail="User already exists")
    user = User(username=credentials.username, hashed_password=pwd_context.hash(credentials.password))
    db.add(user)
    db.commit()
    return {"message": "User registered"}

@app.post("/items")
def add_item(name: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    item = Item(name=name, user_id=user.id)
    db.add(item)
    db.commit()
    return {"message": "Item added"}

@app.get("/items")
def list_items(include_deleted: bool = False, include_bought: bool = True, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    query = db.query(Item).filter(Item.user_id == user.id)
    if not include_deleted:
        query = query.filter(Item.is_deleted == False)
    if not include_bought:
        query = query.filter(Item.is_bought == False)
    return query.all()

@app.post("/items/{item_id}/buy")
def mark_as_bought(item_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    item = db.query(Item).filter(Item.id == item_id, Item.user_id == user.id).first()
    if not item or item.is_deleted:
        raise HTTPException(status_code=404, detail="Item not found")
    item.is_bought = True
    db.commit()
    return {"message": "Item marked as bought"}

@app.delete("/items/{item_id}")
def soft_delete(item_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    item = db.query(Item).filter(Item.id == item_id, Item.user_id == user.id).first()
    if not item or item.is_deleted:
        raise HTTPException(status_code=404, detail="Item not found")
    item.is_deleted = True
    db.commit()
    return {"message": "Item soft deleted"}
