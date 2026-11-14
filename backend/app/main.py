from datetime import UTC, date, datetime, timedelta
import csv
import io
import json

from fastapi import Depends, FastAPI, HTTPException, Query, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from .config import settings
from .db import get_db
from .models import (
    AIConversation,
    AIFeedback,
    AIMessage,
    AIUsageLog,
    AIRecommendation,
    AdminContentDraft,
    Flashcard,
    FlashcardReview,
    Lesson,
    LessonProgress,
    PracticeProblem,
    PracticeTestCase,
    PracticeProblemProgress,
    PracticeSubmission,
    ProblemImportJob,
    PersonalizedRoadmap,
    PersonalizedRoadmapNode,
    Quiz,
    QuizAttempt,
    QuizQuestion,
    RevisionSession,
    RefreshSession,
    Subject,
    SubjectEnrollment,
    User,
    UserActivity,
    UserBookmark,
    UserHistory,
    UserProfile,
)
from .services.code_runner import CodeRunnerError, run_code
from .schemas import (
    AdminDraftRequest,
    AdminDraftResponse,
    AIConversationCreateRequest,
    AIConversationResponse,
    AIFeedbackRequest,
    AIMessageRequest,
    AIMessageResponse,
    CodeAssistantRequest,
    CodeRunRequest,
    CodeRunResponse,
    V1CodeRunRequest,
    V1SubmissionRequest,
    ActivityRequest,
    AuthResponse,
    BookmarkRequest,
    BookmarkResponse,
    DashboardResponse,
    HistoryResponse,
    LoginRequest,
    LessonResponse,
    OnboardingRequest,
    PracticeProblemResponse,
    ProblemProgressRequest,
    ProblemProgressResponse,
    SubmissionHistoryResponse,
    ProblemImportRequest,
    ProblemImportResponse,
    AdminProblemUpdateRequest,
    AdminDashboardResponse,
    AdminTestCaseRequest,
    AdminTestCaseResponse,
    CodingAnalyticsResponse,
    ProfileUpdateRequest,
    QuizAttemptRequest,
    QuizAttemptResponse,
    QuizGenerateRequest,
    QuizQuestionResponse,
    QuizResponse,
    RecommendationResponse,
    RefreshRequest,
    SignupRequest,
    SubmissionRequest,
    SubmissionResponse,
    SubjectResponse,
    TokenResponse,
    UserResponse,
    FlashcardResponse,
    RevisionResponse,
    RoadmapRequest,
    RoadmapResponse,
    RoadmapNodeResponse,
)
from .services.ai.chat_service import AIProviderError, generate_reply
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


def require_admin(user: User) -> User:
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return user


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


def ai_conversation_response(conversation: AIConversation, messages: list[AIMessage] | None = None) -> AIConversationResponse:
    return AIConversationResponse(
        id=conversation.id,
        title=conversation.title,
        teaching_mode=conversation.teaching_mode,
        created_at=conversation.created_at.isoformat(),
        updated_at=conversation.updated_at.isoformat(),
        messages=[
            AIMessageResponse(id=message.id, role=message.role, content=message.content, created_at=message.created_at.isoformat())
            for message in (messages or [])
        ],
    )


def owned_conversation(conversation_id: int, user: User, db: Session) -> AIConversation:
    conversation = db.scalar(select(AIConversation).where(
        AIConversation.id == conversation_id, AIConversation.user_id == user.id,
    ))
    if conversation is None:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return conversation


@app.post("/api/ai/conversations", response_model=AIConversationResponse, status_code=201)
def create_ai_conversation(
    payload: AIConversationCreateRequest,
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
) -> AIConversationResponse:
    conversation = AIConversation(user_id=user.id, title=payload.title, teaching_mode=payload.teaching_mode)
    db.add(conversation)
    db.commit()
    db.refresh(conversation)
    return ai_conversation_response(conversation)


@app.get("/api/ai/conversations", response_model=list[AIConversationResponse])
def list_ai_conversations(user: User = Depends(current_user), db: Session = Depends(get_db)) -> list[AIConversationResponse]:
    conversations = db.scalars(select(AIConversation).where(
        AIConversation.user_id == user.id,
    ).order_by(AIConversation.updated_at.desc()))
    return [ai_conversation_response(conversation) for conversation in conversations]


@app.get("/api/ai/conversations/{conversation_id}", response_model=AIConversationResponse)
def get_ai_conversation(
    conversation_id: int,
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
) -> AIConversationResponse:
    conversation = owned_conversation(conversation_id, user, db)
    messages = list(db.scalars(select(AIMessage).where(
        AIMessage.conversation_id == conversation.id,
    ).order_by(AIMessage.created_at)))
    return ai_conversation_response(conversation, messages)


@app.delete("/api/ai/conversations/{conversation_id}", status_code=204)
def delete_ai_conversation(
    conversation_id: int,
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
) -> None:
    conversation = owned_conversation(conversation_id, user, db)
    db.delete(conversation)
    db.commit()


@app.post("/api/ai/conversations/{conversation_id}/messages", response_model=AIMessageResponse, status_code=201)
def send_ai_message(
    conversation_id: int,
    payload: AIMessageRequest,
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
) -> AIMessageResponse:
    conversation = owned_conversation(conversation_id, user, db)
    since = datetime.now(UTC) - timedelta(minutes=1)
    recent_requests = db.scalar(select(func.count(AIUsageLog.id)).where(
        AIUsageLog.user_id == user.id, AIUsageLog.created_at >= since,
    )) or 0
    if recent_requests >= settings.ai_requests_per_minute:
        raise HTTPException(status_code=429, detail="AI usage limit reached. Try again in a minute.")
    history = list(db.scalars(select(AIMessage).where(
        AIMessage.conversation_id == conversation.id,
    ).order_by(AIMessage.created_at).limit(30)))
    user_message = AIMessage(
        conversation_id=conversation.id, role="user", content=payload.content,
        context_json=json.dumps(payload.context, separators=(",", ":")),
    )
    db.add(user_message)
    db.flush()
    try:
        result = generate_reply(
            [{"role": message.role, "content": message.content} for message in history] + [
                {"role": "user", "content": payload.content},
            ],
            conversation.teaching_mode,
            payload.context,
        )
    except AIProviderError as error:
        db.rollback()
        raise HTTPException(status_code=503, detail=str(error)) from error
    assistant_message = AIMessage(conversation_id=conversation.id, role="assistant", content=result.content)
    db.add(assistant_message)
    db.add(AIUsageLog(
        user_id=user.id, conversation_id=conversation.id,
        prompt_tokens=result.prompt_tokens, completion_tokens=result.completion_tokens,
        model=settings.ai_provider_model,
    ))
    conversation.updated_at = datetime.now(UTC)
    db.commit()
    db.refresh(assistant_message)
    return AIMessageResponse(
        id=assistant_message.id, role=assistant_message.role,
        content=assistant_message.content, created_at=assistant_message.created_at.isoformat(),
    )


