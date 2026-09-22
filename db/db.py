from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

engine = create_engine("sqlite:///users.db", connect_args={"check_same_thread":False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    username = Column(String(100), primary_key=True, index=True)
    password = Column(String(100), nullable=False)
    name = Column(String(100), nullable=True)
    email = Column(String(100), nullable=True, unique=True)
    address = Column(String(100), nullable=True)

class CreditCard(Base):
    __tablename__ = "credit-cards"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(100), ForeignKey("users.username"), index=True)
    number = Column(String(16), nullable=False)
    exp = Column(String(7), nullable=False)
    cvv = Column(String(4), nullable=False)

class Author(Base):
    __tablename__ = "authors"

    id = Column(Integer, primary_key=True, autoincrement=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    biography = Column(String(1000), nullable=True)
    publisher = Column(String(100), nullable=True)

class Book(Base):
    __tablename__ = "books"

    isbn = Column(String(13), primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    description = Column(String(1000), nullable=True)
    price = Column(Integer, nullable=False)
    author_id = Column(Integer, ForeignKey("authors.id"), index=True)
    genre = Column(String(100), nullable=True)
    publisher = Column(String(100), nullable=True)
    year_published = Column(Integer, nullable=True)
    copies_sold = Column(Integer, default=0)

class CartItem(Base):
    __tablename__ = "cart_items"
    __table_args__ = (
        UniqueConstraint("username", "isbn", name="uq_username_isbn_cart"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(100), ForeignKey("users.username"), index=True)
    isbn = Column(String(13), ForeignKey("books.isbn"), index=True)
    quantity = Column(Integer, nullable=False, default=1)


Base.metadata.create_all(engine)
