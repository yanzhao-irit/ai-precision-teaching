import { Link } from 'react-router-dom'

export function TopBar() {
  return (
    <header className="bg-white border-b border-gray-200 sticky top-0 z-10">
      <div className="max-w-6xl mx-auto px-4 py-3 flex items-center gap-3">
        <Link to="/" className="font-bold text-gray-900">🎓 AI 精准教学</Link>
        <span className="text-sm text-gray-400">教师端</span>
      </div>
    </header>
  )
}
