import { useEffect, useState } from 'react'

interface AsyncState<T> {
  data: T | null
  loading: boolean
  error: string | null
}

/** 通用异步数据加载：deps 变化时重新拉取。 */
export function useAsync<T>(fn: () => Promise<T>, deps: unknown[]): AsyncState<T> {
  const [state, setState] = useState<AsyncState<T>>({ data: null, loading: true, error: null })

  useEffect(() => {
    let active = true
    setState((s) => ({ ...s, loading: true, error: null }))
    fn()
      .then((d) => active && setState({ data: d, loading: false, error: null }))
      .catch((e) =>
        active &&
        setState({
          data: null,
          loading: false,
          error: e?.response?.data?.detail || e?.message || '请求失败',
        }),
      )
    return () => {
      active = false
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, deps)

  return state
}
