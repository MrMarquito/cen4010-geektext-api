import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from db.db import Base
from api.api import app, get_db

# Create an isolated in-memory database for testing
TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def client():
    # Build schema fresh for each test function
    Base.metadata.create_all(bind=engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c

    # Teardown database and clear overrides
    Base.metadata.drop_all(bind=engine)
    app.dependency_overrides.clear()


# ==========================================
# Feature 2: Profile Management Tests
# ==========================================
def test_feature_2_profile_management(client):
    # 1. Create User
    user_payload = {
        "username": "tester",
        "password": "secretpassword",
        "name": "Test User",
        "email": "test@example.com",
        "address": "123 Test St",
    }
    res = client.post("/users/", json=user_payload)
    assert res.status_code == 201

    # Duplicate username check
    res_dup = client.post("/users/", json=user_payload)
    assert res_dup.status_code == 400

    # 2. Retrieve User
    res = client.get("/users/tester")
    assert res.status_code == 200
    assert res.json()["email"] == "test@example.com"

    # 3. Update User (non-email fields)
    update_payload = {"name": "Updated Name", "address": "456 New Road"}
    res = client.put("/users/tester", json=update_payload)
    assert res.status_code == 200

    res = client.get("/users/tester")
    assert res.json()["name"] == "Updated Name"

    # 4. Link Credit Card
    card_payload = {
        "card_number": "1234567890123456",
        "expiration": "12/28",
        "cvv": "999",
    }
    res = client.post("/users/tester/credit-cards", json=card_payload)
    assert res.status_code == 201


# ==========================================
# Feature 4: Book Details Tests
# ==========================================
def test_feature_4_book_and_author_management(client):
    # 1. Create Author
    author_payload = {
        "first_name": "Frank",
        "last_name": "Herbert",
        "bio": "Sci-Fi Author",
        "publisher": "Chilton Books",
    }
    res = client.post("/authors/", json=author_payload)
    assert res.status_code == 201

    # 2. Create Book
    book_payload = {
        "isbn": "9780441172719",
        "author_id": 1,
        "name": "Dune",
        "description": "Epic science fiction",
        "price": 20.0,
        "genre": "Sci-Fi",
        "publisher": "Chilton Books",
        "year_published": 1965,
        "copies_sold": 500000,
    }
    res = client.post("/books/", json=book_payload)
    assert res.status_code == 201

    # 3. Retrieve Book by ISBN
    res = client.get("/books/9780441172719")
    assert res.status_code == 200
    assert res.json()["name"] == "Dune"

    # 4. Retrieve Books by Author ID
    res = client.get("/books/author/1")
    assert res.status_code == 200
    assert len(res.json()) == 1
    assert res.json()[0]["isbn"] == "9780441172719"


# ==========================================
# Feature 5: Rating & Commenting Tests
# ==========================================
def test_feature_5_ratings_and_comments(client):
    # Setup prerequisite User and Book
    client.post("/users/", json={"username": "reviewer", "password": "123"})
    client.post("/authors/", json={"first_name": "A", "last_name": "B", "publisher": "Pub"})
    client.post(
        "/books/",
        json={
            "isbn": "1111111111",
            "author_id": 1,
            "name": "Rated Book",
            "price": 10.0,
            "genre": "Tech",
            "publisher": "Pub",
            "year_published": 2020,
        },
    )

    # 1. Add Ratings
    client.post("/ratings/", json={"user_id": 1, "book_isbn": "1111111111", "rating": 5})
    client.post("/ratings/", json={"user_id": 1, "book_isbn": "1111111111", "rating": 3})

    # Validate Rating Bounds (1 to 5)
    res_invalid = client.post("/ratings/", json={"user_id": 1, "book_isbn": "1111111111", "rating": 6})
    assert res_invalid.status_code == 422

    # 2. Get Average Rating ((5 + 3) / 2 = 4.0)
    res = client.get("/books/1111111111/rating/average")
    assert res.status_code == 200
    assert res.json()["average_rating"] == 4.0

    # 3. Add and Retrieve Comments
    client.post("/comments/", json={"user_id": 1, "book_isbn": "1111111111", "comment": "Great read!"})
    res = client.get("/books/1111111111/comments")
    assert res.status_code == 200
    assert len(res.json()) == 1
    assert res.json()[0]["comment"] == "Great read!"


# ==========================================
# Feature 1: Browsing and Sorting Tests
# ==========================================
def test_feature_1_browsing_and_discount(client):
    # Setup books
    client.post("/authors/", json={"first_name": "Author", "last_name": "One", "publisher": "TestPub"})
    client.post(
        "/books/",
        json={
            "isbn": "ISBN-A",
            "author_id": 1,
            "name": "Book A",
            "price": 50.0,
            "genre": "Fantasy",
            "publisher": "TestPub",
            "year_published": 2021,
            "copies_sold": 100,
        },
    )
    client.post(
        "/books/",
        json={
            "isbn": "ISBN-B",
            "author_id": 1,
            "name": "Book B",
            "price": 20.0,
            "genre": "Sci-Fi",
            "publisher": "OtherPub",
            "year_published": 2022,
            "copies_sold": 500,
        },
    )

    # 1. Top Sellers (descending order)
    res = client.get("/books/top-sellers")
    assert res.status_code == 200
    assert res.json()[0]["isbn"] == "ISBN-B"

    # 2. Filter by Genre
    res = client.get("/books/genre/fantasy")
    assert res.status_code == 200
    assert len(res.json()) == 1
    assert res.json()[0]["isbn"] == "ISBN-A"

    # 3. Apply Publisher Discount (20% off $50.00 = $40.00)
    discount_res = client.put("/books/discount", json={"publisher": "TestPub", "discount_percent": 20.0})
    assert discount_res.status_code == 200

    check_res = client.get("/books/ISBN-A")
    assert check_res.json()["price"] == 40.0


# ==========================================
# Feature 3: Shopping Cart Tests
# ==========================================
def test_feature_3_shopping_cart(client):
    # Setup User and Book
    client.post("/users/", json={"username": "shopper", "password": "123"})
    client.post("/authors/", json={"first_name": "A", "last_name": "B", "publisher": "P"})
    client.post(
        "/books/",
        json={
            "isbn": "CART-1",
            "author_id": 1,
            "name": "Book In Cart",
            "price": 25.50,
            "genre": "Tech",
            "publisher": "P",
            "year_published": 2020,
        },
    )

    # 1. Add Book to Cart
    res = client.post("/cart/", json={"user_id": 1, "book_isbn": "CART-1"})
    assert res.status_code == 201

    # 2. Get Cart Books
    res = client.get("/cart/1")
    assert res.status_code == 200
    assert len(res.json()) == 1

    # 3. Get Cart Subtotal
    res = client.get("/cart/1/subtotal")
    assert res.status_code == 200
    assert res.json()["subtotal"] == 25.50

    # 4. Remove Book from Cart
    res = client.delete("/cart/1/books/CART-1")
    assert res.status_code == 200

    # Verify Cart is empty
    res = client.get("/cart/1")
    assert len(res.json()) == 0


# ==========================================
# Feature 6: Wishlist Management Tests
# ==========================================
def test_feature_6_wishlists(client):
    # Setup User and Book
    client.post("/users/", json={"username": "wisher", "password": "123"})
    client.post("/authors/", json={"first_name": "A", "last_name": "B", "publisher": "P"})
    client.post(
        "/books/",
        json={
            "isbn": "WISH-1",
            "author_id": 1,
            "name": "Wish Book",
            "price": 15.00,
            "genre": "Fiction",
            "publisher": "P",
            "year_published": 2019,
        },
    )

    # 1. Create Wishlist
    res = client.post("/wishlists/", json={"user_id": 1, "name": "Favorites"})
    assert res.status_code == 201

    # Unique name check per user
    res_dup = client.post("/wishlists/", json={"user_id": 1, "name": "Favorites"})
    assert res_dup.status_code == 400

    # Enforce 3-wishlist maximum
    client.post("/wishlists/", json={"user_id": 1, "name": "List 2"})
    client.post("/wishlists/", json={"user_id": 1, "name": "List 3"})
    res_overflow = client.post("/wishlists/", json={"user_id": 1, "name": "List 4"})
    assert res_overflow.status_code == 400

    # 2. Add Book to Wishlist
    res = client.post("/wishlists/items", json={"wishlist_id": 1, "book_isbn": "WISH-1"})
    assert res.status_code == 201

    # 3. List Books in Wishlist
    res = client.get("/wishlists/1/books")
    assert res.status_code == 200
    assert len(res.json()) == 1

    # 4. Transfer Book from Wishlist to Shopping Cart
    res = client.delete("/wishlists/1/books/WISH-1")
    assert res.status_code == 200

    # Verify book was removed from wishlist
    res = client.get("/wishlists/1/books")
    assert len(res.json()) == 0

    # Verify book was automatically moved into shopping cart
    cart_res = client.get("/cart/1")
    assert len(cart_res.json()) == 1
    assert cart_res.json()[0]["isbn"] == "WISH-1"