@app.post("/api/ai/messages/{message_id}/feedback", status_code=201)
def add_ai_feedback(
    message_id: int,
    payload: AIFeedbackRequest,
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
) -> dict[str, str]:
    message = db.scalar(select(AIMessage).join(AIConversation).where(
        AIMessage.id == message_id, AIConversation.user_id == user.id,
    ))
    if message is None:
        raise HTTPException(status_code=404, detail="Message not found")
    db.add(AIFeedback(user_id=user.id, message_id=message.id, rating=payload.rating, comment=payload.comment))
    db.commit()
    return {"status": "recorded"}


@app.post("/api/ai/code-assistant")
def code_assistant(
    payload: CodeAssistantRequest,
    user: User = Depends(current_user),
) -> dict[str, str]:
    context = {"language": payload.language, "task": payload.task}
    if payload.error_message:
        context["compiler_error"] = payload.error_message
    try:
        result = generate_reply(
            [{"role": "user", "content": f"Review this code for {payload.task}:\n```{payload.language}\n{payload.code}\n```"}],
            "practical",
            context,
        )
    except AIProviderError as error:
        raise HTTPException(status_code=503, detail=str(error)) from error
    return {"content": result.content}


@app.get("/api/recommendations", response_model=list[RecommendationResponse])
def recommendations(user: User = Depends(current_user), db: Session = Depends(get_db)) -> list[RecommendationResponse]:
    profile = user.profile
    recommendations: list[AIRecommendation] = []
    activity_count = db.scalar(select(func.count(UserActivity.id)).where(UserActivity.user_id == user.id)) or 0
    if profile and profile.topics_completed == 0:
        subject = db.scalar(select(Subject).where(Subject.is_published.is_(True)).order_by(Subject.id))
        if subject:
            recommendations.append(AIRecommendation(
                user_id=user.id, title=f"Start {subject.name}", reason="No completed topics yet; begin with the first published learning path.",
                target_type="subject", target_id=subject.id, evidence_json=json.dumps({"topics_completed": 0}),
            ))
    if activity_count == 0:
        subject = db.scalar(select(Subject).where(Subject.is_published.is_(True)).order_by(Subject.id))
        if subject:
            recommendations.append(AIRecommendation(
                user_id=user.id, title="Build your first study habit", reason="No learning activity has been recorded. Complete a short lesson today.",
                target_type="subject", target_id=subject.id, evidence_json=json.dumps({"activity_count": 0}),
            ))
    if profile and profile.problems_solved == 0:
        problem = db.scalar(select(PracticeProblem).order_by(PracticeProblem.id))
        if problem:
            recommendations.append(AIRecommendation(
                user_id=user.id, title="Try an easy coding problem", reason="Practice history shows no accepted problems yet.",
                target_type="problem", target_id=problem.id, evidence_json=json.dumps({"problems_solved": 0}),
            ))
    for item in recommendations:
        db.add(item)
    db.commit()
    return [
        RecommendationResponse(
            id=item.id, title=item.title, reason=item.reason, target_type=item.target_type,
            target_id=item.target_id, evidence=json.loads(item.evidence_json),
        ) for item in recommendations
    ]


@app.get("/api/analytics")
def analytics(user: User = Depends(current_user), db: Session = Depends(get_db)) -> dict[str, object]:
    activity = db.execute(select(UserActivity.activity_type, func.sum(UserActivity.minutes)).where(
        UserActivity.user_id == user.id,
    ).group_by(UserActivity.activity_type)).all()
    completed_lessons = db.scalar(select(func.count(LessonProgress.id)).where(LessonProgress.user_id == user.id)) or 0
    submissions = db.scalar(select(func.count(PracticeSubmission.id)).where(PracticeSubmission.user_id == user.id)) or 0
    accepted = db.scalar(select(func.count(PracticeSubmission.id)).where(
        PracticeSubmission.user_id == user.id, PracticeSubmission.status == "accepted",
    )) or 0
    return {
        "measured": {
            "activity_minutes_by_type": {kind: int(minutes) for kind, minutes in activity},
            "completed_lessons": completed_lessons,
            "practice_submissions": submissions,
            "accepted_submissions": accepted,
            "acceptance_rate": round(accepted / submissions * 100, 1) if submissions else 0,
            "learning_hours": user.profile.learning_hours if user.profile else 0,
        },
        "insights": [
            "Complete another lesson to establish a measurable learning trend." if completed_lessons < 2 else "Your lesson completion history is building a consistent trend.",
            "Try an easy practice problem to improve coding evidence." if accepted == 0 else "Keep practicing to strengthen problem-solving fluency.",
        ],
    }


