from typing import Optional
from fastapi import FastAPI, HTTPException, Depends, status
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session
from db.db import SessionLocal, User, CreditCard, Author, Book

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Schemas
class UserCreate(BaseModel):
    username: str
    password: str
    name: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None

class UserResponse(BaseModel):
    id: int
    username: str
    name: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class UserUpdate(BaseModel):
    name: Optional[str] = None
    password: Optional[str] = None
    address: Optional[str] = None

class CreditCardCreate(BaseModel):
    card_number: str
    expiration: str
    cvv: str

class AuthorCreate(BaseModel):
    first_name: str
    last_name: str
    bio: str
    publisher: str

class BookCreate(BaseModel):
    isbn: str
    author_id: int
    name: str
    description: Optional[str] = None
    price: float
    genre: str
    publisher: str
    year_published: int
    copies_sold: Optional[int] = None

class BookResponse(BaseModel):
    isbn: str
    author_id: int
    name: str
    description: Optional[str] = None
    price: float
    genre: str
    publisher: str
    year_published: int
    copies_sold: int

    model_config = ConfigDict(from_attributes=True)

### Endpoints ###
@app.get("/")
def root():
    return {"text": "Welcome to GeekTextAPI"}

# Get Users
@app.get("/users/{username}", response_model=UserResponse)
def get_user(username: str, db:Session = Depends(get_db)):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# Create Users
@app.post("/users/", status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.username == user.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already registered")

    new_user = User(
        username = user.username,
        password = user.password,
        name = user.name,
        email = user.email,
        address = user.address
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "User created successfully"}

# Update Users
@app.put("/users/{username}", status_code=status.HTTP_200_OK)
def update_user(username: str, user_data: UserUpdate, db:Session = Depends(get_db)):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    update_dict = user_data.model_dump(exclude_unset=True)
    for field, value in update_dict.items():
        setattr(user, field, value)

    db.commit()
    db.refresh(user)
    return {"message": "User updated successfully"}

# Link CreditCard to Users
@app.post("/users/{username}/credit-cards", status_code=status.HTTP_201_CREATED)
def link_credit(username: str, card_data: CreditCardCreate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    new_card = CreditCard(
        user_id = user.id,
        card_number = card_data.card_number,
        expiration = card_data.expiration,
        cvv = card_data.cvv
    )

    db.add(new_card)
    db.commit()
    db.refresh(new_card)
    return {"message": "Credit card added successfully"}

# Create Authors
@app.post("/authors/", status_code=status.HTTP_201_CREATED)
def create_author(author: AuthorCreate, db: Session = Depends(get_db)):
    existing_author = db.query(Author).filter(Author.first_name == author.first_name, Author.last_name == author.last_name).first()
    if existing_author:
        raise HTTPException(status_code=400, detail="Author already registered")

    new_author = Author(
        first_name = author.first_name,
        last_name = author.last_name,
        bio = author.bio,
        publisher = author.publisher
    )

    db.add(new_author)
    db.commit()
    db.refresh(new_author)
    return {"message": "Author successfully registered"}

# Create Books
@app.post("/books/", status_code=status.HTTP_201_CREATED)
def create_book(book: BookCreate, db: Session = Depends(get_db)):
    existing_book = db.query(Book).filter(Book.isbn == book.isbn).first()
    if existing_book:
        raise HTTPException(status_code=400, detail="Book already registered")

    new_book = Book(
        isbn = book.isbn,
        author_id = book.author_id,
        name = book.name,
        description = book.description,
        price = book.price,
        genre = book.genre,
        publisher = book.publisher,
        year_published = book.year_published,
        copies_sold = book.copies_sold or 0
    )

    db.add(new_book)
    db.commit()
    db.refresh(new_book)
    return {"message":"Book successfully registered"}

# Retrieve Book by ISBN
@app.get("/books/{isbn}", response_model=BookResponse)
def get_book_isbn(isbn: str, db: Session = Depends(get_db)):
    book = db.query(Book).filter(Book.isbn == isbn).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book

# Retrive Book by AuthorCreate
@app.get("/books/author/{author_id}", response_model=list[BookResponse])
def get_book_author_id(author_id: int, db:Session = Depends(get_db)):
    books = db.query(Book).filter(Book.author_id == author_id).all()
    return books
