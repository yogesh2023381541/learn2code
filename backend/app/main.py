from datetime import UTC, date, datetime, timedelta

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from .config import settings
from .db import get_db
from .models import RefreshSession, Subject, SubjectEnrollment, User, UserActivity, UserProfile
from .schemas import (
    ActivityRequest,
    AuthResponse,
    DashboardResponse,
    LoginRequest,
    OnboardingRequest,
    RefreshRequest,
    SignupRequest,
    SubjectResponse,
    TokenResponse,
    UserResponse,
)
from .security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    hash_token,
    verify_password,
)

app = FastAPI(title="Learn2Code API", version="0.2.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
bearer = HTTPBearer(auto_error=False)


def profile_response(user: User) -> UserResponse:
    profile = user.profile
    profile_data = None
    if profile is not None:
        profile_data = {
            "experience_level": profile.experience_level,
            "learning_goal": profile.learning_goal,
            "preferred_language": profile.preferred_language,
            "daily_minutes": profile.daily_minutes,
            "subjects": profile.subjects.split(",") if profile.subjects else [],
            "learning_hours": profile.learning_hours,
            "topics_completed": profile.topics_completed,
            "problems_solved": profile.problems_solved,
            "current_streak": profile.current_streak,
        }
    return UserResponse(
        id=user.id,
        full_name=user.full_name,
        email=user.email,
        role=user.role,
        profile=profile_data,
    )


def create_session_tokens(user: User, db: Session) -> tuple[str, str]:
    access_token = create_access_token(user.id)
    refresh_token, token_id, expires_at = create_refresh_token(user.id)
    db.add(
        RefreshSession(
            user_id=user.id,
            token_id=token_id,
            token_hash=hash_token(refresh_token),
            expires_at=expires_at,
        ),
    )
    return access_token, refresh_token


def current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer),
    db: Session = Depends(get_db),
) -> User:
    if credentials is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")
    try:
        payload = decode_token(credentials.credentials, "access")
        user_id = int(payload["sub"])
    except (ValueError, KeyError, TypeError) as error:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid access token") from error
    user = db.get(User, user_id)
    if user is None or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User is unavailable")
    return user


def auth_response(user: User, access_token: str, refresh_token: str) -> AuthResponse:
    return AuthResponse(
        user=profile_response(user),
        access_token=access_token,
        refresh_token=refresh_token,
    )


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/auth/signup", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
def signup(payload: SignupRequest, db: Session = Depends(get_db)) -> AuthResponse:
    email = str(payload.email).lower()
    if db.scalar(select(User).where(User.email == email)) is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="An account with this email already exists")
    user = User(full_name=payload.full_name.strip(), email=email, password_hash=hash_password(payload.password))
    db.add(user)
    db.flush()
    db.add(UserProfile(user_id=user.id))
    access_token, refresh_token = create_session_tokens(user, db)
    db.commit()
    db.refresh(user)
    return auth_response(user, access_token, refresh_token)