@app.post("/api/roadmaps", response_model=RoadmapResponse, status_code=201)
def create_roadmap(
    payload: RoadmapRequest,
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
) -> RoadmapResponse:
    profile = user.profile
    roadmap = PersonalizedRoadmap(
        user_id=user.id, goal=payload.goal,
        experience_level=profile.experience_level if profile and profile.experience_level else "beginner",
    )
    db.add(roadmap)
    db.flush()
    subjects = list(db.scalars(select(Subject).where(Subject.is_published.is_(True)).order_by(Subject.id)))
    nodes: list[PersonalizedRoadmapNode] = []
    order = 0
    previous_id: int | None = None
    for subject in subjects:
        lessons = list(db.scalars(select(Lesson).where(Lesson.subject_id == subject.id).order_by(Lesson.order_index).limit(3)))
        for lesson in lessons:
            order += 1
            node = PersonalizedRoadmapNode(
                roadmap_id=roadmap.id, subject_id=subject.id, lesson_id=lesson.id,
                title=f"{subject.name}: {lesson.title}", order_index=order,
                estimated_minutes=lesson.estimated_minutes,
                prerequisite_ids=json.dumps([previous_id] if previous_id else []),
            )
            db.add(node)
            db.flush()
            nodes.append(node)
            previous_id = node.id
    db.commit()
    return RoadmapResponse(
        id=roadmap.id, goal=roadmap.goal, experience_level=roadmap.experience_level,
        nodes=[RoadmapNodeResponse(
            id=node.id, title=node.title, subject_id=node.subject_id, lesson_id=node.lesson_id,
            node_type=node.node_type, order_index=node.order_index, estimated_minutes=node.estimated_minutes,
            prerequisite_ids=json.loads(node.prerequisite_ids),
        ) for node in nodes],
    )


@app.post("/api/quizzes", response_model=QuizResponse, status_code=201)
def generate_quiz(
    payload: QuizGenerateRequest,
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
) -> QuizResponse:
    query = select(Lesson).order_by(Lesson.order_index)
    if payload.subject_id:
        query = query.where(Lesson.subject_id == payload.subject_id)
    lessons = list(db.scalars(query.limit(payload.question_count)))
    if not lessons:
        raise HTTPException(status_code=404, detail="No lesson content is available for this quiz")
    quiz = Quiz(user_id=user.id, subject_id=payload.subject_id, title="Generated learning check", difficulty=payload.difficulty, question_count=len(lessons))
    db.add(quiz)
    db.flush()
    questions: list[QuizQuestion] = []
    for lesson in lessons:
        question = QuizQuestion(
            quiz_id=quiz.id, prompt=f"What is the main idea of '{lesson.title}'?",
            options_json=json.dumps([lesson.summary, "Skip the topic", "Delete the program", "None of these"]),
            correct_answer=lesson.summary, explanation=lesson.content,
        )
        db.add(question)
        db.flush()
        questions.append(question)
    db.commit()
    return QuizResponse(
        id=quiz.id, title=quiz.title, difficulty=quiz.difficulty,
        questions=[QuizQuestionResponse(id=q.id, prompt=q.prompt, options=json.loads(q.options_json), explanation=q.explanation) for q in questions],
    )


@app.post("/api/quizzes/{quiz_id}/attempts", response_model=QuizAttemptResponse, status_code=201)
def submit_quiz(
    quiz_id: int,
    payload: QuizAttemptRequest,
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
) -> QuizAttemptResponse:
    quiz = db.scalar(select(Quiz).where(Quiz.id == quiz_id, Quiz.user_id == user.id))
    if quiz is None:
        raise HTTPException(status_code=404, detail="Quiz not found")
    questions = list(db.scalars(select(QuizQuestion).where(QuizQuestion.quiz_id == quiz.id)))
    score = sum(payload.answers.get(str(q.id)) == q.correct_answer for q in questions)
    attempt = QuizAttempt(user_id=user.id, quiz_id=quiz.id, score=score, answers_json=json.dumps(payload.answers))
    db.add(attempt)
    db.commit()
    db.refresh(attempt)
    return QuizAttemptResponse(id=attempt.id, score=score, total=len(questions))


@app.get("/api/revision", response_model=list[RevisionResponse])
def revision_queue(user: User = Depends(current_user), db: Session = Depends(get_db)) -> list[RevisionResponse]:
    rows = db.scalars(select(RevisionSession).where(
        RevisionSession.user_id == user.id, RevisionSession.completed_at.is_(None),
    ).order_by(RevisionSession.due_at))
    return [RevisionResponse(id=row.id, topic=row.topic, due_at=row.due_at.isoformat(), interval_days=row.interval_days) for row in rows]


@app.post("/api/revision", response_model=RevisionResponse, status_code=201)
def create_revision(topic: str, user: User = Depends(current_user), db: Session = Depends(get_db)) -> RevisionResponse:
    row = RevisionSession(user_id=user.id, topic=topic, due_at=datetime.now(UTC) + timedelta(days=1), interval_days=1)
    db.add(row)
    db.commit()
    db.refresh(row)
    return RevisionResponse(id=row.id, topic=row.topic, due_at=row.due_at.isoformat(), interval_days=row.interval_days)


@app.post("/api/revision/{revision_id}/complete", response_model=RevisionResponse)
def complete_revision(revision_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)) -> RevisionResponse:
    row = db.scalar(select(RevisionSession).where(RevisionSession.id == revision_id, RevisionSession.user_id == user.id))
    if row is None:
        raise HTTPException(status_code=404, detail="Revision session not found")
    row.completed_at = datetime.now(UTC)
    row.interval_days = min(60, row.interval_days * 2)
    row.due_at = datetime.now(UTC) + timedelta(days=row.interval_days)
    row.completed_at = None
    db.commit()
    return RevisionResponse(id=row.id, topic=row.topic, due_at=row.due_at.isoformat(), interval_days=row.interval_days)


@app.post("/api/admin/drafts", response_model=AdminDraftResponse, status_code=201)
def create_admin_draft(payload: AdminDraftRequest, user: User = Depends(current_user), db: Session = Depends(get_db)) -> AdminDraftResponse:
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    draft = AdminContentDraft(author_id=user.id, content_type=payload.content_type, title=payload.title, body_json=json.dumps(payload.body))
    db.add(draft)
    db.commit()
    db.refresh(draft)
    return AdminDraftResponse(id=draft.id, content_type=draft.content_type, title=draft.title, status=draft.status, body=payload.body)


@app.post("/api/admin/drafts/{draft_id}/approve", response_model=AdminDraftResponse)
def approve_admin_draft(draft_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)) -> AdminDraftResponse:
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    draft = db.get(AdminContentDraft, draft_id)
    if draft is None:
        raise HTTPException(status_code=404, detail="Draft not found")
    draft.status = "approved"
    draft.reviewed_by = user.id
    db.commit()
    return AdminDraftResponse(id=draft.id, content_type=draft.content_type, title=draft.title, status=draft.status, body=json.loads(draft.body_json))


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


