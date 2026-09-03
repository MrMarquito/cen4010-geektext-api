from datetime import datetime
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
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATABASE_PATH = BASE_DIR / "geektext.db"
engine = create_engine(f'sqlite:///{DATABASE_PATH}', echo=False)

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base = declarative_base()

# Models
class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False)
    password = Column(String(100), nullable=False)
    name = Column(String(100))
    email = Column(String(100))
    address = Column(String(200))

    credit_cards = relationship("CreditCard", backref="user")
    cart_items = relationship("CartItem", backref="user")
    wishlists = relationship("Wishlist", backref="user")

class CreditCard(Base):
    __tablename__ = 'credit_cards'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    card_number = Column(String(19), nullable=False)
    expiration = Column(String(7), nullable=False)
    cvv = Column(String(4), nullable=False)

class Author(Base):
    __tablename__ = 'authors'
    id = Column(Integer, primary_key=True, autoincrement=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    bio = Column(String)
    publisher = Column(String(100))

    books = relationship("Book", backref="author")

class Book(Base):
    __tablename__ = 'books'
    isbn = Column(String(20), primary_key=True)
    author_id = Column(Integer, ForeignKey('authors.id'), nullable=False)
    name = Column(String(150), nullable=False)
    description = Column(String)
    price = Column(Float, nullable=False)
    genre = Column(String(50), nullable=False)
    publisher = Column(String(100), nullable=False)
    year_published = Column(Integer)
    copies_sold = Column(Integer, default=0)

    authors = relationship("Author", backref="book")

class CartItem(Base):
    __tablename__ = 'cart_items'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    book_isbn = Column(String(20), ForeignKey('books.isbn'), nullable=False)

    book = relationship("Book")

class RatingComment(Base):
    __tablename__ = 'ratings_comments'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    book_isbn = Column(String(20), ForeignKey('books.isbn'), nullable=False)
    rating = Column(Integer, nullable=True)
    comment = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User")
    book = relationship("Book")

class Wishlist(Base):
    __tablename__ = 'wishlists'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    name = Column(String(100), nullable=False)

    items = relationship("WishlistItem", backref="wishlist")

class WishlistItem(Base):
    __tablename__ = 'wishlist_items'
    id = Column(Integer, primary_key=True, autoincrement=True)
    wishlist_id = Column(Integer, ForeignKey('wishlists.id'), nullable=False)
    book_isbn = Column(String(20), ForeignKey('books.isbn'), nullable=False)

    book = relationship("Book")

Base.metadata.create_all(engine)
