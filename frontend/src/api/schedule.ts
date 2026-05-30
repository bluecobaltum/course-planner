import type { GenerateResponse, Course } from "@/types/schedule";
import type { StrategyListResponse } from "@/types/strategy";

const API_BASE = "http://localhost:8000";

export async function generateSchedule(
  scenario: string,
  easyCount: number
): Promise<GenerateResponse> {
  const res = await fetch(`${API_BASE}/api/generate_schedule`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ scenario, easy_count: easyCount }),
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.message || `API error: ${res.status}`);
  }

  return res.json();
}

export async function getStrategies(
  scenario?: string
): Promise<StrategyListResponse> {
  const params = scenario ? `?scenario=${encodeURIComponent(scenario)}` : "";
  const res = await fetch(`${API_BASE}/api/strategies${params}`);

  if (!res.ok) {
    throw new Error(`Failed to load strategies: ${res.status}`);
  }

  return res.json();
}

// ── Courses CRUD ──

export async function getCourses(): Promise<Course[]> {
  const res = await fetch(`${API_BASE}/api/courses`);
  if (!res.ok) throw new Error(`Failed to load courses: ${res.status}`);
  return res.json();
}

export async function createCourse(course: Course): Promise<Course> {
  const res = await fetch(`${API_BASE}/api/courses`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(course),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || `Failed to create course: ${res.status}`);
  }
  return res.json();
}

export async function updateCourse(
  sectionId: string,
  course: Course
): Promise<Course> {
  const res = await fetch(`${API_BASE}/api/courses/${sectionId}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(course),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || `Failed to update course: ${res.status}`);
  }
  return res.json();
}

export async function deleteCourse(sectionId: string): Promise<void> {
  const res = await fetch(`${API_BASE}/api/courses/${sectionId}`, {
    method: "DELETE",
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || `Failed to delete course: ${res.status}`);
  }
}
