from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from db.db import SessionLocal, Author, Book

# API Init and Conn with DB
app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Pydantic Models
class AuthorCreate(BaseModel):
    first_name: str
    last_name: str
    biography: str | None = None
    publisher: str | None = None

class AuthorResponse(BaseModel):
    id: int
    first_name: str
    last_name: str
    biography: str | None = None
    publisher: str | None = None

    class Config:
        from_attributes = True

class BookCreate(BaseModel):
    isbn: str
    name: str
    description: str | None = None
    price: int
    author_id: int
    genre: str | None = None
    publisher: str | None = None
    year_published: int | None = None
    copies_sold: int = 0

class BookResponse(BaseModel):
    isbn: str
    name: str
    description: str | None = None
    price: int
    author_id: int
    genre: str | None = None
    publisher: str | None = None
    year_published: int | None = None
    copies_sold: int

    class Config:
        from_attributes = True


# API Endpoints/Routes and functions
@app.post("/books/", response_model=BookResponse, status_code=status.HTTP_201_CREATED)
def create_book(book: BookCreate, db: Session = Depends(get_db)):
    if db.query(Book).filter(Book.isbn == book.isbn).first():
        raise HTTPException(status_code=409, detail="Book with this ISBN already exists!")

    new_book = Book(**book.model_dump())
    db.add(new_book)
    db.commit()
    db.refresh(new_book)
    return new_book

@app.get("/books/{isbn}", response_model=BookResponse, status_code=status.HTTP_200_OK)
def get_book(isbn: str, db: Session = Depends(get_db)):
    book = db.query(Book).filter(Book.isbn == isbn).first()

    if not book:
        raise HTTPException(status_code=404, detail="Book not found!")

    return book

@app.post("/authors/", response_model=AuthorResponse, status_code=status.HTTP_201_CREATED)
def create_author(author: AuthorCreate, db: Session = Depends(get_db)):
    new_author = Author(**author.model_dump())
    db.add(new_author)
    db.commit()
    db.refresh(new_author)
    return new_author

@app.get("/authors/{author_id}/books", response_model=list[BookResponse], status_code=status.HTTP_200_OK)
def get_books_by_author(author_id: int, db: Session = Depends(get_db)):
    author = db.query(Author).filter(Author.id == author_id).first()
    if not author:
        raise HTTPException(status_code=404, detail="Author not found!")

    return db.query(Book).filter(Book.author_id == author_id).all()

