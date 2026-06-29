import { useRef, useState } from 'react'
import { api } from '../services/api'

type ZoneState = { state: 'idle' | 'busy' | 'ok' | 'err'; msg: string }
const IDLE: ZoneState = { state: 'idle', msg: '' }

/** 课程内导入：course 由所在页面（URL）决定，无需手填代码。 */
export default function UploadPanel({ courseCode, onDone }: { courseCode: string; onDone: () => void }) {
  const [zones, setZones] = useState<Record<string, ZoneState>>({ qb: IDLE, ce: IDLE, sa: IDLE })
  const setZone = (k: string, z: ZoneState) => setZones((s) => ({ ...s, [k]: z }))

  async function upload(kind: 'qb' | 'ce' | 'sa', file: File) {
    setZone(kind, { state: 'busy', msg: `上传中：${file.name}` })
    try {
      const r =
        kind === 'qb' ? await api.uploadQuestionBank(file, courseCode)
        : kind === 'ce' ? await api.uploadClassExport(file, courseCode)
        : await api.uploadStudentAnswers(file, courseCode)
      setZone(kind, { state: 'ok', msg: r.message || '导入完成' })
      onDone()
    } catch (e: unknown) {
      const err = e as { response?: { data?: { detail?: string } }; message?: string }
      setZone(kind, { state: 'err', msg: err?.response?.data?.detail || err?.message || '导入失败' })
    }
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
      <DropZone title="课程数据" hint="班级一键导出 .xlsx" accept=".xlsx" zone={zones.ce} onFile={(f) => upload('ce', f)} />
      <DropZone title="作业题库" hint="题库 .xls / .xlsx" accept=".xls,.xlsx" zone={zones.qb} onFile={(f) => upload('qb', f)} />
      <DropZone title="学生作业" hint="zip（内含 .doc）" accept=".zip" zone={zones.sa} onFile={(f) => upload('sa', f)} />
    </div>
  )
}

function DropZone({
  title, hint, accept, zone, onFile,
}: {
  title: string; hint: string; accept: string; zone: ZoneState; onFile: (f: File) => void
}) {
  const ref = useRef<HTMLInputElement>(null)
  const [over, setOver] = useState(false)
  const busy = zone.state === 'busy'
  const border =
    over ? 'border-blue-400 bg-blue-50'
    : zone.state === 'ok' ? 'border-green-300 bg-green-50'
    : zone.state === 'err' ? 'border-red-300 bg-red-50'
    : 'border-gray-300 bg-gray-50'

  return (
    <div
      onClick={() => !busy && ref.current?.click()}
      onDragOver={(e) => { e.preventDefault(); setOver(true) }}
      onDragLeave={() => setOver(false)}
      onDrop={(e) => { e.preventDefault(); setOver(false); const f = e.dataTransfer.files?.[0]; if (f) onFile(f) }}
      className={`border-2 border-dashed rounded-xl p-4 text-center cursor-pointer transition ${border}`}
    >
      <input
        ref={ref} type="file" accept={accept} className="hidden"
        onChange={(e) => { const f = e.target.files?.[0]; if (f) onFile(f); e.target.value = '' }}
      />
      <div className="text-2xl mb-1">{busy ? '⏳' : zone.state === 'ok' ? '✅' : zone.state === 'err' ? '⚠️' : '📁'}</div>
      <div className="text-sm font-medium text-gray-800">{title}</div>
      <div className="text-xs text-gray-400">{hint}</div>
      {zone.msg && (
        <div className={`text-xs mt-2 break-words ${
          zone.state === 'err' ? 'text-red-600' : zone.state === 'ok' ? 'text-green-700' : 'text-gray-500'
        }`}>
          {zone.msg}
        </div>
      )}
    </div>
  )
}
