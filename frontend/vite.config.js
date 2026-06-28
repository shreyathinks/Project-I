import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/auth': { target: 'http://localhost:8000', changeOrigin: true },
      '/inventory': { target: 'http://localhost:8000', changeOrigin: true },
      '/ocr': { target: 'http://localhost:8000', changeOrigin: true },
      '/barcode': { target: 'http://localhost:8000', changeOrigin: true },
      '/recipes': { target: 'http://localhost:8000', changeOrigin: true },
      '/shopping': { target: 'http://localhost:8000', changeOrigin: true },
      '/prediction': { target: 'http://localhost:8000', changeOrigin: true },
      '/dashboard': { target: 'http://localhost:8000', changeOrigin: true },
    }
  },
  build: {
    outDir: 'dist',
    sourcemap: false,
  }
})
