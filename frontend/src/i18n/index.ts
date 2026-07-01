import { createContext, useContext } from 'react'
import zh from './zh'
import en from './en'

export type Lang = 'zh' | 'en'
export type Translations = typeof zh

export const translations: Record<Lang, Translations> = { zh, en }

export const LangContext = createContext<{
  lang: Lang
  setLang: (l: Lang) => void
  t: Translations
}>({ lang: 'zh', setLang: () => {}, t: zh })

export function useLang() {
  return useContext(LangContext)
}
