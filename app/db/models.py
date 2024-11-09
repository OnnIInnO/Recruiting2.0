from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, DateTime, ForeignKey, JSON, Float
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String)
    created_at = Column(DateTime, default=datetime.now())

    # Assessment profiles
    wellbeing_profile = Column(JSON, nullable=True)
    skills_profile = Column(JSON, nullable=True)
    values_profile = Column(JSON, nullable=True)

    # Relationship
    applications = relationship("JobApplication", back_populates="user")


class Company(Base):
    __tablename__ = "companies"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    description = Column(String)
    industry = Column(String)

    # Company profiles
    wellbeing_profile = Column(JSON, nullable=True)
    values_profile = Column(JSON, nullable=True)

    # Relationships
    jobs = relationship("JobPosting", back_populates="company")


class JobPosting(Base):
    __tablename__ = "job_postings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"))
    title = Column(String, nullable=False)
    description = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Job requirements profiles
    skills_requirements = Column(JSON, nullable=True)
    wellbeing_preferences = Column(JSON, nullable=True)
    values_alignment = Column(JSON, nullable=True)

    # Relationships
    company = relationship("Company", back_populates="jobs")
    applications = relationship("JobApplication", back_populates="job")


class JobApplication(Base):
    __tablename__ = "job_applications"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    job_id = Column(UUID(as_uuid=True), ForeignKey("job_postings.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    status = Column(String, default="pending")

    # Match scores
    skills_match = Column(Float)
    wellbeing_match = Column(Float)
    values_match = Column(Float)
    overall_match = Column(Float)

    # Relationships
    user = relationship("User", back_populates="applications")
    job = relationship("JobPosting", back_populates="applications")
