from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from beanie import init_beanie
from database import client
from models import User, Family, College, Milestone, Tip, ChatMessage


from routers import router

app = FastAPI()

# Configure CORS
# Allow any localhost origin for development convenience
allow_origin_regex = r"http://(localhost|127\.0\.0\.1)(:\d+)?"

app.add_middleware(
    CORSMiddleware,
    # allow_origin_regex=[allow_origin_regex,"https://emma-advisor-prototype-yu32.vercel.app"],
    allow_origins=["https://emma-advisor-prototype-yu32.vercel.app"],
    allow_origin_regex=r"http://(localhost|127\.0\.0\.1)(:\d+)?",
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods including OPTIONS
    allow_headers=["*"],
)

# Initialize Beanie on startup
@app.on_event("startup")
async def startup_event():
    # Initialize Beanie with the specific database and models
    await init_beanie(database=client.emma_advisor_db, document_models=[User, Family, College, Milestone, Tip, ChatMessage])

# Include the API router
app.include_router(router)

@app.get("/healthz")
async def health_check():
    try:
        # Check MongoDB connection
        await client.server_info()
        db_status = "connected"
    except Exception as e:
        db_status = f"disconnected: {str(e)}"

    return {
        "status": "ok",
        "database": db_status
    }