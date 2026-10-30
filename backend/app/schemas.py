from pydantic import BaseModel, ConfigDict, EmailStr, Field


class RegisterIn(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    full_name: str = Field(min_length=1, max_length=160)


class LoginIn(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: int
    email: str
    full_name: str
    role: str
    model_config = ConfigDict(from_attributes=True)


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"


class RatingIn(BaseModel):
    skill_id: int
    level: int = Field(ge=0, le=5)


class AssessmentIn(BaseModel):
    ratings: list[RatingIn] = Field(min_length=1)


class RoleIn(BaseModel):
    role_id: int
