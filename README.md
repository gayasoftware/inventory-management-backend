# Inventory Management Backend

This is the backend service for the Inventory Management System, built with FastAPI and PostgreSQL.

## Tech Stack

- **Framework**: FastAPI
- **Database**: PostgreSQL
- **ORM**: SQLAlchemy
- **Validation**: Pydantic
- **Authentication**: JWT (JSON Web Tokens) with `passlib` and `bcrypt`

## Prerequisites

- Python 3.9 or higher
- PostgreSQL installed and running locally (or via Docker)

## Local Setup

1. **Create a Virtual Environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Environment Variables**:
   Ensure you have a PostgreSQL database running. The application expects a database connection. You may need to configure `DATABASE_URL` in your environment or code if not using the default `postgresql://user:password@localhost/inventory_db`.

4. **Run the Application**:
   ```bash
   uvicorn app.main:app --reload
   ```
   The API will be available at `http://localhost:8000`.
   API Documentation (Swagger UI) is at `http://localhost:8000/docs`.

## Docker

To build and run this service using Docker:

```bash
docker build -t inventory-backend .
docker run -p 8000:8000 inventory-backend
```

*Note: When running in Docker, ensure it can connect to your PostgreSQL instance (e.g., using docker-compose is recommended).*
