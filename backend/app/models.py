from datetime import datetime, timezone
from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db import Base


def utcnow():
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    full_name: Mapped[str] = mapped_column(String(160))
    role: Mapped[str] = mapped_column(String(20), default="student")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    profile: Mapped["StudentProfile"] = relationship(back_populates="user", cascade="all, delete-orphan", uselist=False)


class StudentProfile(Base):
    __tablename__ = "student_profiles"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), unique=True)
    target_role_id: Mapped[int | None] = mapped_column(ForeignKey("career_roles.id"), nullable=True)
    institution: Mapped[str | None] = mapped_column(String(200), nullable=True)
    user: Mapped[User] = relationship(back_populates="profile")


class Skill(Base):
    __tablename__ = "skills"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    category: Mapped[str] = mapped_column(String(80))
    description: Mapped[str] = mapped_column(Text, default="")


class CareerRole(Base):
    __tablename__ = "career_roles"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    description: Mapped[str] = mapped_column(Text, default="")


class RoleSkillRequirement(Base):
    __tablename__ = "role_skill_requirements"
    __table_args__ = (UniqueConstraint("role_id", "skill_id"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    role_id: Mapped[int] = mapped_column(ForeignKey("career_roles.id", ondelete="CASCADE"), index=True)
    skill_id: Mapped[int] = mapped_column(ForeignKey("skills.id", ondelete="CASCADE"), index=True)
    weight: Mapped[float] = mapped_column(Float, default=1.0)
    minimum_level: Mapped[int] = mapped_column(Integer, default=1)
    recommended_level: Mapped[int] = mapped_column(Integer, default=3)
    industry_relevance: Mapped[float] = mapped_column(Float, default=0.7)


class StudentAssessment(Base):
    __tablename__ = "student_assessments"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    assessed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    source: Mapped[str] = mapped_column(String(30), default="self_assessment")
    ratings: Mapped[list["StudentSkillRating"]] = relationship(back_populates="assessment", cascade="all, delete-orphan")


class StudentSkillRating(Base):
    __tablename__ = "student_skill_ratings"
    __table_args__ = (UniqueConstraint("assessment_id", "skill_id"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    assessment_id: Mapped[int] = mapped_column(ForeignKey("student_assessments.id", ondelete="CASCADE"), index=True)
    skill_id: Mapped[int] = mapped_column(ForeignKey("skills.id", ondelete="CASCADE"), index=True)
    level: Mapped[int] = mapped_column(Integer)
    assessment: Mapped[StudentAssessment] = relationship(back_populates="ratings")


class LearningResource(Base):
    __tablename__ = "learning_resources"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    description: Mapped[str] = mapped_column(Text)
    skills_text: Mapped[str] = mapped_column(Text, default="")
    difficulty: Mapped[str] = mapped_column(String(20), default="beginner")
    resource_type: Mapped[str] = mapped_column(String(30), default="course")
    duration_hours: Mapped[int] = mapped_column(Integer, default=4)
    url: Mapped[str] = mapped_column(String(500), default="")


class Project(Base):
    __tablename__ = "projects"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    skill_id: Mapped[int | None] = mapped_column(ForeignKey("skills.id"), nullable=True, index=True)
    description: Mapped[str] = mapped_column(Text)
    estimated_hours: Mapped[int] = mapped_column(Integer, default=4)
    difficulty: Mapped[str] = mapped_column(String(20), default="beginner")


class Recommendation(Base):
    __tablename__ = "recommendations"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    role_id: Mapped[int] = mapped_column(ForeignKey("career_roles.id"))
    resource_id: Mapped[int] = mapped_column(ForeignKey("learning_resources.id"))
    score: Mapped[float] = mapped_column(Float)
    explanation: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class LearningRoadmap(Base):
    __tablename__ = "learning_roadmaps"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    role_id: Mapped[int] = mapped_column(ForeignKey("career_roles.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    items: Mapped[list["RoadmapItem"]] = relationship(back_populates="roadmap", cascade="all, delete-orphan")


class RoadmapItem(Base):
    __tablename__ = "roadmap_items"
    id: Mapped[int] = mapped_column(primary_key=True)
    roadmap_id: Mapped[int] = mapped_column(ForeignKey("learning_roadmaps.id", ondelete="CASCADE"), index=True)
    resource_id: Mapped[int] = mapped_column(ForeignKey("learning_resources.id"))
    skill_id: Mapped[int] = mapped_column(ForeignKey("skills.id"))
    sequence: Mapped[int] = mapped_column(Integer)
    priority: Mapped[str] = mapped_column(String(20))
    target_level: Mapped[int] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(String(20), default="not_started")
    assignment: Mapped[str] = mapped_column(Text, default="Build a small project demonstrating this competency.")
    roadmap: Mapped[LearningRoadmap] = relationship(back_populates="items")


class LearningProgress(Base):
    __tablename__ = "learning_progress"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    roadmap_item_id: Mapped[int] = mapped_column(ForeignKey("roadmap_items.id", ondelete="CASCADE"), index=True)
    progress_percent: Mapped[int] = mapped_column(Integer, default=0)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)


class ModelMetadata(Base):
    __tablename__ = "model_metadata"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120))
    version: Mapped[str] = mapped_column(String(40))
    approach: Mapped[str] = mapped_column(Text)
    trained: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