def lesson_response(lesson: Lesson, completed: bool = False) -> LessonResponse:
    return LessonResponse(
        id=lesson.id, subject_id=lesson.subject_id, title=lesson.title, slug=lesson.slug,
        summary=lesson.summary, content=lesson.content, code_example=lesson.code_example,
        video_url=lesson.video_url, order_index=lesson.order_index,
        estimated_minutes=lesson.estimated_minutes, completed=completed,
    )


@app.get("/api/subjects/{slug}/lessons", response_model=list[LessonResponse])
def list_lessons(
    slug: str,
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
) -> list[LessonResponse]:
    subject = db.scalar(select(Subject).where(Subject.slug == slug, Subject.is_published.is_(True)))
    if subject is None:
        raise HTTPException(status_code=404, detail="Subject not found")
    completed_ids = set(db.scalars(select(LessonProgress.lesson_id).where(LessonProgress.user_id == user.id)))
    lessons = db.scalars(select(Lesson).where(Lesson.subject_id == subject.id).order_by(Lesson.order_index))
    return [lesson_response(lesson, lesson.id in completed_ids) for lesson in lessons]


@app.get("/api/lessons/{lesson_id}", response_model=LessonResponse)
def get_lesson(
    lesson_id: int,
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
) -> LessonResponse:
    lesson = db.get(Lesson, lesson_id)
    if lesson is None:
        raise HTTPException(status_code=404, detail="Lesson not found")
    progress = db.scalar(select(LessonProgress).where(
        LessonProgress.user_id == user.id, LessonProgress.lesson_id == lesson.id,
    ))
    db.add(UserHistory(user_id=user.id, target_type="lesson", target_id=lesson.id))
    db.commit()
    return lesson_response(lesson, progress is not None)


@app.post("/api/lessons/{lesson_id}/complete", response_model=LessonResponse)
def complete_lesson(
    lesson_id: int,
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
) -> LessonResponse:
    lesson = db.get(Lesson, lesson_id)
    if lesson is None:
        raise HTTPException(status_code=404, detail="Lesson not found")
    progress = db.scalar(select(LessonProgress).where(
        LessonProgress.user_id == user.id, LessonProgress.lesson_id == lesson.id,
    ))
    if progress is None:
        db.add(LessonProgress(user_id=user.id, lesson_id=lesson.id))
        record = UserActivity(
            user_id=user.id, activity_date=datetime.now(UTC).date(),
            minutes=lesson.estimated_minutes, activity_type="lesson",
        )
        db.add(record)
        profile = user.profile or UserProfile(user_id=user.id)
        profile.learning_hours += lesson.estimated_minutes / 60
        profile.topics_completed += 1
        db.add(profile)
        enrollment = db.scalar(select(SubjectEnrollment).where(
            SubjectEnrollment.user_id == user.id, SubjectEnrollment.subject_id == lesson.subject_id,
        ))
        if enrollment is not None:
            total = db.scalar(select(func.count(Lesson.id)).where(Lesson.subject_id == lesson.subject_id)) or 1
            completed = db.scalar(select(func.count(LessonProgress.id)).join(Lesson, Lesson.id == LessonProgress.lesson_id).where(
                LessonProgress.user_id == user.id, Lesson.subject_id == lesson.subject_id,
            )) or 0
            enrollment.progress = min(100, round(completed / total * 100))
    db.commit()
    return lesson_response(lesson, True)


def practice_response(problem: PracticeProblem, solved: bool = False) -> PracticeProblemResponse:
    return PracticeProblemResponse(
        id=problem.id, title=problem.title, slug=problem.slug, description=problem.description,
        difficulty=problem.difficulty, category=problem.category,
        acceptance_rate=problem.acceptance_rate, solved=solved,
        topic=problem.topic, pattern=problem.pattern, constraints=problem.constraints,
        examples=json.loads(problem.examples_json or "[]"),
        hints=json.loads(problem.hints_json or "[]"),
        editorial=problem.editorial, reference_url=problem.reference_url,
        starter_code=problem.starter_code,
    )


@app.get("/api/practice/problems", response_model=list[PracticeProblemResponse])
def list_practice_problems(
    difficulty: str | None = Query(default=None, max_length=20),
    topic: str | None = Query(default=None, max_length=100),
    pattern: str | None = Query(default=None, max_length=100),
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
) -> list[PracticeProblemResponse]:
    solved_ids = set(db.scalars(select(PracticeSubmission.problem_id).where(
        PracticeSubmission.user_id == user.id, PracticeSubmission.status == "accepted",
    )))
    query = select(PracticeProblem).where(PracticeProblem.is_published.is_(True)).order_by(PracticeProblem.id)
    if difficulty:
        query = query.where(PracticeProblem.difficulty == difficulty)
    if topic:
        query = query.where(PracticeProblem.topic == topic)
    if pattern:
        query = query.where(PracticeProblem.pattern == pattern)
    problems = db.scalars(query)
    return [practice_response(problem, problem.id in solved_ids) for problem in problems]


def progress_response(progress: PracticeProblemProgress) -> ProblemProgressResponse:
    return ProblemProgressResponse(
        problem_id=progress.problem_id, status=progress.status, attempts=progress.attempts,
        bookmarked=progress.bookmarked,
        next_revision_at=progress.next_revision_at.isoformat() if progress.next_revision_at else None,
    )


@app.get("/api/practice/progress", response_model=list[ProblemProgressResponse])
def list_practice_progress(user: User = Depends(current_user), db: Session = Depends(get_db)) -> list[ProblemProgressResponse]:
    rows = db.scalars(select(PracticeProblemProgress).where(
        PracticeProblemProgress.user_id == user.id,
    ).order_by(PracticeProblemProgress.updated_at.desc()))
    return [progress_response(row) for row in rows]


