import logging
import os
import sys

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from budgybot.records import create_db_and_tables
from budgybot.api import transactions

load_dotenv()

DEFAULT_ARCHIVE_DIR = os.getenv("DEFAULT_ARCHIVE_DIR", "../archives")
API_VERSION = os.getenv("API_VERSION", "v1")
app = FastAPI(debug=True, title="Budgybot", version=API_VERSION)

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

log = logging.getLogger("budgybot")

app.include_router(transactions.router)

create_db_and_tables()

try:
    uvicorn.run("budgybot.__main__:app", host="0.0.0.0", port=8000, reload=True)
    sys.exit(0)
except Exception as e:
    log.error(e)
    print(e)
    sys.exit(1)
