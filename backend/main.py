"""
AI 智能选课助手 — FastAPI Application Entry Point.

Start with:
    uvicorn main:app --reload

API Endpoints:
    POST /api/generate_schedule  — Generate top-3 schedule plans
    GET  /api/strategies          — Get course selection strategy cards
    GET  /api/health              — Health check
"""

from dotenv import load_dotenv
load_dotenv()  # Load .env file before anything else

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from routes.schedule import router as schedule_router
from routes.strategies import router as strategies_router
from routes.courses import router as courses_router
from routes.import_router import router as import_router
from models.response import ErrorResponse

# ── App Initialization ───────────────────────────────────────

app = FastAPI(
    title="AI 智能选课助手",
    description="基于多维度评分的智能课表生成系统 — Hackathon MVP",
    version="2.0.0",
)

# ── CORS (allow all origins for hackathon development) ──────

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ──────────────────────────────────────────────────

app.include_router(schedule_router)
app.include_router(strategies_router)
app.include_router(courses_router)
app.include_router(import_router)


# ── Health Check ─────────────────────────────────────────────


@app.get("/api/health", tags=["health"])
async def health_check():
    """Simple health check — verifies the server is running."""
    return {"status": "ok", "service": "AI 智能选课助手"}


# ── Exception Handlers ───────────────────────────────────────


@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError) -> JSONResponse:
    """Handle ValueErrors (e.g., invalid scenario) with a 422 response."""
    return JSONResponse(
        status_code=422,
        content=ErrorResponse(
            error="VALIDATION_ERROR",
            detail=str(exc),
            message="输入参数有误，请检查后重试",
        ).model_dump(),
    )


@app.exception_handler(FileNotFoundError)
async def file_not_found_handler(
    request: Request, exc: FileNotFoundError
) -> JSONResponse:
    """Handle missing data file errors with a 500 response."""
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error="DATA_LOAD_ERROR",
            detail=str(exc),
            message="服务器数据文件缺失，请联系管理员",
        ).model_dump(),
    )


@app.exception_handler(Exception)
async def general_error_handler(request: Request, exc: Exception) -> JSONResponse:
    """Catch-all handler for unexpected errors."""
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error="INTERNAL_ERROR",
            detail=str(exc),
            message="服务器内部错误，请稍后重试",
        ).model_dump(),
    )


# ── Entry Point ──────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
