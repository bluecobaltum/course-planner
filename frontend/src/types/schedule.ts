// Mirrors backend models/course.py ScheduleSlot
export interface ScheduleSlot {
  day: number;   // 1=Monday .. 5=Friday
  start: number; // 1-14
  end: number;   // 1-14, inclusive
}

// Mirrors backend models/course.py Teacher
export interface Teacher {
  name: string;
  rating: number; // 1.0-5.0
}

// Mirrors backend models/course.py Location
export interface Location {
  building: string;
  floor: number;
  room: string;
}

// Mirrors backend models/course.py Course
export interface Course {
  section_id: string;
  course_code: string;
  course_name: string;
  credit_transfer_group: string;
  credits: number;
  teacher: Teacher | null;
  schedule: ScheduleSlot[];
  location: Location | null;
  course_type: "major" | "easy";
  category: "regular" | "pe";
  required: boolean;
  delivery_mode: "线下传统" | "线上网课" | "线上线下混合";
  semester: string;
}

// Mirrors backend models/schedule.py ScoreBreakdown
export interface ScoreBreakdown {
// Schedule-focused metrics (current)
  free_days: number;
  compactness: number;
  no_morning: number;
  no_night: number;
  distribution: number;
  // Legacy fields (reserved for future GPA/teacher modules)
  gpa_score?: number;
  compact_score?: number;
  stress_score?: number;
  free_score?: number;
  morning_penalty?: number;
  friday_penalty?: number;
  monday_penalty?: number;
  afternoon_penalty?: number;
}

// Mirrors backend models/schedule.py PlanAnalysis
export interface PlanAnalysis {
  total_credits: number;
  school_days: number;
  earliest_period: number;
  score_breakdown: ScoreBreakdown;
  reasons: string[];
}

// Mirrors backend models/schedule.py Plan
export interface Plan {
  id: string;
  rank: number;
  score: number;
  label: string;
  courses: Course[];
  analysis: PlanAnalysis;
  matched_strategies: string[];
  llm_review?: {
    overall: string;
    score: number;
    pros: string[];
    cons: string[];
    suggestions: string[];
    best_for: string;
  } | null; // strategy IDs, not full objects
}

// Mirrors backend models/response.py GenerateResponse
export interface GenerateResponse {
  scenario: string;
  plans: Plan[];
}

// Mirrors backend models/response.py ErrorResponse
export interface ErrorResponse {
  error: string;
  detail: string;
  message: string;
}

// Mirrors backend routes/import_router.py ImportStats + ImportResponse
export interface ImportStats {
  course_count: number;
  processing_time_ms: number;
  method: string;
}

export interface ImportResult {
  success: boolean;
  method: string;
  courses: Course[];
  stats: ImportStats;
}

export interface ImportError {
  success: false;
  error: string;
  message: string;
}
