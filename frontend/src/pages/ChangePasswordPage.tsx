import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { useLang } from '../i18n'

const BASE = import.meta.env.VITE_API_BASE ?? 'http://localhost:8000'

export default function ChangePasswordPage() {
  const { refresh } = useAuth()
  const { t } = useLang()
  const navigate = useNavigate()

  const [current, setCurrent] = useState('')
  const [next, setNext] = useState('')
  const [confirm, setConfirm] = useState('')
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    if (next !== confirm) { setError(t.passwordMismatch ?? '两次密码不一致'); return }
    if (next.length < 8) { setError(t.passwordTooShort ?? '密码至少8位'); return }
    setBusy(true)
    try {
      const res = await fetch(`${BASE}/auth/change-password`, {
        method: 'POST',
        credentials: 'include',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ current_password: current, new_password: next }),
      })
      if (!res.ok) {
        const err = await res.json().catch(() => ({}))
        throw new Error(err.detail ?? '修改失败')
      }
      await refresh()
      navigate('/', { replace: true })
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : String(err))
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center px-4">
      <div className="w-full max-w-sm bg-white rounded-2xl shadow-lg p-8">
        <h1 className="text-xl font-bold text-gray-800 mb-1">{t.changePassword ?? '修改密码'}</h1>
        <p className="text-sm text-gray-400 mb-6">{t.changePasswordHint ?? '首次登录，请修改初始密码'}</p>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-600 mb-1">{t.currentPassword ?? '当前密码'}</label>
            <input type="password" value={current} onChange={e => setCurrent(e.target.value)} required
              className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400" />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-600 mb-1">{t.newPassword ?? '新密码'}</label>
            <input type="password" value={next} onChange={e => setNext(e.target.value)} required
              className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400" />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-600 mb-1">{t.confirmPassword ?? '确认密码'}</label>
            <input type="password" value={confirm} onChange={e => setConfirm(e.target.value)} required
              className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400" />
          </div>

          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 text-sm rounded-lg px-3 py-2">
              {error}
            </div>
          )}

          <button type="submit" disabled={busy}
            className="w-full bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white font-semibold rounded-lg py-2 text-sm transition-colors">
            {busy ? '保存中…' : (t.savePassword ?? '保存')}
          </button>
        </form>
      </div>
    </div>
  )
}
