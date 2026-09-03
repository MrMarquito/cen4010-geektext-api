from datetime import datetime
from db.db import Base, engine, SessionLocal, User, Author, Book, Rating, Comment

def seed_database():
    db = SessionLocal()
    try:
        # Recreate tables cleanly
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)

        # 1. Real Authors
        authors = [
            Author(
                first_name="Robert",
                last_name="Martin",
                bio="Software engineer and author known for agile software development principles.",
                publisher="Prentice Hall"
            ),
            Author(
                first_name="Andrew",
                last_name="Hunt",
                bio="Author of books on agile programming, software craft, and systems design.",
                publisher="Addison-Wesley"
            ),
            Author(
                first_name="Frank",
                last_name="Herbert",
                bio="American science fiction author best known for the novel Dune and its sequels.",
                publisher="Chilton Books"
            ),
            Author(
                first_name="J.R.R.",
                last_name="Tolkien",
                bio="English writer, philologist, and author of high-fantasy works.",
                publisher="George Allen & Unwin"
            ),
            Author(
                first_name="William",
                last_name="Gibson",
                bio="American-Canadian speculative fiction writer and pioneer of the cyberpunk subgenre.",
                publisher="Ace Books"
            ),
        ]
        db.add_all(authors)
        db.commit()

        # 2. Real Books with Genuine ISBNs
        books = [
            Book(
                isbn="9780132350884",
                author_id=1,
                name="Clean Code: A Handbook of Agile Software Craftsmanship",
                description="Even bad code can function. But if code isn't clean, it can bring a development organization to its knees.",
                price=37.99,
                genre="Technology",
                publisher="Prentice Hall",
                year_published=2008,
                copies_sold=142000
            ),
            Book(
                isbn="9780134494166",
                author_id=1,
                name="Clean Architecture: A Craftsman's Guide to Software Structure",
                description="Practical software architecture solutions for the real world.",
                price=34.99,
                genre="Technology",
                publisher="Prentice Hall",
                year_published=2017,
                copies_sold=98000
            ),
            Book(
                isbn="9780201616224",
                author_id=2,
                name="The Pragmatic Programmer: From Journeyman to Master",
                description="Straightforward advice covering career development and software architecture.",
                price=42.50,
                genre="Technology",
                publisher="Addison-Wesley",
                year_published=1999,
                copies_sold=185000
            ),
            Book(
                isbn="9780441172719",
                author_id=3,
                name="Dune",
                description="Set on the desert planet Arrakis, Dune tells the story of the boy Paul Atreides.",
                price=18.99,
                genre="Sci-Fi",
                publisher="Chilton Books",
                year_published=1965,
                copies_sold=2000000
            ),
            Book(
                isbn="9780547928227",
                author_id=4,
                name="The Hobbit",
                description="A fantasy novel following the quest of home-loving hobbit Bilbo Baggins.",
                price=14.95,
                genre="Fantasy",
                publisher="George Allen & Unwin",
                year_published=1937,
                copies_sold=1500000
            ),
            Book(
                isbn="9780441569595",
                author_id=5,
                name="Neuromancer",
                description="Case was the sharpest data-thief in the matrix until ex-employers crippled his nervous system.",
                price=16.00,
                genre="Sci-Fi",
                publisher="Ace Books",
                year_published=1984,
                copies_sold=650000
            ),
        ]
        db.add_all(books)
        db.commit()

        # 3. Default Users for Flutter Testing
        users = [
            User(
                username="testuser",
                password="password123",
                name="John Doe",
                email="johndoe@example.com",
                address="123 University Way, Miami, FL"
            ),
            User(
                username="alice_dev",
                password="securepass456",
                name="Alice Smith",
                email="alice@tech.org",
                address="456 Innovation Blvd, Austin, TX"
            )
        ]
        db.add_all(users)
        db.commit()

        # 4. Ratings and Comments
        ratings = [
            Rating(user_id=1, book_isbn="9780132350884", rating=5, created_at=datetime.utcnow()),
            Rating(user_id=2, book_isbn="9780132350884", rating=4, created_at=datetime.utcnow()),
            Rating(user_id=1, book_isbn="9780201616224", rating=5, created_at=datetime.utcnow()),
            Rating(user_id=2, book_isbn="9780441172719", rating=5, created_at=datetime.utcnow()),
        ]
        comments = [
            Comment(
                user_id=1,
                book_isbn="9780132350884",
                comment="A must-read for every computer science major. Changed how I name functions.",
                created_at=datetime.utcnow()
            ),
            Comment(
                user_id=2,
                book_isbn="9780132350884",
                comment="Great practical examples, especially the formatting and error handling chapters.",
                created_at=datetime.utcnow()
            ),
            Comment(
                user_id=2,
                book_isbn="9780441172719",
                comment="Incredible world-building and philosophical depth. One of my favorites.",
                created_at=datetime.utcnow()
            ),
        ]
        db.add_all(ratings)
        db.add_all(comments)
        db.commit()

        print("Database successfully seeded with real-world data!")

    except Exception as e:
        db.rollback()
        print(f"Error seeding data: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
