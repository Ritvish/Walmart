from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from app.database import create_tables, SessionLocal
from app.routers import auth, products, cart, club, orders, clubbed_cart, split_payment
from app.crud import timeout_expired_buddies, cleanup_old_buddy_entries
import os
import uvicorn
import asyncio
import threading

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
app.include_router(split_payment.router)

@app.on_event("startup")
def startup_event():
    """Create database tables on startup"""
    create_tables()
    
    # Start background cleanup task
    global cleanup_thread
    cleanup_thread = threading.Thread(target=cleanup_task, daemon=True)
    cleanup_thread.start()
    print("Background cleanup task started")

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

# Background cleanup task
def cleanup_task():
    """Background task to clean up expired buddy queue entries"""
    while True:
        try:
            db = SessionLocal()
            try:
                # Mark expired entries as TIMED_OUT
                expired_count = timeout_expired_buddies(db)
                if expired_count > 0:
                    print(f"Marked {expired_count} buddy queue entries as timed out")
                
                # Clean up old entries (older than 24 hours)
                deleted_count = cleanup_old_buddy_entries(db, hours_old=24)
                if deleted_count > 0:
                    print(f"Cleaned up {deleted_count} old buddy queue entries")
                    
            finally:
                db.close()
        except Exception as e:
            print(f"Error in cleanup task: {e}")
        
        # Sleep for 5 minutes
        import time
        time.sleep(300)

# Start background cleanup task
cleanup_thread = threading.Thread(target=cleanup_task, daemon=True)
cleanup_thread.start()

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
