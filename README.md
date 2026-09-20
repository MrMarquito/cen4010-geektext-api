# Feature 4: Book Details API

Owner: Will

Branch: `book-details`


## Overview
Implements backend for book creation, book retrieval by ISBN, author creation, and querying books by author using FastAPI, SQLAlchemy, and SQLite.

## Implemented Endpoints

| Method | Endpoint | Description | Status Code |
| :--- | :--- | :--- | :--- |
| `POST` | `/books/` | Create a new book | 201 Created / 409 Conflict |
| `GET` | `/books/{isbn}` | Retrieve book details by ISBN | 200 OK / 404 Not Found |
| `POST` | `/authors/` | Create a new author | 201 Created |
| `GET` | `/authors/{author_id}/books` | Retrieve all books by an author | 200 OK / 404 Not Found |

## How to Run & Verify

1. Activate your virtual environment and install dependencies.
2. Start the local development server:
```bash
   uvicorn api.api:app --reload
```

## UML Diagrams

### Use Case Diagram
![Use Case Diagram](diagrams/use_case_book-details.png)

### Class Diagram
![Class Diagram](diagrams/classes_book-details.png)

### Sequence Diagram
![Sequence Diagram](diagrams/sequence_book_creation.png)