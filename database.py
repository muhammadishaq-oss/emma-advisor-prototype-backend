import os
import certifi
from pathlib import Path
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

# Load .env from the same directory as this file
env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)

DATABASE_URL = os.getenv("DATABASE_URL")

# Mask the password in logs
if DATABASE_URL:
    masked_url = DATABASE_URL.split('@')[-1] if '@' in DATABASE_URL else "..."
    print(f'database url target === ...@{masked_url}')
else:
    # Default to local mongodb if not set
    DATABASE_URL = "mongodb://localhost:27017"
    print("DATABASE_URL not set, using default local connection.")


# Use certifi for valid SSL certificates (The Robust Fix)
# tlsAllowInvalidCertificates caused internal errors, so we use proper CAs now.
# However, for debugging Render connection issues, we can try to be more permissive if needed
# but usually this error is due to IP Whitelisting on Atlas.
client = AsyncIOMotorClient(
    DATABASE_URL,
    tls=True,
    tlsCAFile=certifi.where(),
    serverSelectionTimeoutMS=5000,
    # tlsAllowInvalidCertificates=True # Uncomment this if you suspect certificate issues, but it's unsafe for prod
)