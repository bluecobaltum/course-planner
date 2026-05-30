"""
Image-based course table parser — provider architecture.

Current: MockImageParser (file → JSON lookup)
Reserved: QwenVisionParser, DoubaoVisionParser, GLM4VParser (future)
"""

import json
import os
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

# ── Configuration ────────────────────────────────────────────────

IMAGE_PROVIDER = os.environ.get("IMAGE_PROVIDER", "mock")

MOCK_RESULTS_DIR = Path(__file__).parent.parent / "mock_results"

# Map known filenames to mock result files
MOCK_FILE_MAP: dict[str, str] = {
    "schedule_1": "schedule_1.json",
    "schedule_2": "schedule_2.json",
    "schedule_3": "schedule_3.json",
}


# ── Abstract Interface ───────────────────────────────────────────


class BaseImageParser(ABC):
    """Abstract interface for image-based course parsing.

    Future providers (QwenVision, DoubaoVision, GLM4V) implement this.
    """

    @abstractmethod
    def parse(self, image_path: str) -> list[dict[str, Any]]:
        """Parse a course schedule image into Course-compatible dicts.

        Args:
            image_path: Path to the uploaded image file.

        Returns:
            List of course dicts matching the Course model shape.
        """
        ...

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Human-readable provider name for logging/display."""
        ...


# ── Mock Implementation ──────────────────────────────────────────


class MockImageParser(BaseImageParser):
    """Mock parser: maps uploaded filename to pre-canned JSON results.

    Used during hackathon development. Replaced by real vision models
    post-demo by changing IMAGE_PROVIDER config.
    """

    @property
    def provider_name(self) -> str:
        return "MockImageParser"

    def parse(self, image_path: str) -> list[dict[str, Any]]:
        """Look up mock result JSON by uploaded filename.

        Strategy: extract stem from filename (without extension),
        match against MOCK_FILE_MAP. If no match, use the first
        available mock file as default.
        """
        filename = Path(image_path).stem

        # Exact match first
        result_file = MOCK_FILE_MAP.get(filename)

        if not result_file:
            # Fuzzy: check if filename contains any known key
            for key, val in MOCK_FILE_MAP.items():
                if key in filename or filename in key:
                    result_file = val
                    break

        if not result_file:
            # Fallback: use first available mock file
            available = list(MOCK_RESULTS_DIR.glob("*.json"))
            if available:
                result_file = available[0].name
            else:
                return []

        result_path = MOCK_RESULTS_DIR / result_file
        if not result_path.exists():
            return []

        with open(result_path, "r", encoding="utf-8") as f:
            return json.load(f)


# ── Future Providers (Stubs) ─────────────────────────────────────


class QwenVisionParser(BaseImageParser):
    """Real Qwen2.5-VL parser via OpenAI-compatible Vision API.

    Works with any OpenAI-compatible provider:
      - AIPING:    base_url=https://aiping.cn/api/v1
      - DashScope: base_url=https://dashscope.aliyuncs.com/compatible-mode/v1
      - Local:     any vLLM/ollama OpenAI-compatible endpoint

    Flow:
        Image → Qwen2.5-VL → OCR + table understanding
        → Structured course JSON → _normalize_course() validation → Preview page

    Requires:
      - OPENAI_API_KEY   (your provider's API key)
      - OPENAI_BASE_URL  (optional, defaults to OpenAI)
    """

    MODEL = os.environ.get("IMAGE_VISION_MODEL", "Qwen2.5-VL-72B-Instruct")

    SYSTEM_PROMPT = (
        "你是大学课表解析器。识别图片中的所有课程，输出严格 JSON 数组。\n\n"
        "每门课格式：\n"
        '{"section_id":"课程代码-01","course_code":"MATH101","course_name":"高等数学",'
        '"credit_transfer_group":"MATH101","credits":4,\n'
        '"teacher":{"name":"王教授","rating":4.5},\n'
        '"schedule":[{"day":1,"start":1,"end":2}],\n'
        '"location":{"building":"汇文楼","floor":3,"room":"301"},\n'
        '"course_type":"major","delivery_mode":"线下传统","semester":"2025-2026-2"}\n\n'
        "规则：\n"
        "- day: 1=周一..5=周五\n"
        "- start/end: 上午=1-5节, 下午=6-10节, 晚上=11-14节\n"
        "- course_type: major=专业课 easy=选修/水课\n"
        "- delivery_mode: 线下传统/线上网课/线上线下混合\n"
        "- 教师评分默认4.0，未标注教师则teacher为null\n"
        "- 无教室信息则location为null\n"
        "- 线上课schedule可为空数组[]\n"
        "- 输出纯JSON，不要markdown代码块，不要解释文字"
    )

    @property
    def provider_name(self) -> str:
        return "QwenVision"

    def parse(self, image_path: str) -> list[dict[str, Any]]:
        """Send image to Qwen2.5-VL via OpenAI-compatible API, parse into Course dicts."""
        import base64
        from openai import OpenAI

        api_key = os.environ.get("OPENAI_API_KEY", "")
        if not api_key:
            raise RuntimeError(
                "Qwen Vision 需要 OPENAI_API_KEY 环境变量。"
                "请设置后重试，或切换 IMAGE_PROVIDER=mock 使用模拟识别。"
            )

        base_url = os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1")
        client = OpenAI(api_key=api_key, base_url=base_url)

        # Read and encode image
        with open(image_path, "rb") as f:
            image_b64 = base64.b64encode(f.read()).decode("utf-8")

        ext = Path(image_path).suffix.lower().lstrip(".")
        mime = f"image/{ext}" if ext in ("png", "jpg", "jpeg") else "image/png"

        last_error: Exception | None = None
        for attempt in range(2):  # 1 try + 1 retry
            try:
                response = client.chat.completions.create(
                    model=self.MODEL,
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"data:{mime};base64,{image_b64}"
                                    },
                                },
                                {"type": "text", "text": self.SYSTEM_PROMPT},
                            ],
                        }
                    ],
                    max_tokens=4096,
                    temperature=0.1,
                )

                raw_text = response.choices[0].message.content
                if not raw_text:
                    raise ValueError("Vision API 返回空内容")

                # Strip markdown code fences if present
                raw_text = raw_text.strip()
                if raw_text.startswith("```"):
                    raw_text = raw_text.split("\n", 1)[-1]
                    if raw_text.endswith("```"):
                        raw_text = raw_text[:-3]
                    raw_text = raw_text.strip()

                courses = json.loads(raw_text)
                if isinstance(courses, dict):
                    courses = courses.get("courses", [courses])
                if not isinstance(courses, list):
                    raise ValueError("Vision API 返回了非数组格式")

                # Validate and normalize each course
                from services.llm_parser import _normalize_course
                return [_normalize_course(c) for c in courses if isinstance(c, dict)]

            except (json.JSONDecodeError, ValueError, KeyError) as e:
                last_error = e
                if attempt == 0:
                    continue
            except Exception as e:
                last_error = e
                break

        raise RuntimeError(f"Qwen Vision Parse Failed: {last_error}")


class QwenVisionV2Parser(BaseImageParser):
    """Stub: Qwen Vision V2 (待开发)."""

    @property
    def provider_name(self) -> str:
        return "QwenVisionV2"

    def parse(self, image_path: str) -> list[dict[str, Any]]:
        raise NotImplementedError("QwenVisionV2Parser 尚未实现")


class DoubaoVisionParser(BaseImageParser):
    """Stub: ByteDance Doubao Vision (待开发)."""

    @property
    def provider_name(self) -> str:
        return "DoubaoVision"

    def parse(self, image_path: str) -> list[dict[str, Any]]:
        raise NotImplementedError("DoubaoVisionParser 尚未实现")


class DoubaoVisionV2Parser(BaseImageParser):
    """Stub: Doubao Vision V2 (待开发)."""

    @property
    def provider_name(self) -> str:
        return "DoubaoVisionV2"

    def parse(self, image_path: str) -> list[dict[str, Any]]:
        raise NotImplementedError("DoubaoVisionV2Parser 尚未实现")


class GLM4VParser(BaseImageParser):
    """Stub: Zhipu GLM-4V Vision (待开发)."""

    @property
    def provider_name(self) -> str:
        return "GLM4V"

    def parse(self, image_path: str) -> list[dict[str, Any]]:
        raise NotImplementedError("GLM4VParser 尚未实现")


# ── Factory ──────────────────────────────────────────────────────

_PARSER_REGISTRY: dict[str, type[BaseImageParser]] = {
    "mock": MockImageParser,
    "qwen": QwenVisionParser,
    "qwen_v2": QwenVisionV2Parser,
    "doubao": DoubaoVisionParser,
    "doubao_v2": DoubaoVisionV2Parser,
    "glm4v": GLM4VParser,
}


def get_image_parser() -> BaseImageParser:
    """Factory: return the configured image parser instance.

    Controlled by IMAGE_PROVIDER env var or config. Default: "mock".
    """
    parser_cls = _PARSER_REGISTRY.get(IMAGE_PROVIDER)
    if parser_cls is None:
        raise ValueError(
            f"未知的图片识别提供商: {IMAGE_PROVIDER}. "
            f"可用选项: {list(_PARSER_REGISTRY.keys())}"
        )
    return parser_cls()
