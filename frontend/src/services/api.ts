// API 客户端 · 后端 CORS 已开放，直接跨域请求 backend
import axios from 'axios'
import type {
  Course, Student, FullDiagnosis, Mastery, Profile, Recommendation,
  WatchItem, EvalOverview,
  CourseSummary, DashboardData, WeakKP, HighErrorQuestion, QuestionDrill, KPDrill,
  AttentionData, RosterData,
} from '../types'

const baseURL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export const http = axios.create({ baseURL, timeout: 30000 })

const cc = (course_code: string) => ({ params: { course_code } })
// 课程 + 可选班级（缺省=全部班级）
const ccc = (course_code: string, class_name?: string) => ({
  params: { course_code, class_name: class_name || undefined },
})

export const api = {
  courses: (): Promise<Course[]> =>
    http.get('/api/courses').then((r) => r.data),

  createCourse: (course_code: string, course_name: string): Promise<Course> =>
    http.post('/api/courses', { course_code, course_name }).then((r) => r.data),

  students: (course: string): Promise<Student[]> =>
    http.get('/api/students', cc(course)).then((r) => r.data),

  diagnosis: (course: string, no: string): Promise<FullDiagnosis> =>
    http.get(`/api/diagnosis/student/${no}`, cc(course)).then((r) => r.data),

  mastery: (course: string, no: string): Promise<Mastery> =>
    http.get(`/api/diagnosis/student/${no}/mastery`, cc(course)).then((r) => r.data),

  profile: (course: string, no: string): Promise<Profile> =>
    http.get(`/api/profiles/student/${no}`, cc(course)).then((r) => r.data),

  recommendations: (course: string, no: string): Promise<Recommendation> =>
    http.get(`/api/recommendations/student/${no}`, cc(course)).then((r) => r.data),

  watchList: (course: string): Promise<WatchItem[]> =>
    http.get('/api/warnings/watch-list', cc(course)).then((r) => r.data),

  overview: (course: string): Promise<EvalOverview> =>
    http.get('/api/evaluation/overview', cc(course)).then((r) => r.data),

  // ===== 看板 · dashboard =====
  courseSummaries: (): Promise<CourseSummary[]> =>
    http.get('/api/dashboard/courses').then((r) => r.data),

  classes: (course: string): Promise<string[]> =>
    http.get('/api/dashboard/classes', cc(course)).then((r) => r.data),

  dashboard: (course: string, cls?: string): Promise<DashboardData> =>
    http.get('/api/dashboard/course', ccc(course, cls)).then((r) => r.data),

  attention: (course: string, cls?: string): Promise<AttentionData> =>
    http.get('/api/dashboard/attention', ccc(course, cls)).then((r) => r.data),

  roster: (course: string, cls?: string): Promise<RosterData> =>
    http.get('/api/dashboard/students', ccc(course, cls)).then((r) => r.data),

  weakKPs: (course: string, cls?: string, limit = 10): Promise<WeakKP[]> =>
    http
      .get('/api/dashboard/weak-knowledge-points', { params: { course_code: course, class_name: cls || undefined, limit } })
      .then((r) => r.data),

  highErrorQuestions: (course: string, cls?: string, limit = 10): Promise<HighErrorQuestion[]> =>
    http
      .get('/api/dashboard/high-error-questions', { params: { course_code: course, class_name: cls || undefined, limit } })
      .then((r) => r.data),

  questionDrill: (course: string, id: string, cls?: string): Promise<QuestionDrill> =>
    http.get(`/api/dashboard/question/${id}`, ccc(course, cls)).then((r) => r.data),

  kpDrill: (course: string, code: string, cls?: string): Promise<KPDrill> =>
    http.get(`/api/dashboard/knowledge-point/${encodeURIComponent(code)}`, ccc(course, cls)).then((r) => r.data),

  // ===== 数据上传 · upload =====
  uploadQuestionBank: (file: File, course_code: string, course_name?: string): Promise<{ message: string }> => {
    const fd = new FormData()
    fd.append('file', file)
    fd.append('course_code', course_code)
    if (course_name) fd.append('course_name', course_name)
    return http.post('/api/upload/question-bank', fd).then((r) => r.data)
  },

  uploadClassExport: (file: File, course_code: string, course_name?: string): Promise<{ message: string }> => {
    const fd = new FormData()
    fd.append('file', file)
    fd.append('course_code', course_code)
    if (course_name) fd.append('course_name', course_name)
    return http.post('/api/upload/class-export', fd).then((r) => r.data)
  },

  uploadStudentAnswers: (file: File, course_code: string): Promise<{ message: string }> => {
    const fd = new FormData()
    fd.append('file', file)
    fd.append('course_code', course_code)
    return http.post('/api/upload/student-answers', fd).then((r) => r.data)
  },
}
