from datetime import datetime, timezone
from pathlib import Path
from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    DateTime,
    ForeignKey,
    create_engine
)
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

# Anchors database path directly to the db directory
BASE_DIR = Path(__file__).resolve().parent
DATABASE_PATH = BASE_DIR / "geektext.db"
engine = create_engine(f"sqlite:///{DATABASE_PATH}", echo=False)

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False)
    password = Column(String(100), nullable=False)
    name = Column(String(100))
    email = Column(String(100))
    address = Column(String(200))

    credit_cards = relationship("CreditCard", backref="user")
    cart_items = relationship("CartItem", backref="user")
    wishlists = relationship("Wishlist", backref="user")
    ratings = relationship("Rating", backref="user")
    comments = relationship("Comment", backref="user")

class CreditCard(Base):
    __tablename__ = "credit_cards"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    card_number = Column(String(19), nullable=False)
    expiration = Column(String(7), nullable=False)
    cvv = Column(String(4), nullable=False)

class Author(Base):
    __tablename__ = "authors"
    id = Column(Integer, primary_key=True, autoincrement=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    bio = Column(String)
    publisher = Column(String(100))

    books = relationship("Book", backref="author")

class Book(Base):
    __tablename__ = "books"
    isbn = Column(String(20), primary_key=True)
    author_id = Column(Integer, ForeignKey("authors.id"), nullable=False)
    name = Column(String(150), nullable=False)
    description = Column(String)
    price = Column(Float, nullable=False)
    genre = Column(String(50), nullable=False)
    publisher = Column(String(100), nullable=False)
    year_published = Column(Integer)
    copies_sold = Column(Integer, default=0)

    ratings = relationship("Rating", backref="book")
    comments = relationship("Comment", backref="book")

class Rating(Base):
    __tablename__ = "ratings"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    book_isbn = Column(String(20), ForeignKey("books.isbn"), nullable=False)
    rating = Column(Integer, nullable=False)  # 1 to 5 scale
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

class Comment(Base):
    __tablename__ = "comments"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    book_isbn = Column(String(20), ForeignKey("books.isbn"), nullable=False)
    comment = Column(String, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

class CartItem(Base):
    __tablename__ = "cart_items"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    book_isbn = Column(String(20), ForeignKey("books.isbn"), nullable=False)

    book = relationship("Book")

class Wishlist(Base):
    __tablename__ = "wishlists"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(100), nullable=False)

    items = relationship("WishlistItem", backref="wishlist")

class WishlistItem(Base):
    __tablename__ = "wishlist_items"
    id = Column(Integer, primary_key=True, autoincrement=True)
    wishlist_id = Column(Integer, ForeignKey("wishlists.id"), nullable=False)
    book_isbn = Column(String(20), ForeignKey("books.isbn"), nullable=False)

    book = relationship("Book")

Base.metadata.create_all(engine)
