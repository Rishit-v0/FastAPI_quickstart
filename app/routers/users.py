from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from .. import models, schemas, auth
from ..database import get_db
from ..cache import cache_get, cache_set, cache_delete_pattern
import logging

logger = logging.getLogger(__name__)


# APIRouter groups related endpoints — equivalent of Django's include() + urls.py
# prefix = all routes in this router are prefixed with /users
# tags = grouping in Swagger UI documentation
router = APIRouter(prefix="/users", tags=["users"])

# Separate router for auth endpoints
auth_router = APIRouter(prefix="/auth", tags=["auth"])


@auth_router.post("/token", response_model=schemas.Token)
async def login(
    # OAuth2PasswordRequestForm extracts username + password from form data
    # FastAPI handles this automatically — you just declare it as a dependency
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    # Look up user by email (we use email as username field)
    user = db.query(models.User).filter(
        models.User.email == form_data.username
    ).first()

    # Verify user exists and password is correct
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Generate JWT token
    access_token = auth.create_access_token(
        data={"sub": user.email},  # sub = subject = user identifier
        expires_delta=timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/register", response_model=schemas.UserResponse, status_code=201)
async def register(user_data: schemas.UserCreate, db: Session = Depends(get_db)):
    # Check passwords match
    if user_data.password != user_data.password2:
        raise HTTPException(status_code=400, detail="Passwords do not match")

    # Check email not already taken
    existing = db.query(models.User).filter(
        models.User.email == user_data.email
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create user with hashed password
    user = models.User(
        email=user_data.email,
        username=user_data.username,
        hashed_password = auth.hash_password(user_data.password[:72])
    )
    db.add(user)      # stage the insert
    db.commit()       # execute INSERT — equivalent of Django's save()
    db.refresh(user)  # reload from DB to get auto-generated fields like id, created_at
    return user


@router.get("/me", response_model=schemas.UserResponse)
async def get_profile(current_user: models.User = Depends(auth.get_current_user)):
    # Depends(auth.get_current_user) = protected route
    # FastAPI automatically validates the JWT and injects the user object
    # Equivalent of Django's @permission_classes([IsAuthenticated])
    cache_key = f"user_profile_{int(current_user.id)}"
    cached = await cache_get(cache_key)
    if cached:
        logger.info(f"Cache Hit for user {cache_key}")
        cached['from_cache'] = True
        return cached
    logger.info(f"Cache Miss for user {cache_key} - fetching from DB")
    user_data = {
        "id": int(current_user.id),
        "email": current_user.email,
        "username": current_user.username,
        "created_at": str(current_user.created_at),
        "is_active": current_user.is_active,
        "from_cache": False,
    }
    
    await cache_set(cache_key, user_data, ttl=600)  # Cache for 10 minutes
    return current_user


@router.post("/me", response_model=schemas.UserResponse)
async def update_profile(
    update_data: schemas.UserUpdate,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    for field, value in update_data.dict(exclude_unset=True).items():
        setattr(current_user, field, value)
    db.commit()
    db.refresh(current_user)

    # Invalidate cache for this user
    await cache_delete_pattern(f"user_profile_{int(current_user.id)}*")
    logger.info(f"Cache invalidated for user {int(current_user.id)} after profile update")
    return current_user