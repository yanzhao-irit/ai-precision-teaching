import { useParams, useNavigate } from 'react-router-dom'
import { api } from '../services/api'
import { useAsync } from '../hooks/useAsync'
import {
  Card, Stat, Loading, ErrorBox, Empty, Badge, Donut, SectionTitle,
  COLORS, pct, masteryColor, tierKind, useTierLabels,
} from '../components/ui'
import { useLang } from '../i18n'

export default function StudentPage() {
  const { code = '', no } = useParams()
  const nav = useNavigate()
  const { t } = useLang()
  const tierLabels = useTierLabels()

  const diag = useAsync(() => api.diagnosis(code, no!), [code, no])
  const prof = useAsync(() => api.profile(code, no!), [code, no])
  const mast = useAsync(() => api.mastery(code, no!), [code, no])
  const labels = useAsync(() => api.weakKPs(code, undefined, 999), [code])

  if (diag.loading) return <Loading />
  if (diag.error) return <ErrorBox message={diag.error} />
  if (!diag.data) return <Empty text={t.noDiagData} />

  const d = diag.data
  const by = d.mastery_summary.by_state
  const labelMap = new Map((labels.data || []).map((k) => [k.kp_code, k.label]))
  const masteryRows = Object.entries(mast.data || {}).sort(
    (a, b) => a[1].probability - b[1].probability,
  )

  return (
    <div className="space-y-5">
      <button onClick={() => nav(-1)} className="text-sm text-blue-600 hover:underline">{t.back}</button>

      <div className="flex items-center gap-2">
        <h2 className="text-lg font-semibold text-gray-800">{t.studentTitle(no!)}</h2>
        {prof.data && <Badge kind={prof.data.tier}>{prof.data.tier}</Badge>}
      </div>

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <Stat label={t.avgMasteryStat} value={pct(d.mastery_summary.avg_mastery)} />
        <Stat label={t.attemptsErrors} value={`${d.total_attempts} / ${d.total_errors}`} />
        <Stat label={t.accuracyStat} value={pct(prof.data?.behavior.accuracy)} />
        <Stat label={t.masteredKPs} value={`${by.mastered} / ${by.mastered + by.learning + by.not_learned}`} />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
        <Card>
          <SectionTitle>{t.kpMasteryDistribution}</SectionTitle>
          <div className="flex items-center gap-6">
            <Donut
              segments={[
                { value: by.mastered, color: COLORS.mastered },
                { value: by.learning, color: COLORS.partial },
                { value: by.not_learned, color: COLORS.unlearned },
              ]}
              centerTop={by.mastered + by.learning + by.not_learned}
              centerBottom={t.knowledgePoints}
            />
            <div className="space-y-2 text-sm">
              <Legend color={COLORS.mastered} label={t.mastered} v={by.mastered} />
              <Legend color={COLORS.partial} label={t.partial} v={by.learning} />
              <Legend color={COLORS.unlearned} label={t.unlearned} v={by.not_learned} />
            </div>
          </div>
        </Card>

        <Card>
          <SectionTitle>{t.priorityInterventions}</SectionTitle>
          {d.priority_interventions.length === 0 ? (
            <Empty text={t.noInterventions} />
          ) : (
            <div className="space-y-3">
              {d.priority_interventions.map((p, i) => (
                <div key={i} className="border-l-2 border-amber-300 pl-3">
                  <div className="flex items-center gap-2">
                    <Badge kind={p.priority}>{p.priority}</Badge>
                    <span className="text-sm font-medium text-gray-800">{p.concept_cn || p.concept}</span>
                  </div>
                  <p className="text-xs text-gray-500 mt-1 whitespace-pre-wrap">{p.recommendation}</p>
                </div>
              ))}
            </div>
          )}
        </Card>
      </div>

      <Card>
        <SectionTitle>{t.kpMasteryDetail}</SectionTitle>
        {mast.loading ? <Loading /> : masteryRows.length === 0 ? (
          <Empty text={t.noMasteryDetail} />
        ) : (
          <div className="divide-y divide-gray-50">
            {masteryRows.map(([codeKey, m]) => (
              <div key={codeKey} className="py-2 flex items-center gap-3">
                <span className="text-sm text-gray-800 flex-1 truncate">{labelMap.get(codeKey) || codeKey}</span>
                <div className="w-40 bg-gray-100 rounded-full h-2 overflow-hidden">
                  <div
                    className="h-2 rounded-full"
                    style={{ width: `${Math.round(m.probability * 100)}%`, background: masteryColor(m.probability) }}
                  />
                </div>
                <span className="text-sm font-semibold w-12 text-right" style={{ color: masteryColor(m.probability) }}>
                  {pct(m.probability)}
                </span>
                <Badge kind={tierKind(m.state)}>{tierLabels[m.state] || m.state}</Badge>
              </div>
            ))}
          </div>
        )}
      </Card>
    </div>
  )
}

function Legend({ color, label, v }: { color: string; label: string; v: number }) {
  return (
    <div className="flex items-center gap-2">
      <span className="inline-block w-3 h-3 rounded-sm" style={{ background: color }} />
      <span className="text-gray-700 w-20">{label}</span>
      <span className="font-semibold text-gray-900">{v}</span>
    </div>
  )
}
