from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.orm import Session

from .config import settings
from .db import Base, engine, get_db
from .models import Subject, User, UserProfile
from .schemas import (
    LoginRequest,
    OnboardingRequest,
    SignupRequest,
    SubjectResponse,
    TokenResponse,
    UserResponse,
)
from .security import create_access_token, decode_user_id, hash_password, verify_password

app = FastAPI(title="Learn2Code API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
bearer = HTTPBearer(auto_error=False)


@app.on_event("startup")
def create_tables() -> None:
    Base.metadata.create_all(bind=engine)


def current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer),
    db: Session = Depends(get_db),
) -> User:
    if credentials is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")
    try:
        user_id = decode_user_id(credentials.credentials)
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(error)) from error
    user = db.get(User, user_id)
    if user is None or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User is unavailable")
    return user


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/auth/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def signup(payload: SignupRequest, db: Session = Depends(get_db)) -> User:
    email = payload.email.lower()
    if db.scalar(select(User).where(User.email == email)) is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="An account with this email already exists")
    user = User(full_name=payload.full_name.strip(), email=email, password_hash=hash_password(payload.password))
    db.add(user)
    db.flush()
    db.add(UserProfile(user_id=user.id))
    db.commit()
    db.refresh(user)
    return user


@app.post("/api/auth/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
    user = db.scalar(select(User).where(User.email == payload.email.lower()))
    if user is None or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Email or password is incorrect")
    return TokenResponse(access_token=create_access_token(user.id))


@app.get("/api/auth/me", response_model=UserResponse)
def me(user: User = Depends(current_user)) -> User:
    return user


@app.put("/api/users/me/onboarding", response_model=UserResponse)
def save_onboarding(
    payload: OnboardingRequest,
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
) -> User:
    profile = user.profile or UserProfile(user_id=user.id)
    profile.experience_level = payload.experience_level
    profile.learning_goal = payload.learning_goal
    profile.preferred_language = payload.preferred_language
    profile.daily_minutes = payload.daily_minutes
    profile.subjects = ",".join(payload.subjects)
    db.add(profile)
    db.commit()
    db.refresh(user)
    return user


@app.get("/api/subjects", response_model=list[SubjectResponse])
def list_subjects(db: Session = Depends(get_db)) -> list[Subject]:
    return list(db.scalars(select(Subject).where(Subject.is_published.is_(True)).order_by(Subject.name)))
