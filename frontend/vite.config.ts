import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    // WSL2 对 /mnt/c（Windows 文件）的 inotify 不生效，必须用轮询才能热更新
    watch: { usePolling: true, interval: 300 },
  },
})
