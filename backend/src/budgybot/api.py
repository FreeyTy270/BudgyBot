import logging

from sqlmodel import SQLModel, create_engine
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware



app = FastAPI(debug=True, title="Budgybot", version="0.1.0")
sql_path = "sqlite:///backend/budgybot.db"
records_engine = create_engine(sql_path)
SQLModel.metadata.create_all(records_engine)
log = logging.getLogger("budgybot")

origins = [
        "http://localhost:5173",
        "http://192.168.50.85:5173",
]

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Svelte dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
@app.get("/api")
async def root():
    return {"message": "Welcome to budgybot!!!!"}