@app.post("/api/auth/login", response_model=AuthResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> AuthResponse:
    user = db.scalar(select(User).where(User.email == str(payload.email).lower()))
    if user is None or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Email or password is incorrect")
    access_token, refresh_token = create_session_tokens(user, db)
    db.commit()
    return auth_response(user, access_token, refresh_token)


@app.post("/api/auth/refresh", response_model=TokenResponse)
def refresh(payload: RefreshRequest, db: Session = Depends(get_db)) -> TokenResponse:
    try:
        claims = decode_token(payload.refresh_token, "refresh")
        token_id = str(claims["jti"])
        user_id = int(claims["sub"])
    except (ValueError, KeyError, TypeError) as error:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token") from error
    session = db.scalar(
        select(RefreshSession).where(
            RefreshSession.token_id == token_id,
            RefreshSession.token_hash == hash_token(payload.refresh_token),
        ),
    )
    expires_at = session.expires_at.replace(tzinfo=UTC) if session and session.expires_at.tzinfo is None else session.expires_at if session else None
    if session is None or session.revoked_at is not None or expires_at <= datetime.now(UTC):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh session is invalid")
    user = db.get(User, user_id)
    if user is None or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User is unavailable")
    session.revoked_at = datetime.now(UTC)
    access_token, refresh_token = create_session_tokens(user, db)
    db.commit()
    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


@app.post("/api/auth/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(payload: RefreshRequest, db: Session = Depends(get_db)) -> None:
    try:
        claims = decode_token(payload.refresh_token, "refresh")
        token_id = str(claims["jti"])
    except (ValueError, KeyError, TypeError):
        return
    session = db.scalar(select(RefreshSession).where(RefreshSession.token_id == token_id))
    if session is not None and session.revoked_at is None:
        session.revoked_at = datetime.now(UTC)
        db.commit()


@app.get("/api/auth/me", response_model=UserResponse)
def me(user: User = Depends(current_user)) -> User:
    return profile_response(user)


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
    selected_subjects = list(
        db.scalars(select(Subject).where(Subject.name.in_(payload.subjects), Subject.is_published.is_(True))),
    )
    existing = {
        enrollment.subject_id: enrollment
        for enrollment in db.scalars(select(SubjectEnrollment).where(SubjectEnrollment.user_id == user.id))
    }
    for subject in selected_subjects:
        if subject.id not in existing:
            db.add(SubjectEnrollment(user_id=user.id, subject_id=subject.id))
    db.commit()
    db.refresh(user)
    return profile_response(user)


@app.get("/api/dashboard", response_model=DashboardResponse)
def dashboard(user: User = Depends(current_user), db: Session = Depends(get_db)) -> DashboardResponse:
    profile = user.profile or UserProfile(user_id=user.id)
    rows = db.execute(
        select(Subject, SubjectEnrollment)
        .join(SubjectEnrollment, SubjectEnrollment.subject_id == Subject.id)
        .where(SubjectEnrollment.user_id == user.id, Subject.is_published.is_(True))
        .order_by(Subject.name)
    ).all()
    subjects = [
        SubjectResponse(
            id=subject.id,
            name=subject.name,
            slug=subject.slug,
            category=subject.category,
            description=subject.description,
            difficulty=subject.difficulty,
            estimated_minutes=subject.estimated_minutes,
            progress=enrollment.progress,
        )
        for subject, enrollment in rows
    ]
    overall_progress = round(sum(subject.progress for subject in subjects) / len(subjects)) if subjects else 0
    today = datetime.now(UTC).date()
    activity_rows = db.execute(
        select(UserActivity.activity_date, func.sum(UserActivity.minutes))
        .where(
            UserActivity.user_id == user.id,
            UserActivity.activity_date >= today - timedelta(days=6),
        )
        .group_by(UserActivity.activity_date),
    ).all()
    activity_by_date = {activity_date: int(minutes) for activity_date, minutes in activity_rows}
    return DashboardResponse(
        learning_hours=profile.learning_hours,
        topics_completed=profile.topics_completed,
        problems_solved=profile.problems_solved,
        current_streak=profile.current_streak,
        overall_progress=overall_progress,
        recommended_subjects=subjects,
        weekly_activity=[activity_by_date.get(today - timedelta(days=offset), 0) for offset in range(6, -1, -1)],
        daily_goal_minutes=profile.daily_minutes or 30,
        today_minutes=activity_by_date.get(today, 0),
    )


@app.post("/api/users/me/activity", status_code=status.HTTP_201_CREATED)
def record_activity(
    payload: ActivityRequest,
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
) -> dict[str, int]:
    profile = user.profile or UserProfile(user_id=user.id)
    db.add(UserActivity(
        user_id=user.id,
        activity_date=datetime.now(UTC).date(),
        minutes=payload.minutes,
        activity_type=payload.activity_type,
    ))
    profile.learning_hours += payload.minutes / 60
    if payload.activity_type == "lesson":
        profile.topics_completed += 1
    db.add(profile)
    db.commit()
    return {"minutes": payload.minutes, "topics_completed": profile.topics_completed}


@app.get("/api/subjects", response_model=list[SubjectResponse])
def list_subjects(db: Session = Depends(get_db)) -> list[Subject]:
    return list(db.scalars(select(Subject).where(Subject.is_published.is_(True)).order_by(Subject.name)))
