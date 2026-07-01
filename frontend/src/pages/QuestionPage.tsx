import { useParams, useNavigate, useSearchParams } from 'react-router-dom'
import { api } from '../services/api'
import { useAsync } from '../hooks/useAsync'
import {
  Card, Loading, ErrorBox, Empty, Badge, SectionTitle, COLORS, pct, masteryColor,
} from '../components/ui'
import { useLang } from '../i18n'

const clean = (s: string | null | undefined) => {
  if (!s) return ''
  const t = s.trim()
  return t.toLowerCase() === 'nan' ? '' : t
}

export default function QuestionPage() {
  const { code = '', id } = useParams()
  const [sp] = useSearchParams()
  const className = sp.get('class') || ''
  const q = className ? `?class=${encodeURIComponent(className)}` : ''
  const nav = useNavigate()
  const { t } = useLang()
  const { data, loading, error } = useAsync(
    () => api.questionDrill(code, id!, className),
    [code, className, id],
  )

  if (loading) return <Loading />
  if (error) return <ErrorBox message={error} />
  if (!data) return <Empty text={t.questionNotFound} />

  const { detail, distribution, missed_students } = data
  const maxCount = Math.max(1, ...distribution.map((d) => d.count))

  return (
    <div className="space-y-5">
      <button onClick={() => nav(-1)} className="text-sm text-blue-600 hover:underline">{t.back}</button>

      <Card>
        <div className="flex items-center gap-2 mb-3">
          <span className="text-sm font-semibold text-gray-900">{t.questionNo(detail.seq_no)}</span>
          {data.kp_label && (
            <Badge kind="low">
              <span
                className="cursor-pointer"
                onClick={() => data.kp_code && nav(`/course/${code}/kp/${encodeURIComponent(data.kp_code)}${q}`)}
              >
                {t.knowledgePoint(data.kp_label)}
              </span>
            </Badge>
          )}
          <span className="ml-auto text-sm" style={{ color: masteryColor(data.accuracy) }}>
            {t.accuracy} {pct(data.accuracy)}（{data.correct}/{data.total}）
          </span>
        </div>

        <p className="text-gray-800 mb-4 whitespace-pre-wrap">{detail.stem}</p>

        <div className="space-y-2">
          {detail.options.map((o) => (
            <div
              key={o.label}
              className={`flex items-start gap-2 rounded-lg border px-3 py-2 text-sm ${
                o.is_correct ? 'border-green-300 bg-green-50' : 'border-gray-200'
              }`}
            >
              <span className={`font-semibold ${o.is_correct ? 'text-green-700' : 'text-gray-600'}`}>{o.label}</span>
              <span className="text-gray-700">{o.text}</span>
              {o.is_correct && <span className="ml-auto text-xs text-green-700">{t.correctAnswer}</span>}
            </div>
          ))}
        </div>

        {clean(detail.explanation) && (
          <div className="mt-4 text-sm text-gray-600 bg-gray-50 rounded-lg p-3">
            <span className="font-semibold">{t.explanation}</span>{clean(detail.explanation)}
          </div>
        )}
      </Card>

      <Card>
        <SectionTitle right={<span className="text-xs text-gray-400">{t.studentAnswerDist}</span>}>
          {t.distractorAnalysis}
        </SectionTitle>
        {distribution.length === 0 ? (
          <Empty text={t.noAnswerData} />
        ) : (
          <div className="space-y-3">
            {distribution.map((d, i) => (
              <div key={i} className="flex items-center gap-3">
                <span className="w-10 text-sm font-semibold text-gray-700">{d.answer || t.empty}</span>
                <div className="flex-1 bg-gray-100 rounded-full h-5 overflow-hidden">
                  <div
                    className="h-5 rounded-full flex items-center justify-end pr-2 text-xs text-white"
                    style={{
                      width: `${Math.round((d.count / maxCount) * 100)}%`,
                      background: d.is_correct ? COLORS.mastered : COLORS.unlearned,
                    }}
                  >
                    {d.count}
                  </div>
                </div>
                {d.is_correct && <span className="text-xs text-green-700 shrink-0">✓</span>}
              </div>
            ))}
          </div>
        )}
        <p className="text-xs text-gray-400 mt-3">{t.distractorNote}</p>
      </Card>

      <Card>
        <SectionTitle>{t.missedStudents(missed_students.length)}</SectionTitle>
        {missed_students.length === 0 ? (
          <Empty text={t.noMissed} />
        ) : (
          <div className="flex flex-wrap gap-2">
            {missed_students.map((s) => (
              <button
                key={s.student_no}
                onClick={() => nav(`/course/${code}/student/${s.student_no}${q}`)}
                className="px-3 py-1.5 rounded-lg border border-gray-200 text-sm text-gray-700 hover:bg-gray-50"
              >
                {s.name || s.student_no}
                <span className="text-xs text-red-500 ml-1">{t.selectedAnswer(s.answer || t.empty)}</span>
              </button>
            ))}
          </div>
        )}
      </Card>
    </div>
  )
}
