"""Course import endpoints.

POST /api/import/excel  — Upload .xlsx/.xls, parse via openpyxl
POST /api/import/text   — Send free text to GPT-4o-mini for parsing
POST /api/import/image  — Upload image, mock recognition (file→JSON lookup)

All return unified: {success, method, courses, stats}
"""

import time
import tempfile
import os
from pathlib import Path

from fastapi import APIRouter, File, UploadFile, HTTPException
from pydantic import BaseModel, Field

from services.excel_parser import parse_excel
from services.llm_parser import parse_course_text
from services.image_parser import get_image_parser

router = APIRouter(prefix="/api/import", tags=["import"])


# ── Shared Response Model ───────────────────────────────────────


class ImportStats(BaseModel):
    course_count: int
    processing_time_ms: float
    method: str


class ImportResponse(BaseModel):
    success: bool
    method: str
    courses: list[dict]
    stats: ImportStats


class ImportError(BaseModel):
    success: bool = False
    error: str
    message: str


# ── Helpers ─────────────────────────────────────────────────────


def _build_response(
    method: str, courses: list[dict], elapsed_ms: float
) -> dict:
    return {
        "success": True,
        "method": method,
        "courses": courses,
        "stats": {
            "course_count": len(courses),
            "processing_time_ms": round(elapsed_ms, 1),
            "method": method,
        },
    }


# ── Excel Import ────────────────────────────────────────────────


@router.post("/excel")
async def import_excel(file: UploadFile = File(...)) -> dict:
    """Parse an uploaded Excel course schedule file."""
    if not file.filename:
        raise HTTPException(400, "未提供文件名")

    ext = Path(file.filename).suffix.lower()
    if ext not in (".xlsx", ".xls"):
        raise HTTPException(400, f"不支持的文件格式: {ext}，请上传 .xlsx 或 .xls")

    content = await file.read()
    if not content:
        raise HTTPException(400, "上传文件为空")

    start = time.perf_counter()
    try:
        courses = parse_excel(content, file.filename)
    except Exception as e:
        raise HTTPException(500, f"Excel 解析失败: {e}")
    elapsed = (time.perf_counter() - start) * 1000

    return _build_response("excel", courses, elapsed)


# ── AI Text Import ──────────────────────────────────────────────


class TextImportRequest(BaseModel):
    text: str = Field(..., min_length=1, description="Free-form course text")


@router.post("/text")
async def import_text(req: TextImportRequest) -> dict:
    """Parse free-form Chinese course text via GPT-4o-mini."""
    start = time.perf_counter()
    try:
        courses = parse_course_text(req.text)
    except ValueError as e:
        raise HTTPException(422, str(e))
    except Exception as e:
        raise HTTPException(500, f"AI 解析失败: {e}")
    elapsed = (time.perf_counter() - start) * 1000

    return _build_response("text", courses, elapsed)


# ── Image Import ────────────────────────────────────────────────


@router.post("/image")
async def import_image(file: UploadFile = File(...)) -> dict:
    """Recognize courses from an uploaded schedule screenshot (mock)."""
    if not file.filename:
        raise HTTPException(400, "未提供文件名")

    ext = Path(file.filename).suffix.lower()
    if ext not in (".png", ".jpg", ".jpeg"):
        raise HTTPException(400, f"不支持的文件格式: {ext}，请上传 png/jpg/jpeg")

    content = await file.read()
    if not content:
        raise HTTPException(400, "上传文件为空")

    # Save to temp file for parser
    suffix = ext if ext.startswith(".") else f".{ext}"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(content)
        tmp_path = tmp.name

    start = time.perf_counter()
    try:
        parser = get_image_parser()
        courses = parser.parse(tmp_path)
    except Exception as e:
        os.unlink(tmp_path)
        raise HTTPException(500, f"图片识别失败: {e}")
    elapsed = (time.perf_counter() - start) * 1000

    # Cleanup
    os.unlink(tmp_path)

    return _build_response("image", courses, elapsed)
