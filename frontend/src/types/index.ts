// API 响应类型 · API response types（对齐后端 EngineDataGateway 输出）

export interface Course {
  course_code: string
  course_name: string
  term_code: string | null
}

export interface Student {
  id: string // student_no
  name: string | null
}

export interface MasteryItem {
  probability: number
  state: string // mastered | partial | unlearned
  attempts: number
  recent_trend: string
  confidence: number
  last_attempt_correct: boolean | null
}

export type Mastery = Record<string, MasteryItem>

export interface SingleDiagnosis {
  student_id: string
  question_id: string
  question_text: string
  visible_concept_id: string
  visible_concept: string
  visible_concept_cn: string
  visible_concept_mastery: number
  root_cause_concept: string
  root_cause_concept_cn: string
  cause_type: string
  prerequisite_gap_depth: number | null
  suspicion_score: number
  error_type: string
  error_pattern: string
  time_seconds: number | null
  misconceptions: string[]
  explanation: string
  recommendation: string
  priority: 'high' | 'medium' | 'low'
}

export interface FullDiagnosis {
  student_id: string
  total_attempts: number
  total_errors: number
  mastery_summary: {
    avg_mastery: number
    by_state: { mastered: number; learning: number; not_learned: number }
  }
  individual_diagnoses: SingleDiagnosis[]
  error_patterns: {
    total_errors: number
    by_type: Record<string, number>
    most_common: string | null
    systematic_errors: number
  }
  priority_interventions: {
    concept: string
    concept_cn: string
    cause_type: string
    suspicion: number
    example_question: string
    recommendation: string
    priority: string
  }[]
}

export interface Profile {
  student_id: string
  tier: 'advanced' | 'on_track' | 'weak' | 'at_risk'
  knowledge: {
    avg_mastery: number
    weak_concept_count: number
    weak_concepts: ({ concept_id: string } & MasteryItem)[]
    mastery_detail: Mastery
  }
  behavior: { total_attempts: number; accuracy: number; avg_time_seconds: number }
  cognition: { dominant_error_types: string[] }
}

export interface Recommendation {
  student_id: string
  remedial: any[]
  consolidation: any[]
  extension: any[]
  summary: {
    total_weak_concepts: number
    total_learning_concepts: number
    total_mastered_concepts: number
    recommended_count: number
  }
}

export interface WatchItem {
  student_id: string
  tier: string
  risk_score: number
  signals: string[]
  avg_mastery: number
  accuracy: number
  wrong_count: number
}

export interface EvalOverview {
  total_students: number
  total_concepts: number
  total_relations: number
  total_diagnosed_mistakes: number
  tier_distribution: { at_risk: number; weak: number; on_track: number; advanced: number }
}

// ===== 教师端看板 · teacher dashboard =====

export interface CourseSummary {
  course_code: string
  course_name: string
  term_code: string | null
  student_count: number
  class_count: number
  chapter_count: number
  accuracy: number | null
}

export interface DashboardData {
  course_code: string
  class_name: string | null
  stats: {
    student_count: number
    class_count: number
    chapter_count: number
    response_count: number
    tested_students: number
    accuracy: number | null
    engagement: {
      task_completion_ratio: number | null
      avg_discussion_count: number | null
      avg_chapter_visits: number | null
    }
    grade: { avg_homework: number | null; avg_final: number | null }
  }
  mastery: {
    avg_mastery: number
    tested_students: number
    distribution: { mastered: number; partial: number; unlearned: number }
  }
}

export interface WeakKP {
  kp_code: string
  label: string
  avg_mastery: number
  tier: string
  accuracy: number | null
  student_count: number
}

export interface HighErrorQuestion {
  question_id: string
  seq_no: number
  stem: string
  type: string
  total: number
  correct: number
  accuracy: number | null
  error_rate: number | null
  kp_code: string | null
  kp_label: string | null
}

export interface QuestionOption {
  label: string
  text: string
  is_correct: boolean
}

export interface QuestionDrill {
  detail: {
    question_id: string
    seq_no: number
    type: string
    stem: string
    correct_answer: string | null
    explanation: string | null
    difficulty: number | null
    options: QuestionOption[]
  }
  kp_code: string | null
  kp_label: string | null
  total: number
  correct: number
  accuracy: number | null
  distribution: { answer: string | null; count: number; is_correct: boolean }[]
  missed_students: { student_no: string; name: string | null; answer: string | null }[]
}

export interface RosterStudent {
  student_no: string
  name: string | null
  class_name: string | null
  tier: 'excellent' | 'on_track' | 'weak' | 'untested'
  avg_mastery: number | null
  accuracy: number | null
  homework_score: number | null
  attitude: boolean
}

export interface RosterData {
  students: RosterStudent[]
  counts: { excellent: number; on_track: number; weak: number; untested: number; attitude: number }
}

export interface AttentionData {
  academic: { student_no: string; name: string | null; avg_mastery: number; accuracy: number | null }[]
  attitude: {
    student_no: string; name: string | null
    homework_score: number | null; final_score: number | null
    task_completed: number | null; task_total: number | null
  }[]
  untested: { student_no: string; name: string | null; task_ratio: number | null; homework_score: number | null }[]
  counts: { academic: number; attitude: number; untested: number; total_enrolled: number }
}

export interface KPDrill {
  kp_code: string
  label: string
  avg_mastery: number | null
  tier: string | null
  accuracy: number | null
  students: { student_no: string; name: string | null; total: number; correct: number; accuracy: number | null }[]
}