@app.patch("/api/practice/problems/{problem_id}/progress", response_model=ProblemProgressResponse)
def update_practice_progress(
    problem_id: int,
    payload: ProblemProgressRequest,
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
) -> ProblemProgressResponse:
    if db.get(PracticeProblem, problem_id) is None:
        raise HTTPException(status_code=404, detail="Practice problem not found")
    progress = db.scalar(select(PracticeProblemProgress).where(
        PracticeProblemProgress.user_id == user.id, PracticeProblemProgress.problem_id == problem_id,
    ))
    if progress is None:
        progress = PracticeProblemProgress(user_id=user.id, problem_id=problem_id, attempts=0, status="not_started", bookmarked=False)
        db.add(progress)
    progress.status = payload.status
    if payload.bookmarked is not None:
        progress.bookmarked = payload.bookmarked
    if payload.status == "revision":
        progress.next_revision_at = datetime.now(UTC) + timedelta(days=1)
    db.commit()
    db.refresh(progress)
    return progress_response(progress)


@app.get("/api/practice/problems/{slug}", response_model=PracticeProblemResponse)
def get_practice_problem(slug: str, user: User = Depends(current_user), db: Session = Depends(get_db)) -> PracticeProblemResponse:
    problem = db.scalar(select(PracticeProblem).where(PracticeProblem.slug == slug))
    if problem is None:
        raise HTTPException(status_code=404, detail="Practice problem not found")
    solved = db.scalar(select(PracticeSubmission.id).where(
        PracticeSubmission.user_id == user.id, PracticeSubmission.problem_id == problem.id,
        PracticeSubmission.status == "accepted",
    )) is not None
    db.add(UserHistory(user_id=user.id, target_type="problem", target_id=problem.id))
    db.commit()
    return practice_response(problem, solved)


@app.post("/api/practice/problems/{problem_id}/run", response_model=CodeRunResponse)
def run_practice_code(
    problem_id: int,
    payload: CodeRunRequest,
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
) -> CodeRunResponse:
    if db.get(PracticeProblem, problem_id) is None:
        raise HTTPException(status_code=404, detail="Practice problem not found")
    try:
        result = run_code(payload.language, payload.code, payload.stdin)
    except CodeRunnerError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    return CodeRunResponse(
        status=result.status, stdout=result.stdout, stderr=result.stderr,
        duration_ms=result.duration_ms, memory_kb=result.memory_kb,
    )


def _normalized_output(value: str) -> str:
    lines = [" ".join(line.split()) for line in value.strip().splitlines()]
    return "\n".join(lines)


def _outputs_match(actual: str, expected: str) -> bool:
    if _normalized_output(actual) == _normalized_output(expected):
        return True
    try:
        return json.loads(actual) == json.loads(expected)
    except (json.JSONDecodeError, TypeError):
        return False


@app.post("/api/practice/problems/{problem_id}/submissions", response_model=SubmissionResponse, status_code=201)
def submit_practice(
    problem_id: int,
    payload: SubmissionRequest,
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
) -> SubmissionResponse:
    problem = db.get(PracticeProblem, problem_id)
    if problem is None:
        raise HTTPException(status_code=404, detail="Practice problem not found")
    test_cases = list(db.scalars(select(PracticeTestCase).where(
        PracticeTestCase.problem_id == problem.id,
    ).order_by(PracticeTestCase.order_index)))
    status = "accepted"
    passed_tests = 0
    duration_ms = 0
    memory_kb = 0
    stdout = ""
    stderr = ""
    for test_case in test_cases:
        try:
            result = run_code(payload.language, payload.code, test_case.stdin)
        except CodeRunnerError as error:
            raise HTTPException(status_code=400, detail=str(error)) from error
        duration_ms += result.duration_ms
        memory_kb = max(memory_kb, result.memory_kb)
        stdout, stderr = result.stdout, result.stderr
        if result.status == "time_limit_exceeded":
            status = "time_limit_exceeded"
            break
        if result.status != "accepted":
            status = result.status
            break
        if not _outputs_match(result.stdout, test_case.expected_stdout):
            status = "wrong_answer"
            break
        passed_tests += 1
    submission = PracticeSubmission(
        user_id=user.id, problem_id=problem.id, language=payload.language,
        code=payload.code, status=status, stdout=stdout, stderr=stderr,
        duration_ms=duration_ms, memory_kb=memory_kb,
        passed_tests=passed_tests, total_tests=len(test_cases),
    )
    db.add(submission)
    progress = db.scalar(select(PracticeProblemProgress).where(
        PracticeProblemProgress.user_id == user.id, PracticeProblemProgress.problem_id == problem.id,
    ))
    if progress is None:
        progress = PracticeProblemProgress(user_id=user.id, problem_id=problem.id, attempts=0, status="not_started", bookmarked=False)
        db.add(progress)
    progress.attempts += 1
    progress.status = "solved" if status == "accepted" else "attempted"
    if status == "accepted":
        progress.next_revision_at = datetime.now(UTC) + timedelta(days=1)
    profile = user.profile or UserProfile(user_id=user.id)
    already_solved = db.scalar(select(PracticeSubmission.id).where(
        PracticeSubmission.user_id == user.id, PracticeSubmission.problem_id == problem.id,
        PracticeSubmission.status == "accepted",
    )) is not None
    if status == "accepted" and not already_solved:
        profile.problems_solved += 1
        db.add(profile)
    db.commit()
    db.refresh(submission)
    return SubmissionResponse(
        id=submission.id, status=submission.status, language=submission.language,
        stdout=stdout, stderr=stderr, duration_ms=duration_ms,
        memory_kb=memory_kb, passed_tests=passed_tests, total_tests=len(test_cases),
    )


@app.post("/api/v1/code/run", response_model=CodeRunResponse)
def run_code_v1(
    payload: V1CodeRunRequest,
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
) -> CodeRunResponse:
    return run_practice_code(payload.problem_id, payload, user, db)


@app.post("/api/v1/code/submit", response_model=SubmissionResponse, status_code=201)
def submit_code_v1(
    payload: V1SubmissionRequest,
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
) -> SubmissionResponse:
    return submit_practice(payload.problem_id, payload, user, db)


