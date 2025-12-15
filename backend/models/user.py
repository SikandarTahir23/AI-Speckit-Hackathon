"""
User Model (Hackathon Bonus Feature 1)

Stores user authentication and profile information.
Uses FastAPI-Users with SQLAlchemy (not SQLModel due to compatibility).
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum as SQLAEnum
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTable
from datetime import datetime
import enum


class SoftwareBackground(str, enum.Enum):
    """Software development experience levels"""
    BEGINNER = "Beginner"
    INTERMEDIATE = "Intermediate"
    ADVANCED = "Advanced"


class HardwareBackground(str, enum.Enum):
    """Hardware/robotics experience levels"""
    NONE = "None"
    BASIC = "Basic"
    HANDS_ON = "Hands-on"


# Declarative base for User table (shared with FastAPI-Users)
class Base(DeclarativeBase):
    pass


class User(SQLAlchemyBaseUserTable[int], Base):
    """
    User table for authentication and profiling.

    Extends FastAPI-Users base table with custom profile fields
    for hackathon bonus feature (authentication + profiling).
    """

    __tablename__ = "users"

    # Primary key (explicitly defined to ensure proper inheritance)
    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    # Other inherited fields from SQLAlchemyBaseUserTable:
    # - email: Mapped[str] (unique, indexed)
    # - hashed_password: Mapped[str]
    # - is_active: Mapped[bool]
    # - is_superuser: Mapped[bool]
    # - is_verified: Mapped[bool]

    # Profile fields (FR-002, FR-003 from spec.md)
    software_background = Column(
        SQLAEnum(SoftwareBackground),
        nullable=False,
        doc="User's software development experience level"
    )
    hardware_background = Column(
        SQLAEnum(HardwareBackground),
        nullable=False,
        doc="User's hardware/robotics experience level"
    )
    python_familiar = Column(
        Boolean,
        nullable=False,
        default=False,
        doc="User familiarity with Python programming"
    )
    ros_familiar = Column(
        Boolean,
        nullable=False,
        default=False,
        doc="User familiarity with ROS (Robot Operating System)"
    )
    aiml_familiar = Column(
        Boolean,
        nullable=False,
        default=False,
        doc="User familiarity with AI/ML concepts"
    )

    # Timestamps
    created_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        doc="Account creation timestamp (UTC)"
    )
    updated_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        doc="Last profile update timestamp (UTC)"
    )


# Validation rules (enforced at API layer):
# - email: Valid RFC 5322 format, unique (enforced by database constraint)
# - password: Min 8 chars, 1 uppercase, 1 lowercase, 1 digit (FR-006)
# - software_background: Must be one of ["Beginner", "Intermediate", "Advanced"]
# - hardware_background: Must be one of ["None", "Basic", "Hands-on"]
# - Profile fields are required during registration (FR-003)
