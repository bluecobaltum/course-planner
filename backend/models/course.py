"""Course-related data models.

Defines the fundamental building blocks for course data:
schedule slots, teachers, locations, and the full course/section record.
"""

from typing import Literal, Optional

from pydantic import BaseModel, Field, field_validator


class ScheduleSlot(BaseModel):
    """A single time-range on one day of the week.

    Uses period numbers (节次), not clock times.
    Period system: 1-14节 (上午=1-5, 下午=6-10, 晚上=11-14)
    早八 = 第1-2节 (the earliest morning slot)
    """

    day: int = Field(..., ge=1, le=5, description="1=Monday .. 5=Friday")
    start: int = Field(..., ge=1, le=14, description="Start period (1-14)")
    end: int = Field(..., ge=1, le=14, description="End period, inclusive (1-14)")

    @field_validator("end")
    @classmethod
    def end_must_be_gte_start(cls, v: int, info) -> int:
        """Validate that end period is not before start period."""
        if "start" in info.data and v < info.data["start"]:
            raise ValueError(
                f"end={v} must be >= start={info.data['start']}"
            )
        return v


class Teacher(BaseModel):
    """Teacher information with student evaluation rating."""

    name: str = Field(..., min_length=1, description="Teacher's full name")
    rating: float = Field(
        ..., ge=1.0, le=5.0, description="Student evaluation score (1.0-5.0)"
    )


class Location(BaseModel):
    """Classroom location information."""

    building: str = Field(..., min_length=1, description="Building name, e.g. 汇文楼")
    floor: int = Field(..., ge=0, description="Floor number (0 = ground/virtual)")
    room: str = Field(..., min_length=1, description="Room number (as string)")


class Course(BaseModel):
    """A complete course section / teaching class record.

    Each section represents one specific offering of a course:
    a particular teacher, at particular times, in a particular room.
    Multiple sections of the same course share the same credit_transfer_group
    and are mutually exclusive (you only take one).
    """

    section_id: str = Field(
        ..., min_length=1, description="Unique section ID, e.g. MATH101-01"
    )
    course_code: str = Field(..., min_length=1, description="Course code, e.g. MATH101")
    course_name: str = Field(..., min_length=1, description="Course display name")
    credit_transfer_group: str = Field(
        ...,
        min_length=1,
        description=(
            "Credit transfer group ID. All sections in the same group are "
            "mutually exclusive — you can only select one."
        ),
    )
    credits: int = Field(..., ge=1, le=10, description="Credit hours for this course")
    teacher: Optional[Teacher] = Field(
        default=None, description="Teacher info (None if not yet assigned)"
    )
    schedule: list[ScheduleSlot] = Field(
        ..., min_length=0, description="Weekly meeting times (empty for async online)"
    )
    location: Optional[Location] = Field(
        default=None, description="Classroom location (None if not yet assigned)"
    )
    course_type: Literal["major", "easy"] = Field(
        ..., description="'major' = required course, 'easy' = optional/elective"
    )
    delivery_mode: Literal["线下传统", "线上网课", "线上线下混合"] = Field(
        ...,
        description="Teaching mode: traditional offline / online / blended",
    )
    semester: str = Field(default="2025-2026-2", description="Academic semester ID")
