import os
from pathlib import Path
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

# Load .env from the same directory as this file
env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)

DATABASE_URL = os.getenv("DATABASE_URL")
print(f'database url === {DATABASE_URL}')
if not DATABASE_URL:
    # Default to local mongodb if not set
    DATABASE_URL = "mongodb://localhost:27017"


client = AsyncIOMotorClient(DATABASE_URL)