@app.get("/api/submissions", response_model=list[SubmissionHistoryResponse])
def list_submissions(
    limit: int = Query(default=50, ge=1, le=200),
    problem_id: int | None = Query(default=None, gt=0),
    language: str | None = Query(default=None, max_length=40),
    verdict: str | None = Query(default=None, max_length=30),
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
) -> list[SubmissionHistoryResponse]:
    query = select(PracticeSubmission, PracticeProblem.title).join(
        PracticeProblem, PracticeProblem.id == PracticeSubmission.problem_id,
    ).where(PracticeSubmission.user_id == user.id).order_by(
        PracticeSubmission.submitted_at.desc(),
    ).limit(limit)
    if problem_id:
        query = query.where(PracticeSubmission.problem_id == problem_id)
    if language:
        query = query.where(PracticeSubmission.language == language)
    if verdict:
        query = query.where(PracticeSubmission.status == verdict)
    return [
        SubmissionHistoryResponse(
            id=submission.id, status=submission.status, language=submission.language,
            stdout=submission.stdout or "", stderr=submission.stderr or "",
            duration_ms=submission.duration_ms, memory_kb=submission.memory_kb or 0,
            passed_tests=submission.passed_tests,
            total_tests=submission.total_tests, problem_id=submission.problem_id,
            problem_title=title, code=submission.code,
            submitted_at=submission.submitted_at.isoformat(),
        )
        for submission, title in db.execute(query)
    ]


@app.get("/api/analytics/coding", response_model=CodingAnalyticsResponse)
def coding_analytics(user: User = Depends(current_user), db: Session = Depends(get_db)) -> CodingAnalyticsResponse:
    submissions = list(db.scalars(select(PracticeSubmission).where(
        PracticeSubmission.user_id == user.id,
    )))
    problem_ids = {row.problem_id for row in submissions}
    problems = {
        row.id: row for row in db.scalars(select(PracticeProblem).where(PracticeProblem.id.in_(problem_ids)))
    } if problem_ids else {}
    by_difficulty: dict[str, dict[str, int]] = {}
    by_topic: dict[str, dict[str, int]] = {}
    by_language: dict[str, int] = {}
    for submission in submissions:
        problem = problems.get(submission.problem_id)
        if problem is None:
            continue
        difficulty = by_difficulty.setdefault(problem.difficulty, {"attempted": 0, "solved": 0})
        difficulty["attempted"] += 1
        if submission.status == "accepted":
            difficulty["solved"] += 1
        topic = problem.topic or problem.category
        topic_stats = by_topic.setdefault(topic, {"attempted": 0, "solved": 0})
        topic_stats["attempted"] += 1
        if submission.status == "accepted":
            topic_stats["solved"] += 1
        by_language[submission.language] = by_language.get(submission.language, 0) + 1
    accepted = sum(1 for row in submissions if row.status == "accepted")
    solved = db.scalar(select(func.count()).select_from(PracticeProblemProgress).where(
        PracticeProblemProgress.user_id == user.id, PracticeProblemProgress.status == "solved",
    )) or 0
    return CodingAnalyticsResponse(
        attempted=len(problem_ids), solved=solved, total_submissions=len(submissions),
        accepted_submissions=accepted,
        acceptance_rate=round((accepted / len(submissions)) * 100, 2) if submissions else 0,
        by_difficulty=by_difficulty, by_language=by_language, by_topic=by_topic,
    )


@app.get("/api/admin/problems", response_model=list[PracticeProblemResponse])
def admin_list_problems(user: User = Depends(current_user), db: Session = Depends(get_db)) -> list[PracticeProblemResponse]:
    require_admin(user)
    return [practice_response(problem) for problem in db.scalars(select(PracticeProblem).order_by(PracticeProblem.id.desc()))]


@app.post("/api/admin/problems", response_model=PracticeProblemResponse, status_code=201)
def admin_create_problem(
    payload: AdminProblemUpdateRequest,
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
) -> PracticeProblemResponse:
    require_admin(user)
    if db.scalar(select(PracticeProblem).where(PracticeProblem.slug == payload.slug)):
        raise HTTPException(status_code=409, detail="A problem with this slug already exists")
    problem = PracticeProblem(
        title=payload.title, slug=payload.slug, description=payload.description,
        difficulty=payload.difficulty, category=payload.category,
        topic=payload.topic, constraints=payload.constraints,
        examples_json=json.dumps(payload.examples), hints_json=json.dumps(payload.hints),
        editorial=payload.editorial, reference_url=payload.reference_url,
        starter_code=payload.starter_code, is_published=payload.is_published,
    )
    db.add(problem)
    db.commit()
    db.refresh(problem)
    return practice_response(problem)


@app.put("/api/admin/problems/{problem_id}", response_model=PracticeProblemResponse)
def admin_update_problem(
    problem_id: int,
    payload: AdminProblemUpdateRequest,
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
) -> PracticeProblemResponse:
    require_admin(user)
    problem = db.get(PracticeProblem, problem_id)
    if problem is None:
        raise HTTPException(status_code=404, detail="Practice problem not found")
    duplicate = db.scalar(select(PracticeProblem).where(
        PracticeProblem.slug == payload.slug, PracticeProblem.id != problem_id,
    ))
    if duplicate:
        raise HTTPException(status_code=409, detail="A problem with this slug already exists")
    for field in ["title", "slug", "description", "difficulty", "category", "topic", "constraints", "editorial", "reference_url", "starter_code", "is_published"]:
        setattr(problem, field, getattr(payload, field))
    problem.examples_json = json.dumps(payload.examples)
    problem.hints_json = json.dumps(payload.hints)
    db.commit()
    db.refresh(problem)
    return practice_response(problem)


@app.delete("/api/admin/problems/{problem_id}", status_code=204)
def admin_delete_problem(problem_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)) -> None:
    require_admin(user)
    problem = db.get(PracticeProblem, problem_id)
    if problem is None:
        raise HTTPException(status_code=404, detail="Practice problem not found")
    db.delete(problem)
    db.commit()


