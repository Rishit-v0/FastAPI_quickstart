from fastapi import FastAPI
from .database import engine, Base

from .routers.users import router as users_router, auth_router

# Create all tables in PostgreSQL
# Equivalent of running python manage.py migrate
# In production you'd use Alembic migrations instead
Base.metadata.create_all(bind=engine)

# Create the FastAPI app instance
# docs_url="/docs" = Swagger UI available at /docs (auto-generated, no extra work!)
# This is a massive FastAPI advantage over Django — free interactive API docs
app = FastAPI(
    title = "FastAPI Quickstart",
    description = "A simple FastAPI app with user registration and authentication",
    version = "1.0.0",
    docs_url="/docs",
)
 

# Include routers with prefix
# All user routes become /api/v1/users/...
# All auth routes become /api/v1/auth/...
app.include_router(users_router, prefix="/api/v1")
app.include_router(auth_router, prefix="/api/v1")

@app.get("/")
def root():
    return {"message": "Welcome to the FastAPI Quickstart!", "docs": "/docs"}
