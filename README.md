# CEN 4010 - GeekText RESTful API Project Fall 2026

An end-to-end, full-stack bookstore application tailored for technology, software architecture, and speculative fiction literature. The system pairs a high-performance FastAPI backend using SQLAlchemy ORM and SQLite with a responsive, modern Flutter Web client deployed via automated CI/CD to GitHub Pages.

---

## Architecture & Tech Stack

* **Backend:** FastAPI (Python 3.12+), Pydantic v2 validation, Uvicorn ASGI server
* **Database & ORM:** SQLite with SQLAlchemy ORM (configured for concurrency and foreign key cascades)
* **Frontend:** Flutter Web (Material 3 design system, procedural canvas graphics, interactive hover states)
* **Testing & Quality:** Pytest with in-memory SQLite dependency injection and HTTPX test client
* **Deployment & CI/CD:** GitHub Actions automated deployment to GitHub Pages with live Cloudflare Quick Tunnel backend resolution

---

## Core Implemented Features

1. **Book Browsing & Sorting (Feature 1):**
   * Filter books by genre (Technology, Sci-Fi, Fantasy, Fiction).
   * Retrieve Top 10 best-selling titles ranked by sales volume.
   * Apply publisher-wide percentage discounts in real-time.

2. **User Profile Management (Feature 2):**
   * Create user accounts with unique username validation.
   * Retrieve user profiles and update non-immutable fields (name, address, password) while enforcing email read-only security.
   * Link multiple credit cards to user profiles.

3. **Shopping Cart Subsystem (Feature 3):**
   * Add books to persistent shopping carts.
   * Real-time cart subtotal calculation.
   * View all active cart items and remove individual titles with instant UI recalculation.

4. **Book Details & Author Administration (Feature 4):**
   * Add authors and register books associated with specific author IDs.
   * Query individual books by ISBN.
   * Query catalog titles filtered by Author ID.

5. **Ratings & Reader Reviews (Feature 5):**
   * Submit 1–5 star ratings and written text reviews.
   * Real-time calculation and display of a book's average star rating.
   * View datestamped customer comments.

6. **Wishlist Management (Feature 6):**
   * Create up to 3 distinct wishlists per user account.
   * Add titles to specific wishlists.
   * Seamless single-action transfer of books from a wishlist directly into the active shopping cart.

---

## Project Structure

```text
geektext/
├── .github/
│   └── workflows/
│       ├── deploy_pages.yml      # CI/CD Flutter Web builder & GitHub Pages deployer
│       └── test.yml              # Automated Pytest suite runner on git push
├── api/
│   └── api.py                   # FastAPI application routes & Pydantic schemas
├── db/
│   └── db.py                    # SQLAlchemy database engine, session, & schema models
├── lib/
│   ├── models/                  # Dart data classes (Book, Comment, User, Wishlist)
│   ├── screens/                 # BookDetails, Cart, Wishlist, and Profile screens
│   ├── services/                # ApiService HTTP client & dynamic backend discovery
│   ├── widgets/                 # Procedural BookCover & InteractiveBookCard components
│   └── main.dart                # Application entrypoint, catalog grid, & navigation
├── test_api.py                  # Pytest integration tests covering all 6 feature modules
├── seed_data.py                 # Real-world catalog, author, user, & review seeder
├── requirements.txt             # Python runtime and testing dependencies
└── pubspec.yaml                 # Flutter package definitions
