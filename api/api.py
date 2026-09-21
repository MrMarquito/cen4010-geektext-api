from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session
from pydantic import BaseModel
from db.db import SessionLocal, User, CreditCard, Author, Book, CartItem

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
        from_attributes = True

class CreditCardCreate(BaseModel):
    number: str
    exp: str
    cvv: str

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

class CartItemAdd(BaseModel):
    isbn: str
    quantity: int = 1

class CartBookResponse(BaseModel):
    isbn: str
    name: str
    price: int
    quantity: int

    class Config:
        from_attributes = True

class CartSubtotalResponse(BaseModel):
    username: str
    subtotal: int

# API Endpoints/Routes and functions
@app.get("/")
def root():
    return {"text": "Welcome to GeekText API"}

@app.post("/users/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    if user.email and db.query(User).filter(user.username == User.username).first():
        raise HTTPException(status_code=409, detail="Email already in use!")

    new_user = User(**user.model_dump())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.get("/users/{username}", response_model=UserResponse, status_code=status.HTTP_200_OK)
def get_user(username: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == username).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found!")

    return user

@app.put("/users/{username}", status_code=status.HTTP_204_NO_CONTENT)
def update_user(username: str, user: UserUpdate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == username).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found!")

    update_data = user.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_user, key, value)
    db.commit()
    return

@app.post("/users/{username}/credit-card/", response_model=None, status_code=status.HTTP_201_CREATED)
def create_credit_card(username: str, credit_card: CreditCardCreate, db: Session = Depends(get_db)):
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

@app.post("/cart/{username}/books", status_code=status.HTTP_204_NO_CONTENT)
def add_to_cart(username: str, item: CartItemAdd, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == username).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found!")

    db_book = db.query(Book).filter(Book.isbn == item.isbn).first()
    if not db_book:
        raise HTTPException(status_code=404, detail="Book not found!")

    existing = (
        db.query(CartItem)
        .filter(CartItem.username == username, CartItem.isbn == item.isbn)
        .first()
    )
    if existing:
        existing.quantity += item.quantity
    else:
        db.add(CartItem(username=username, isbn=item.isbn, quantity=item.quantity))

    db.commit()
    return


@app.get("/cart/{username}/books", response_model=list[CartBookResponse], status_code=status.HTTP_200_OK)
def get_cart(username: str, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == username).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found!")

    rows = (
        db.query(CartItem, Book)
        .join(Book, CartItem.isbn == Book.isbn)
        .filter(CartItem.username == username)
        .all()
    )

    return [
        CartBookResponse(isbn=book.isbn, name=book.name, price=book.price, quantity=cart_item.quantity)
        for cart_item, book in rows
    ]


@app.get("/cart/{username}/subtotal", response_model=CartSubtotalResponse, status_code=status.HTTP_200_OK)
def get_cart_subtotal(username: str, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == username).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found!")

    total = (
        db.query(func.coalesce(func.sum(Book.price * CartItem.quantity), 0))
        .join(CartItem, CartItem.isbn == Book.isbn)
        .filter(CartItem.username == username)
        .scalar()
    )
    return CartSubtotalResponse(username=username, subtotal=total)


@app.delete("/cart/{username}/books/{isbn}", status_code=status.HTTP_204_NO_CONTENT)
def remove_from_cart(username: str, isbn: str, db: Session = Depends(get_db)):
    deleted = (
        db.query(CartItem)
        .filter(CartItem.username == username, CartItem.isbn == isbn)
        .delete()
    )
    db.commit()
    if not deleted:
        raise HTTPException(status_code=404, detail="Book not found in user's cart!")
    return
