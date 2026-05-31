"""Course data CRUD endpoints.

GET    /api/courses              — List all courses
POST   /api/courses              — Add a new course
PUT    /api/courses/{section_id} — Update a course
DELETE /api/courses/{section_id} — Delete a course
"""

import json
from pathlib import Path

from fastapi import APIRouter, HTTPException

from models.course import Course
from services.course_classifier import apply_classification

router = APIRouter(prefix="/api", tags=["courses"])

DATA_FILE = Path(__file__).parent.parent / "data" / "courses.json"


def _read_courses() -> list[dict]:
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def _write_courses(courses: list[dict]) -> None:
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(courses, f, ensure_ascii=False, indent=2)


@router.get("/courses")
async def list_courses() -> list[dict]:
    return _read_courses()


@router.post("/courses", status_code=201)
async def create_course(course: Course) -> dict:
    courses = _read_courses()

    # Check duplicate section_id
    if any(c["section_id"] == course.section_id for c in courses):
        raise HTTPException(
            status_code=409,
            detail=f"班号 {course.section_id} 已存在",
        )

    course_dict = apply_classification(course.model_dump())
    courses.append(course_dict)
    _write_courses(courses)
    return course_dict


@router.put("/courses/{section_id}")
async def update_course(section_id: str, course: Course) -> dict:
    courses = _read_courses()

    for i, c in enumerate(courses):
        if c["section_id"] == section_id:
            course_dict = apply_classification(course.model_dump())
            courses[i] = course_dict
            _write_courses(courses)
            return course_dict

    raise HTTPException(status_code=404, detail=f"班号 {section_id} 不存在")


@router.delete("/courses/{section_id}", status_code=204)
async def delete_course(section_id: str):
    courses = _read_courses()
    new_courses = [c for c in courses if c["section_id"] != section_id]

    if len(new_courses) == len(courses):
        raise HTTPException(status_code=404, detail=f"班号 {section_id} 不存在")

    _write_courses(new_courses)
