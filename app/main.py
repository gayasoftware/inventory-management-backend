from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from . import models, database
from .routers import auth, items, transactions

models.Base.metadata.create_all(bind=database.engine)

# Auto-migration for margin column
from sqlalchemy import text, inspect
try:
    inspector = inspect(database.engine)
    if inspector.has_table("items"):
        columns = [c["name"] for c in inspector.get_columns("items")]
        if "margin" not in columns:
            print("Migrating database: Adding 'margin' column to 'items' table...")
            with database.engine.connect() as conn:
                conn.execute(text("ALTER TABLE items ADD COLUMN margin FLOAT DEFAULT 0.0"))
                conn.commit()
            print("Migration successful.")
except Exception as e:
    print(f"Migration failed: {e}")

app = FastAPI(title="Inventory Management System")

origins = [
    "http://localhost:5173",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(items.router)
app.include_router(transactions.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to the Inventory Management System API"}
