from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

engine = create_engine("sqlite:///users.db", connect_args={"check_same_thread":False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

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