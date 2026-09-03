from datetime import datetime, timezone
from typing import Optional, List
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import func
from sqlalchemy.orm import Session

from db.db import (
    SessionLocal,
    User,
    CreditCard,
    Author,
    Book,
    Rating,
    Comment,
    CartItem,
    Wishlist,
    WishlistItem
)

app = FastAPI(title="GeekText API")

# CORS Middleware configured for local development and client apps
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- Schemas ---

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
    bio: Optional[str] = None
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
    copies_sold: Optional[int] = 0

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

class RatingCreate(BaseModel):
    user_id: int
    book_isbn: str
    rating: int = Field(..., ge=1, le=5, description="Rating scale between 1 and 5")

class RatingResponse(BaseModel):
    id: int
    user_id: int
    book_isbn: str
    rating: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class CommentCreate(BaseModel):
    user_id: int
    book_isbn: str
    comment: str

class CommentResponse(BaseModel):
    id: int
    user_id: int
    book_isbn: str
    comment: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class AverageRatingResponse(BaseModel):
    book_isbn: str
    average_rating: float

class PublisherDiscount(BaseModel):
    publisher: str
    discount_percent: float = Field(..., ge=0, le=100, description="Discount percentage between 0 and 100")

class CartItemCreate(BaseModel):
    user_id: int
    book_isbn: str

class SubtotalResponse(BaseModel):
    user_id: int
    subtotal: float

class WishlistCreate(BaseModel):
    user_id: int
    name: str

class WishlistItemCreate(BaseModel):
    wishlist_id: int
    book_isbn: str

class WishlistResponse(BaseModel):
    id: int
    user_id: int
    name: str

    model_config = ConfigDict(from_attributes=True)

# --- Endpoints ---

@app.get("/")
def root():
    return {"text": "Welcome to GeekTextAPI"}

# === Feature 1: Book Browsing and Sorting ===

# Top Sellers (Top 10 books by copies sold descending)
@app.get("/books/top-sellers", response_model=List[BookResponse])
def get_top_sellers(db: Session = Depends(get_db)):
    return db.query(Book).order_by(Book.copies_sold.desc()).limit(10).all()

# Retrieve books by genre
@app.get("/books/genre/{genre}", response_model=List[BookResponse])
def get_books_by_genre(genre: str, db: Session = Depends(get_db)):
    books = db.query(Book).filter(func.lower(Book.genre) == genre.lower()).all()
    return books

# Retrieve books with a rating equal to or higher than the threshold
@app.get("/books/rating/{min_rating}", response_model=List[BookResponse])
def get_books_by_rating(min_rating: float, db: Session = Depends(get_db)):
    # Group ratings by book ISBN and filter where average rating >= min_rating
    matching_isbns = (
        db.query(Rating.book_isbn)
        .group_by(Rating.book_isbn)
        .having(func.avg(Rating.rating) >= min_rating)
        .subquery()
    )
    return db.query(Book).filter(Book.isbn.in_(matching_isbns)).all()

# Discount books by publisher
@app.put("/books/discount", status_code=status.HTTP_200_OK)
def discount_by_publisher(discount_data: PublisherDiscount, db: Session = Depends(get_db)):
    books = db.query(Book).filter(func.lower(Book.publisher) == discount_data.publisher.lower()).all()
    if not books:
        raise HTTPException(
            status_code=404,
            detail=f"No books found for publisher '{discount_data.publisher}'"
        )

    multiplier = 1.0 - (discount_data.discount_percent / 100.0)
    for book in books:
        book.price = round(book.price * multiplier, 2)

    db.commit()
    return {"message": f"Updated {len(books)} books with a {discount_data.discount_percent}% discount"}

# === Feature 2: Profile Management ===

