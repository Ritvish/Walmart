from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from app.database import create_tables
from app.routers import auth, products, cart, club, orders, clubbed_cart
import os
import uvicorn

# Create FastAPI app
app = FastAPI(
    title="BuddyCart API",
    description="Smart order clubbing system for delivery cost savings",
    version="1.0.0"
)

# CORS middleware
origins = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:3001").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(products.router)
app.include_router(cart.router)
app.include_router(club.router)
app.include_router(orders.router)
app.include_router(clubbed_cart.router)

@app.on_event("startup")
def startup_event():
    """Create database tables on startup"""
    create_tables()

@app.get("/")
def read_root():
    return {
        "message": "Welcome to BuddyCart API",
        "description": "Smart order clubbing system for delivery cost savings",
        "version": "1.0.0",
        "docs_url": "/docs"
    }

@app.get("/health")
def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
