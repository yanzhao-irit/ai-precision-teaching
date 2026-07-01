import { useNavigate } from 'react-router-dom'
import { api } from '../../services/api'
import { useAsync } from '../../hooks/useAsync'
import {
  Card, Loading, ErrorBox, Empty, RankRow, SectionTitle, COLORS, pct, masteryColor, useTierLabels,
} from '../../components/ui'
import { useLang } from '../../i18n'

export default function DiagnosisTab({ courseCode, className, reloadKey }: { courseCode: string; className: string; reloadKey: number }) {
  const nav = useNavigate()
  const { t } = useLang()
  const tierLabels = useTierLabels()
  const weak = useAsync(() => api.weakKPs(courseCode, className, 10), [courseCode, className, reloadKey])
  const hard = useAsync(() => api.highErrorQuestions(courseCode, className, 10), [courseCode, className, reloadKey])
  const q = className ? `?class=${encodeURIComponent(className)}` : ''

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
      <Card>
        <SectionTitle right={<span className="text-xs text-gray-400">{t.clickForDetails}</span>}>
          {t.weakKPTop10}
        </SectionTitle>
        {weak.loading ? <Loading /> : weak.error ? <ErrorBox message={weak.error} /> :
          !weak.data || weak.data.length === 0 ? <Empty text={t.noDataShort} /> : (
            <div className="divide-y divide-gray-50">
              {weak.data.map((k) => (
                <RankRow
                  key={k.kp_code}
                  label={k.label}
                  sub={<>{t.masteryAccStudents(pct(k.avg_mastery), pct(k.accuracy), k.student_count)}</>}
                  value={k.avg_mastery}
                  display={tierLabels[k.tier] || ''}
                  color={masteryColor(k.avg_mastery)}
                  onClick={() => nav(`/course/${courseCode}/kp/${encodeURIComponent(k.kp_code)}${q}`)}
                />
              ))}
            </div>
          )}
      </Card>

      <Card>
        <SectionTitle right={<span className="text-xs text-gray-400">{t.clickForDetails}</span>}>
          {t.highErrorTop10}
        </SectionTitle>
        {hard.loading ? <Loading /> : hard.error ? <ErrorBox message={hard.error} /> :
          !hard.data || hard.data.length === 0 ? <Empty text={t.noDataShort} /> : (
            <div className="divide-y divide-gray-50">
              {hard.data.map((qq) => (
                <RankRow
                  key={qq.question_id}
                  label={<>{t.questionLabel(qq.seq_no, qq.kp_label || t.noKP)}</>}
                  sub={<span className="line-clamp-1">{qq.stem}</span>}
                  value={qq.error_rate ?? 0}
                  display={t.errorRate(pct(qq.error_rate))}
                  color={COLORS.unlearned}
                  onClick={() => nav(`/course/${courseCode}/question/${qq.question_id}${q}`)}
                />
              ))}
            </div>
          )}
      </Card>
    </div>
  )
}
