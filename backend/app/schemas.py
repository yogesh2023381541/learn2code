from pydantic import BaseModel, ConfigDict, EmailStr, Field


class SignupRequest(BaseModel):
    full_name: str = Field(min_length=2, max_length=120)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class ProfileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    experience_level: str | None = None
    learning_goal: str | None = None
    preferred_language: str | None = None
    daily_minutes: int | None = None
    subjects: list[str] = []
    learning_hours: float = 0
    topics_completed: int = 0
    problems_solved: int = 0
    current_streak: int = 0


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    full_name: str
    email: EmailStr
    role: str
    profile: ProfileResponse | None = None


class OnboardingRequest(BaseModel):
    experience_level: str = Field(pattern="^(beginner|intermediate|advanced)$")
    learning_goal: str = Field(min_length=2, max_length=100)
    preferred_language: str = Field(min_length=1, max_length=40)
    daily_minutes: int = Field(ge=5, le=480)
    subjects: list[str] = Field(min_length=1, max_length=20)


class ActivityRequest(BaseModel):
    minutes: int = Field(ge=1, le=1440)
    activity_type: str = Field(pattern="^(lesson|practice|quiz)$")


class SubjectResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    slug: str
    category: str
    description: str
    difficulty: str
    estimated_minutes: int
    progress: int = 0


class AuthResponse(TokenResponse):
    user: UserResponse


class RefreshRequest(BaseModel):
    refresh_token: str = Field(min_length=1)


class DashboardResponse(BaseModel):
    learning_hours: float
    topics_completed: int
    problems_solved: int
    current_streak: int
    overall_progress: int
    recommended_subjects: list[SubjectResponse]
    weekly_activity: list[int]
    daily_goal_minutes: int
    today_minutes: int


class LessonResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    subject_id: int
    title: str
    slug: str
    summary: str
    content: str
    code_example: str | None = None
    video_url: str | None = None
    order_index: int
    estimated_minutes: int
    completed: bool = False


class PracticeProblemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    slug: str
    description: str
    difficulty: str
    category: str
    acceptance_rate: float
    solved: bool = False
    topic: str | None = None
    pattern: str | None = None
    constraints: str | None = None
    examples: list[dict[str, str]] = []
    hints: list[str] = []
    editorial: str | None = None
    reference_url: str | None = None
    starter_code: str | None = None


class SubmissionRequest(BaseModel):
    language: str = Field(min_length=1, max_length=40)
    code: str = Field(min_length=1, max_length=100_000)


class CodeRunRequest(SubmissionRequest):
    stdin: str = Field(default="", max_length=20_000)


class CodeRunResponse(BaseModel):
    status: str
    stdout: str
    stderr: str
    duration_ms: int


class SubmissionResponse(BaseModel):
    id: int
    status: str
    language: str


class ProblemProgressResponse(BaseModel):
    problem_id: int
    status: str
    attempts: int
    bookmarked: bool
    next_revision_at: str | None = None


class ProblemProgressRequest(BaseModel):
    status: str = Field(pattern="^(not_started|attempted|solved|revision)$")
    bookmarked: bool | None = None


class BookmarkRequest(BaseModel):
    target_type: str = Field(pattern="^(lesson|problem|subject)$")
    target_id: int = Field(gt=0)


class BookmarkResponse(BookmarkRequest):
    id: int


class HistoryResponse(BaseModel):
    target_type: str
    target_id: int
    viewed_at: str


class ProfileUpdateRequest(BaseModel):
    full_name: str = Field(min_length=2, max_length=120)
    daily_minutes: int = Field(ge=5, le=480)


class AIConversationCreateRequest(BaseModel):
    title: str = Field(default="New conversation", min_length=1, max_length=160)
    teaching_mode: str = Field(default="beginner", pattern="^(beginner|detailed|interview|practical|revision)$")


class AIMessageRequest(BaseModel):
    content: str = Field(min_length=1, max_length=20_000)
    context: dict[str, str] = Field(default_factory=dict)


class AIMessageResponse(BaseModel):
    id: int
    role: str
    content: str
    created_at: str


class AIConversationResponse(BaseModel):
    id: int
    title: str
    teaching_mode: str
    created_at: str
    updated_at: str
    messages: list[AIMessageResponse] = []


class AIFeedbackRequest(BaseModel):
    rating: str = Field(pattern="^(helpful|not_helpful)$")
    comment: str | None = Field(default=None, max_length=2_000)


class CodeAssistantRequest(BaseModel):
    task: str = Field(min_length=1, max_length=100)
    code: str = Field(min_length=1, max_length=100_000)
    language: str = Field(min_length=1, max_length=40)
    error_message: str | None = Field(default=None, max_length=10_000)


class RecommendationResponse(BaseModel):
    id: int
    title: str
    reason: str
    target_type: str
    target_id: int
    evidence: dict[str, int | float | str]


class RoadmapRequest(BaseModel):
    goal: str = Field(min_length=2, max_length=180)


class RoadmapNodeResponse(BaseModel):
    id: int
    title: str
    subject_id: int
    lesson_id: int | None
    node_type: str
    order_index: int
    estimated_minutes: int
    prerequisite_ids: list[int]


class RoadmapResponse(BaseModel):
    id: int
    goal: str
    experience_level: str
    nodes: list[RoadmapNodeResponse]


class QuizGenerateRequest(BaseModel):
    subject_id: int | None = None
    difficulty: str = Field(default="beginner", pattern="^(beginner|intermediate|advanced)$")
    question_count: int = Field(default=5, ge=1, le=20)


class QuizQuestionResponse(BaseModel):
    id: int
    prompt: str
    options: list[str]
    explanation: str


class QuizResponse(BaseModel):
    id: int
    title: str
    difficulty: str
    questions: list[QuizQuestionResponse]


class QuizAttemptRequest(BaseModel):
    answers: dict[str, str]


class QuizAttemptResponse(BaseModel):
    id: int
    score: int
    total: int


class RevisionResponse(BaseModel):
    id: int
    topic: str
    due_at: str
    interval_days: int


class FlashcardResponse(BaseModel):
    id: int
    topic: str
    front: str
    back: str


class AdminDraftRequest(BaseModel):
    content_type: str = Field(pattern="^(lesson|quiz|example|flashcard|practice)$")
    title: str = Field(min_length=2, max_length=180)
    body: dict[str, str | list[str]]


class AdminDraftResponse(BaseModel):
    id: int
    content_type: str
    title: str
    status: str
    body: dict[str, str | list[str]]