@app.get("/api/admin/dashboard", response_model=AdminDashboardResponse)
def admin_dashboard(user: User = Depends(current_user), db: Session = Depends(get_db)) -> AdminDashboardResponse:
    require_admin(user)
    problems = list(db.scalars(select(PracticeProblem)))
    submissions = list(db.scalars(select(PracticeSubmission)))
    return AdminDashboardResponse(
        total_problems=len(problems),
        published_problems=sum(problem.is_published for problem in problems),
        draft_problems=sum(not problem.is_published for problem in problems),
        total_submissions=len(submissions),
        accepted_submissions=sum(row.status == "accepted" for row in submissions),
        imports=db.scalar(select(func.count()).select_from(ProblemImportJob)) or 0,
        by_difficulty={key: sum(problem.difficulty == key for problem in problems) for key in ("Easy", "Medium", "Hard")},
        by_category={category: sum(problem.category == category for problem in problems) for category in {problem.category for problem in problems}},
    )


@app.get("/api/admin/problems/import/template")
def admin_import_template(
    file_format: str = Query(default="json", pattern="^(json|csv)$"),
    user: User = Depends(current_user),
) -> Response:
    require_admin(user)
    if file_format == "csv":
        content = "title,slug,description,difficulty,category,topic,constraints,examples,hints,test_cases,starter_code,is_published\n"
        content += 'Example,example-problem,"Describe the task",Easy,Arrays,Arrays,"Input constraints","[]","[]","[]","",true\n'
        return Response(content, media_type="text/csv", headers={"Content-Disposition": "attachment; filename=learn2code-problems.csv"})
    content = json.dumps({"problems": [{
        "title": "Example", "slug": "example-problem", "description": "Describe the task",
        "difficulty": "Easy", "category": "Arrays", "topic": "Arrays",
        "constraints": ["Add constraints"], "examples": [{"input": "1", "output": "1"}],
        "hints": ["Add a hint"], "test_cases": [{"input": "1", "expected_output": "1", "is_hidden": False}],
        "starter_code": {"python": "print(1)"}, "is_published": True,
    }]}, indent=2)
    return Response(content, media_type="application/json", headers={"Content-Disposition": "attachment; filename=learn2code-problems.json"})


@app.get("/api/admin/problems/export")
def admin_export_problems(
    file_format: str = Query(default="json", pattern="^(json|csv)$"),
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
) -> Response:
    require_admin(user)
    problems = list(db.scalars(select(PracticeProblem).order_by(PracticeProblem.id)))
    rows = [{
        "title": problem.title, "slug": problem.slug, "description": problem.description,
        "difficulty": problem.difficulty, "category": problem.category, "topic": problem.topic,
        "constraints": problem.constraints, "examples": json.loads(problem.examples_json or "[]"),
        "hints": json.loads(problem.hints_json or "[]"), "editorial": problem.editorial,
        "reference_url": problem.reference_url, "starter_code": problem.starter_code,
        "is_published": problem.is_published,
        "test_cases": [{
            "input": case.stdin, "expected_output": case.expected_stdout, "is_hidden": case.is_hidden,
        } for case in problem.test_cases],
    } for problem in problems]
    if file_format == "json":
        return Response(json.dumps({"problems": rows}, indent=2), media_type="application/json", headers={"Content-Disposition": "attachment; filename=learn2code-problems.json"})
    output = io.StringIO()
    fieldnames = ["title", "slug", "description", "difficulty", "category", "topic", "constraints", "examples", "hints", "test_cases", "starter_code", "is_published"]
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    for row in rows:
        writer.writerow({field: json.dumps(row[field]) if isinstance(row[field], (list, dict)) else row[field] for field in fieldnames})
    return Response(output.getvalue(), media_type="text/csv", headers={"Content-Disposition": "attachment; filename=learn2code-problems.csv"})


@app.get("/api/admin/problems/{problem_id}/test-cases", response_model=list[AdminTestCaseResponse])
def admin_list_test_cases(problem_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)) -> list[PracticeTestCase]:
    require_admin(user)
    if db.get(PracticeProblem, problem_id) is None:
        raise HTTPException(status_code=404, detail="Practice problem not found")
    return list(db.scalars(select(PracticeTestCase).where(
        PracticeTestCase.problem_id == problem_id,
    ).order_by(PracticeTestCase.order_index)))


@app.put("/api/admin/problems/{problem_id}/test-cases", response_model=list[AdminTestCaseResponse])
def admin_replace_test_cases(
    problem_id: int,
    payload: list[AdminTestCaseRequest],
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
) -> list[PracticeTestCase]:
    require_admin(user)
    if db.get(PracticeProblem, problem_id) is None:
        raise HTTPException(status_code=404, detail="Practice problem not found")
    for case in list(db.scalars(select(PracticeTestCase).where(PracticeTestCase.problem_id == problem_id))):
        db.delete(case)
    db.flush()
    for order_index, case in enumerate(payload):
        db.add(PracticeTestCase(problem_id=problem_id, order_index=order_index, **case.model_dump()))
    db.commit()
    return list(db.scalars(select(PracticeTestCase).where(
        PracticeTestCase.problem_id == problem_id,
    ).order_by(PracticeTestCase.order_index)))


def _parse_problem_import(payload: ProblemImportRequest) -> list[dict[str, object]]:
    if payload.file_format == "json":
        parsed = json.loads(payload.content)
        if isinstance(parsed, dict):
            parsed = parsed.get("problems")
        if not isinstance(parsed, list):
            raise ValueError("JSON must contain a problems array")
        return parsed
    rows = csv.DictReader(io.StringIO(payload.content))
    return [dict(row) for row in rows]


