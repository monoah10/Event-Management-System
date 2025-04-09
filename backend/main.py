from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware

from backend.auth import DBRateLimiter
from backend.routes import user_routes, event_routes

app = FastAPI(
    title="Event Management API",
    description="An API for managing users, events, and participation",
    version="1.0.0",
    dependencies=[Depends(DBRateLimiter)]
)

# CORS for frontend interaction
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register Routes
app.include_router(user_routes.router)
app.include_router(event_routes.router)

@app.get("/")
async def root():
    return {"message": "Event Management API is running"}
