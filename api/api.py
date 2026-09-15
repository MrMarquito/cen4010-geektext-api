from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from db.db import SessionLocal, User, CreditCard

# API Init and Conn with DB
app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Pydantic Models
class UserCreate(BaseModel):
    username: str
    password: str
    name: str | None = None
    email: str | None = None
    address: str | None = None

class UserUpdate(BaseModel):
    password: str | None = None
    name: str | None = None
    address: str | None = None

class UserResponse(BaseModel):
    username: str
    name: str | None = None
    email: str | None = None
    address: str | None = None

    class Config:
        from_attributes=True

class CreditCardCreate(BaseModel):
    number: str
    exp: str
    cvv: str

# API Endpoints/Routes and functions
@app.get("/")
def root():
    return {"text:Welcome to GeekText API"}


@app.post("/users/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate, db:Session = Depends(get_db)):
    if db.query(User).filter(user.username == User.username).first():
        raise HTTPException(status_code=409, detail="User already exists!")

    new_user = User(**user.model_dump())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.get("/users/{username}", response_model=UserResponse, status_code=status.HTTP_200_OK)
def get_user(username: str, db:Session = Depends(get_db)):
    user = db.query(User).filter(User.username == username).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found!")

    return user

@app.put("/users/{username}/update", status_code=status.HTTP_204_NO_CONTENT)
def update_user(username: str, user: UserUpdate, db:Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == username).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found!")

    update_data = user.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_user, key, value)
    db.commit()
    return

@app.post("/users/{username}/credit-card/", response_model=None, status_code=status.HTTP_201_CREATED)
def create_credit_card(username: str, credit_card: CreditCardCreate, db:Session=Depends(get_db)):
    db_user = db.query(User).filter(User.username == username).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found!")

    new_credit_card = CreditCard(
        username=username,
        number=credit_card.number,
        exp=credit_card.exp,
        cvv=credit_card.cvv
    )
    db.add(new_credit_card)
    db.commit()
    return
