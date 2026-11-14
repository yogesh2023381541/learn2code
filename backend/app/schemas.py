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
    token_type: str = "bearer"


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    full_name: str
    email: EmailStr
    role: str


class OnboardingRequest(BaseModel):
    experience_level: str = Field(pattern="^(beginner|intermediate|advanced)$")
    learning_goal: str = Field(min_length=2, max_length=100)
    preferred_language: str = Field(min_length=1, max_length=40)
    daily_minutes: int = Field(ge=5, le=480)
    subjects: list[str] = Field(min_length=1, max_length=20)


class SubjectResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    slug: str
    category: str
    description: str
    difficulty: str
    estimated_minutes: int
