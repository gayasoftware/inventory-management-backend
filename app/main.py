from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from . import models, database
from .routers import auth, products, orders, inventory, users

models.Base.metadata.create_all(bind=database.engine)

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
app.include_router(products.router)
app.include_router(orders.router)
app.include_router(inventory.router)
app.include_router(users.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to the Inventory Management System API"}
