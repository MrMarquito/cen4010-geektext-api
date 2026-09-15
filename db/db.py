from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
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

Base.metadata.create_all(engine)