@app.post("/api/admin/problems/import", response_model=ProblemImportResponse, status_code=201)
def admin_import_problems(
    payload: ProblemImportRequest,
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
) -> ProblemImportResponse:
    require_admin(user)
    try:
        rows = _parse_problem_import(payload)
    except (ValueError, json.JSONDecodeError) as error:
        raise HTTPException(status_code=422, detail=f"Invalid {payload.file_format.upper()} import: {error}") from error
    errors: list[str] = []
    imported = skipped = 0
    job = ProblemImportJob(admin_id=user.id, file_format=payload.file_format, mode=payload.mode)
    db.add(job)
    db.flush()
    for index, raw in enumerate(rows, 1):
        if not isinstance(raw, dict):
            errors.append(f"Row {index}: expected an object")
            continue
        slug = str(raw.get("slug", "")).strip()
        required = ["title", "slug", "description", "difficulty", "category"]
        missing = [field for field in required if not str(raw.get(field, "")).strip()]
        if missing:
            errors.append(f"Row {index}: missing {', '.join(missing)}")
            continue
        if str(raw["difficulty"]) not in {"Easy", "Medium", "Hard"}:
            errors.append(f"Row {index}: difficulty must be Easy, Medium, or Hard")
            continue
        existing = db.scalar(select(PracticeProblem).where(PracticeProblem.slug == slug))
        if existing and payload.mode == "skip":
            skipped += 1
            continue
        if existing and payload.mode == "fail":
            errors.append(f"Row {index}: duplicate slug '{slug}'")
            continue
        def list_value(name: str) -> list:
            value = raw.get(name, [])
            if isinstance(value, str):
                try:
                    value = json.loads(value)
                except json.JSONDecodeError:
                    return [value]
            return value if isinstance(value, list) else []
        if existing:
            problem = existing
        else:
            problem = PracticeProblem(slug=slug)
            db.add(problem)
        problem.title = str(raw["title"])
        problem.description = str(raw["description"])
        problem.difficulty = str(raw["difficulty"])
        problem.category = str(raw["category"])
        problem.topic = str(raw.get("topic") or "") or None
        problem.constraints = str(raw.get("constraints") or "") or None
        problem.examples_json = json.dumps(list_value("examples"))
        problem.hints_json = json.dumps(list_value("hints"))
        problem.editorial = str(raw.get("editorial") or "") or None
        problem.reference_url = str(raw.get("reference_url") or "") or None
        starter_code = raw.get("starter_code")
        problem.starter_code = json.dumps(starter_code) if isinstance(starter_code, dict) else (str(starter_code) if starter_code else None)
        problem.is_published = str(raw.get("is_published", "true")).lower() not in {"false", "0", "draft"}
        db.flush()
        test_cases = list_value("test_cases")
        if existing:
            for test_case in list(db.scalars(select(PracticeTestCase).where(PracticeTestCase.problem_id == problem.id))):
                db.delete(test_case)
        for order, test_case in enumerate(test_cases):
            if not isinstance(test_case, dict) or "expected_output" not in test_case:
                errors.append(f"Row {index}: invalid test case at position {order + 1}")
                continue
            db.add(PracticeTestCase(
                problem_id=problem.id, stdin=str(test_case.get("input", "")),
                expected_stdout=str(test_case["expected_output"]),
                is_hidden=bool(test_case.get("is_hidden", False)), order_index=order,
            ))
        imported += 1
    if errors and payload.mode == "fail":
        db.rollback()
        raise HTTPException(status_code=422, detail={"message": "Import validation failed", "errors": errors})
    job.imported_count = imported
    job.skipped_count = skipped
    job.error_count = len(errors)
    job.errors_json = json.dumps(errors)
    db.commit()
    db.refresh(job)
    return ProblemImportResponse(
        id=job.id, status="completed_with_errors" if errors else "completed",
        imported_count=imported, skipped_count=skipped, error_count=len(errors), errors=errors,
    )


@app.get("/api/admin/problems/import/history", response_model=list[ProblemImportResponse])
def admin_import_history(user: User = Depends(current_user), db: Session = Depends(get_db)) -> list[ProblemImportResponse]:
    require_admin(user)
    jobs = db.scalars(select(ProblemImportJob).where(
        ProblemImportJob.admin_id == user.id,
    ).order_by(ProblemImportJob.created_at.desc()).limit(50))
    return [
        ProblemImportResponse(
            id=job.id, status=job.status, imported_count=job.imported_count,
            skipped_count=job.skipped_count, error_count=job.error_count,
            errors=json.loads(job.errors_json or "[]"),
        )
        for job in jobs
    ]


@app.patch("/api/users/me/profile", response_model=UserResponse)
def update_profile(
    payload: ProfileUpdateRequest,
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
) -> UserResponse:
    user.full_name = payload.full_name.strip()
    profile = user.profile or UserProfile(user_id=user.id)
    profile.daily_minutes = payload.daily_minutes
    db.add(profile)
    db.commit()
    db.refresh(user)
    return profile_response(user)


@app.get("/api/users/me/bookmarks", response_model=list[BookmarkResponse])
def list_bookmarks(user: User = Depends(current_user), db: Session = Depends(get_db)) -> list[UserBookmark]:
    return list(db.scalars(select(UserBookmark).where(UserBookmark.user_id == user.id).order_by(UserBookmark.created_at.desc())))


@app.post("/api/users/me/bookmarks", response_model=BookmarkResponse, status_code=201)
def add_bookmark(
    payload: BookmarkRequest,
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
) -> UserBookmark:
    bookmark = db.scalar(select(UserBookmark).where(
        UserBookmark.user_id == user.id, UserBookmark.target_type == payload.target_type,
        UserBookmark.target_id == payload.target_id,
    ))
    if bookmark is None:
        bookmark = UserBookmark(user_id=user.id, target_type=payload.target_type, target_id=payload.target_id)
        db.add(bookmark)
        db.commit()
        db.refresh(bookmark)
    return bookmark


@app.delete("/api/users/me/bookmarks/{target_type}/{target_id}", status_code=204)
def delete_bookmark(
    target_type: str,
    target_id: int,
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
) -> None:
    bookmark = db.scalar(select(UserBookmark).where(
        UserBookmark.user_id == user.id, UserBookmark.target_type == target_type,
        UserBookmark.target_id == target_id,
    ))
    if bookmark is not None:
        db.delete(bookmark)
        db.commit()


@app.get("/api/users/me/history", response_model=list[HistoryResponse])
def list_history(user: User = Depends(current_user), db: Session = Depends(get_db)) -> list[UserHistory]:
    rows = db.scalars(select(UserHistory).where(UserHistory.user_id == user.id).order_by(UserHistory.viewed_at.desc()).limit(50))
    return [
        HistoryResponse(target_type=row.target_type, target_id=row.target_id, viewed_at=row.viewed_at.isoformat())
        for row in rows
    ]
