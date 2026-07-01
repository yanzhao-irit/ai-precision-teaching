import type { ReactNode } from 'react'
import { useLang } from '../i18n'

export function Card({ title, children, className = '' }: { title?: ReactNode; children: ReactNode; className?: string }) {
  return (
    <div className={`bg-white rounded-xl shadow-sm border border-gray-100 p-5 ${className}`}>
      {title && <h3 className="text-base font-semibold text-gray-800 mb-3">{title}</h3>}
      {children}
    </div>
  )
}

export function Stat({ label, value, hint }: { label: string; value: ReactNode; hint?: string }) {
  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-5">
      <div className="text-2xl font-bold text-gray-900">{value}</div>
      <div className="text-sm text-gray-500 mt-1">{label}</div>
      {hint && <div className="text-xs text-gray-400 mt-0.5">{hint}</div>}
    </div>
  )
}

const TIER_STYLE: Record<string, string> = {
  advanced: 'bg-green-100 text-green-800',
  on_track: 'bg-blue-100 text-blue-800',
  weak: 'bg-yellow-100 text-yellow-800',
  at_risk: 'bg-red-100 text-red-800',
  high: 'bg-red-100 text-red-800',
  medium: 'bg-yellow-100 text-yellow-800',
  low: 'bg-gray-100 text-gray-700',
  mastered: 'bg-green-100 text-green-800',
  partial: 'bg-yellow-100 text-yellow-800',
  unlearned: 'bg-red-100 text-red-800',
}

export function Badge({ children, kind = '' }: { children: ReactNode; kind?: string }) {
  return (
    <span className={`px-2 py-0.5 rounded-full text-xs font-semibold ${TIER_STYLE[kind] || 'bg-gray-100 text-gray-700'}`}>
      {children}
    </span>
  )
}

export function Bar({ value, color = 'bg-blue-500' }: { value: number; color?: string }) {
  const pct = Math.max(0, Math.min(100, Math.round(value * 100)))
  return (
    <div className="w-full bg-gray-100 rounded-full h-2 overflow-hidden">
      <div className={`${color} h-2 rounded-full`} style={{ width: `${pct}%` }} />
    </div>
  )
}

export function Loading({ text }: { text?: string }) {
  const { t } = useLang()
  return <div className="text-sm text-gray-400 py-8 text-center">{text ?? t.loading}</div>
}

export function ErrorBox({ message }: { message: string }) {
  return (
    <div className="bg-red-50 border border-red-200 text-red-700 rounded-lg p-4 text-sm">
      ⚠️ {message}
    </div>
  )
}

export function Empty({ text }: { text: string }) {
  return <div className="text-sm text-gray-400 py-8 text-center">{text}</div>
}

// ===== charts & color helpers =====

export const COLORS = {
  mastered: '#22c55e',
  partial: '#f59e0b',
  unlearned: '#ef4444',
  neutral: '#e5e7eb',
  blue: '#3b82f6',
}

export function useTierLabels(): Record<string, string> {
  const { t } = useLang()
  return {
    mastered: t.mastered,
    partial: t.partial,
    unlearned: t.unlearned,
    learning: t.partial,
    not_learned: t.unlearned,
    no_data: t.noDataTier,
  }
}

/** Kept for compatibility — prefer useTierLabels() in components */
export const TIER_CN: Record<string, string> = {
  mastered: '已掌握',
  partial: '部分掌握',
  unlearned: '未掌握',
  learning: '部分掌握',
  not_learned: '未掌握',
  no_data: '无数据',
}

export const pct = (x: number | null | undefined, d = 0): string =>
  x == null ? '—' : `${(x * 100).toFixed(d)}%`

export function masteryColor(v: number | null | undefined): string {
  if (v == null) return COLORS.neutral
  if (v >= 0.7) return COLORS.mastered
  if (v >= 0.4) return COLORS.partial
  return COLORS.unlearned
}

export function tierKind(tier: string | null | undefined): string {
  if (tier === 'mastered') return 'mastered'
  if (tier === 'partial' || tier === 'learning') return 'partial'
  return 'unlearned'
}

export function Donut({
  segments,
  size = 132,
  centerTop,
  centerBottom,
}: {
  segments: { value: number; color: string }[]
  size?: number
  centerTop?: ReactNode
  centerBottom?: ReactNode
}) {
  const total = segments.reduce((s, x) => s + x.value, 0) || 1
  const stroke = 16
  const r = size / 2 - stroke / 2 - 2
  const c = 2 * Math.PI * r
  let offset = 0
  return (
    <div className="relative inline-flex items-center justify-center" style={{ width: size, height: size }}>
      <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`}>
        <circle cx={size / 2} cy={size / 2} r={r} fill="none" stroke={COLORS.neutral} strokeWidth={stroke} />
        <g transform={`rotate(-90 ${size / 2} ${size / 2})`}>
          {segments.map((s, i) => {
            const len = (s.value / total) * c
            const el = (
              <circle
                key={i}
                cx={size / 2}
                cy={size / 2}
                r={r}
                fill="none"
                stroke={s.color}
                strokeWidth={stroke}
                strokeDasharray={`${len} ${c - len}`}
                strokeDashoffset={-offset}
                strokeLinecap="butt"
              />
            )
            offset += len
            return el
          })}
        </g>
      </svg>
      <div className="absolute flex flex-col items-center">
        {centerTop != null && <div className="text-2xl font-bold text-gray-900 leading-none">{centerTop}</div>}
        {centerBottom != null && <div className="text-xs text-gray-500 mt-1">{centerBottom}</div>}
      </div>
    </div>
  )
}

export function RankRow({
  label,
  sub,
  value,
  display,
  color,
  onClick,
}: {
  label: ReactNode
  sub?: ReactNode
  value: number
  display: string
  color?: string
  onClick?: () => void
}) {
  const pctv = Math.max(0, Math.min(100, Math.round(value * 100)))
  return (
    <div
      className={`py-2 ${onClick ? 'cursor-pointer hover:bg-gray-50 -mx-2 px-2 rounded-lg' : ''}`}
      onClick={onClick}
    >
      <div className="flex items-center justify-between gap-3 mb-1">
        <div className="text-sm text-gray-800 truncate">{label}</div>
        <div className="text-sm font-semibold text-gray-700 shrink-0 tabular-nums">{display}</div>
      </div>
      <div className="w-full bg-gray-100 rounded-full h-2 overflow-hidden">
        <div className="h-2 rounded-full" style={{ width: `${pctv}%`, background: color || COLORS.blue }} />
      </div>
      {sub != null && <div className="text-xs text-gray-400 mt-1">{sub}</div>}
    </div>
  )
}

export function SectionTitle({ children, right }: { children: ReactNode; right?: ReactNode }) {
  return (
    <div className="flex items-center justify-between mb-3">
      <h3 className="text-base font-semibold text-gray-800">{children}</h3>
      {right}
    </div>
  )
}