@app.post("/users/", status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter(User.username == user.username).first():
        raise HTTPException(status_code=400, detail="Username already registered")

    new_user = User(
        username=user.username,
        password=user.password,
        name=user.name,
        email=user.email,
        address=user.address
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "User created successfully"}

@app.get("/users/{username}", response_model=UserResponse)
def get_user(username: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.put("/users/{username}", status_code=status.HTTP_200_OK)
def update_user(username: str, user_data: UserUpdate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    update_dict = user_data.model_dump(exclude_unset=True)
    for field, value in update_dict.items():
        setattr(user, field, value)

    db.commit()
    db.refresh(user)
    return {"message": "User updated successfully"}

@app.post("/users/{username}/credit-cards", status_code=status.HTTP_201_CREATED)
def link_credit_card(username: str, card_data: CreditCardCreate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    new_card = CreditCard(
        user_id=user.id,
        card_number=card_data.card_number,
        expiration=card_data.expiration,
        cvv=card_data.cvv
    )
    db.add(new_card)
    db.commit()
    db.refresh(new_card)
    return {"message": "Credit card added successfully"}


# === Feature 3: Shopping Cart ===

# Add a book to the shopping cart
@app.post("/cart/", status_code=status.HTTP_201_CREATED)
def add_to_cart(item: CartItemCreate, db: Session = Depends(get_db)):
    if not db.query(User).filter(User.id == item.user_id).first():
        raise HTTPException(status_code=404, detail="User not found")
    if not db.query(Book).filter(Book.isbn == item.book_isbn).first():
        raise HTTPException(status_code=404, detail="Book not found")

    new_cart_item = CartItem(
        user_id=item.user_id,
        book_isbn=item.book_isbn
    )
    db.add(new_cart_item)
    db.commit()
    db.refresh(new_cart_item)
    return {"message": "Book added to cart successfully"}

# Retrieve list of books in the shopping cart
@app.get("/cart/{user_id}", response_model=List[BookResponse])
def get_cart_books(user_id: int, db: Session = Depends(get_db)):
    if not db.query(User).filter(User.id == user_id).first():
        raise HTTPException(status_code=404, detail="User not found")

    cart_entries = db.query(CartItem).filter(CartItem.user_id == user_id).all()
    # Extract the Book model instances linked via relationship
    return [entry.book for entry in cart_entries]

# Retrieve the subtotal of the books in the cart
@app.get("/cart/{user_id}/subtotal", response_model=SubtotalResponse)
def get_cart_subtotal(user_id: int, db: Session = Depends(get_db)):
    if not db.query(User).filter(User.id == user_id).first():
        raise HTTPException(status_code=404, detail="User not found")

    cart_entries = db.query(CartItem).filter(CartItem.user_id == user_id).all()
    total = sum(entry.book.price for entry in cart_entries)

    return SubtotalResponse(user_id=user_id, subtotal=round(total, 2))

# Delete a book instance from the user's shopping cart
@app.delete("/cart/{user_id}/books/{book_isbn}", status_code=status.HTTP_200_OK)
def remove_from_cart(user_id: int, book_isbn: str, db: Session = Depends(get_db)):
    cart_entry = (
        db.query(CartItem)
        .filter(CartItem.user_id == user_id, CartItem.book_isbn == book_isbn)
        .first()
    )
    if not cart_entry:
        raise HTTPException(status_code=404, detail="Book not found in user's cart")

    db.delete(cart_entry)
    db.commit()
    return {"message": "Book removed from cart successfully"}

# === Feature 4: Book Details ===

@app.post("/authors/", status_code=status.HTTP_201_CREATED)
def create_author(author: AuthorCreate, db: Session = Depends(get_db)):
    new_author = Author(
        first_name=author.first_name,
        last_name=author.last_name,
        bio=author.bio,
        publisher=author.publisher
    )
    db.add(new_author)
    db.commit()
    db.refresh(new_author)
    return {"message": "Author successfully registered"}

@app.post("/books/", status_code=status.HTTP_201_CREATED)
def create_book(book: BookCreate, db: Session = Depends(get_db)):
    if db.query(Book).filter(Book.isbn == book.isbn).first():
        raise HTTPException(status_code=400, detail="Book already registered")

    if not db.query(Author).filter(Author.id == book.author_id).first():
        raise HTTPException(status_code=404, detail="Author ID does not exist")

    new_book = Book(
        isbn=book.isbn,
        author_id=book.author_id,
        name=book.name,
        description=book.description,
        price=book.price,
        genre=book.genre,
        publisher=book.publisher,
        year_published=book.year_published,
        copies_sold=book.copies_sold or 0
    )
    db.add(new_book)
    db.commit()
    db.refresh(new_book)
    return {"message": "Book successfully registered"}

@app.get("/books/{isbn}", response_model=BookResponse)
def get_book_by_isbn(isbn: str, db: Session = Depends(get_db)):
    book = db.query(Book).filter(Book.isbn == isbn).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book

@app.get("/books/author/{author_id}", response_model=List[BookResponse])
def get_books_by_author(author_id: int, db: Session = Depends(get_db)):
    return db.query(Book).filter(Book.author_id == author_id).all()

# === Feature 5: Book Rating and Commenting ===

@app.post("/ratings/", status_code=status.HTTP_201_CREATED)
def add_rating(rating_data: RatingCreate, db: Session = Depends(get_db)):
    if not db.query(User).filter(User.id == rating_data.user_id).first():
        raise HTTPException(status_code=404, detail="User not found")
    if not db.query(Book).filter(Book.isbn == rating_data.book_isbn).first():
        raise HTTPException(status_code=404, detail="Book not found")

    new_rating = Rating(
        user_id=rating_data.user_id,
        book_isbn=rating_data.book_isbn,
        rating=rating_data.rating,
        created_at=datetime.now(timezone.utc)
    )
    db.add(new_rating)
    db.commit()
    db.refresh(new_rating)
    return {"message": "Rating recorded successfully"}

@app.post("/comments/", status_code=status.HTTP_201_CREATED)
def add_comment(comment_data: CommentCreate, db: Session = Depends(get_db)):
    if not db.query(User).filter(User.id == comment_data.user_id).first():
        raise HTTPException(status_code=404, detail="User not found")
    if not db.query(Book).filter(Book.isbn == comment_data.book_isbn).first():
        raise HTTPException(status_code=404, detail="Book not found")

    new_comment = Comment(
        user_id=comment_data.user_id,
        book_isbn=comment_data.book_isbn,
        comment=comment_data.comment,
        created_at=datetime.utcnow()
    )
    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)
    return {"message": "Comment posted successfully"}

@app.get("/books/{isbn}/comments", response_model=List[CommentResponse])
def get_comments_for_book(isbn: str, db: Session = Depends(get_db)):
    if not db.query(Book).filter(Book.isbn == isbn).first():
        raise HTTPException(status_code=404, detail="Book not found")
    return db.query(Comment).filter(Comment.book_isbn == isbn).all()

@app.get("/books/{isbn}/rating/average", response_model=AverageRatingResponse)
def get_average_rating(isbn: str, db: Session = Depends(get_db)):
    if not db.query(Book).filter(Book.isbn == isbn).first():
        raise HTTPException(status_code=404, detail="Book not found")

    avg_rating = db.query(func.avg(Rating.rating)).filter(Rating.book_isbn == isbn).scalar()
    computed_avg = round(float(avg_rating), 2) if avg_rating is not None else 0.0

    return AverageRatingResponse(book_isbn=isbn, average_rating=computed_avg)


# === Feature 6: Wish List Management ===

# Create a wishlist (Max 3 wishlists per user, unique name)
@app.post("/wishlists/", status_code=status.HTTP_201_CREATED)
def create_wishlist(wishlist_data: WishlistCreate, db: Session = Depends(get_db)):
    if not db.query(User).filter(User.id == wishlist_data.user_id).first():
        raise HTTPException(status_code=404, detail="User not found")

    # Enforce rule: Users can create and have up to 3 different wish lists
    existing_count = db.query(Wishlist).filter(Wishlist.user_id == wishlist_data.user_id).count()
    if existing_count >= 3:
        raise HTTPException(
            status_code=400,
            detail="Wishlist limit reached. Users may only maintain up to 3 wishlists."
        )

    # Enforce unique name per user
    duplicate_name = (
        db.query(Wishlist)
        .filter(Wishlist.user_id == wishlist_data.user_id, Wishlist.name == wishlist_data.name)
        .first()
    )
    if duplicate_name:
        raise HTTPException(status_code=400, detail="A wishlist with this name already exists for this user")

    new_wishlist = Wishlist(
        user_id=wishlist_data.user_id,
        name=wishlist_data.name
    )
    db.add(new_wishlist)
    db.commit()
    db.refresh(new_wishlist)
    return {"message": "Wishlist created successfully"}

# Add a book to a user's wishlist
@app.post("/wishlists/items", status_code=status.HTTP_201_CREATED)
def add_to_wishlist(item_data: WishlistItemCreate, db: Session = Depends(get_db)):
    if not db.query(Wishlist).filter(Wishlist.id == item_data.wishlist_id).first():
        raise HTTPException(status_code=404, detail="Wishlist not found")
    if not db.query(Book).filter(Book.isbn == item_data.book_isbn).first():
        raise HTTPException(status_code=404, detail="Book not found")

    new_item = WishlistItem(
        wishlist_id=item_data.wishlist_id,
        book_isbn=item_data.book_isbn
    )
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    return {"message": "Book added to wishlist successfully"}

# List books in a user's wishlist
@app.get("/wishlists/{wishlist_id}/books", response_model=List[BookResponse])
def get_wishlist_books(wishlist_id: int, db: Session = Depends(get_db)):
    wishlist = db.query(Wishlist).filter(Wishlist.id == wishlist_id).first()
    if not wishlist:
        raise HTTPException(status_code=404, detail="Wishlist not found")

    # Extract related Book objects from the wishlist items
    return [item.book for item in wishlist.items]

# Remove a book from wishlist into the user's shopping cart
@app.delete("/wishlists/{wishlist_id}/books/{book_isbn}", status_code=status.HTTP_200_OK)
def transfer_wishlist_to_cart(wishlist_id: int, book_isbn: str, db: Session = Depends(get_db)):
    wishlist = db.query(Wishlist).filter(Wishlist.id == wishlist_id).first()
    if not wishlist:
        raise HTTPException(status_code=404, detail="Wishlist not found")

    wishlist_item = (
        db.query(WishlistItem)
        .filter(WishlistItem.wishlist_id == wishlist_id, WishlistItem.book_isbn == book_isbn)
        .first()
    )
    if not wishlist_item:
        raise HTTPException(status_code=404, detail="Book not found in this wishlist")

    # 1. Remove the book from the wishlist
    db.delete(wishlist_item)

    # 2. Add the book directly into the user's cart
    cart_item = CartItem(
        user_id=wishlist.user_id,
        book_isbn=book_isbn
    )
    db.add(cart_item)

    # Commit both changes in a single atomic transaction
    db.commit()
    return {"message": "Book removed from wishlist and added to shopping cart"}

@app.get("/users/{user_id}/wishlists", response_model=List[WishlistResponse])
def get_user_wishlists(user_id: int, db: Session = Depends(get_db)):
    return db.query(Wishlist).filter(Wishlist.user_id == user_id).all()
