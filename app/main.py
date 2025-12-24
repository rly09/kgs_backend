from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import engine, Base
from .routers import (
    auth_router,
    admin_router,
    categories_router,
    products_router,
    orders_router,
    settings_router
)

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="KPG Shop API",
    description="Backend API for KPG Shop application",
    version="1.0.0"
)

# Configure CORS for Flutter web and mobile
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router, prefix="/api")
app.include_router(admin_router, prefix="/api")
app.include_router(categories_router, prefix="/api")
app.include_router(products_router, prefix="/api")
app.include_router(orders_router, prefix="/api")
app.include_router(settings_router, prefix="/api")

@app.get("/")
def root():
    return {
        "message": "KPG Shop API",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
def health_check():
    return {"status": "healthy"}
