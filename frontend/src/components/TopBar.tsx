import { Link } from 'react-router-dom'
import { useLang } from '../i18n'
import { useAuth } from '../context/AuthContext'

export function TopBar() {
  const { lang, setLang, t } = useLang()
  const { logout } = useAuth()
  return (
    <header className="bg-white border-b border-gray-200 sticky top-0 z-10">
      <div className="max-w-6xl mx-auto px-4 py-3 flex items-center gap-3">
        <Link to="/" className="font-bold text-gray-900">🎓 {t.appTitle}</Link>
        <span className="text-sm text-gray-400">{t.appSubtitle}</span>
        <div className="ml-auto flex items-center gap-3 text-sm">
          <button
            onClick={() => setLang('zh')}
            className={`px-2 py-0.5 rounded-md transition ${lang === 'zh' ? 'bg-blue-600 text-white' : 'text-gray-500 hover:text-gray-800'}`}
          >
            中文
          </button>
          <button
            onClick={() => setLang('en')}
            className={`px-2 py-0.5 rounded-md transition ${lang === 'en' ? 'bg-blue-600 text-white' : 'text-gray-500 hover:text-gray-800'}`}
          >
            EN
          </button>
          <button
            onClick={logout}
            className="text-gray-400 hover:text-red-500 transition-colors"
          >
            {t.logout ?? '退出'}
          </button>
        </div>
      </div>
    </header>
  )
}
