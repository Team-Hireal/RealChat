import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

const PORT = 6001;

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  base: './',
  build: {
    outDir: '../dist',
    emptyOutDir: true,
  },
  server: {
    port: PORT,
    proxy: {
      '/api': {
        target: 'http://localhost:5050',
        changeOrigin: true,
      },
      '/socket.io': {
        target: 'http://localhost:5050',
        changeOrigin: true,
        ws: true,
      }
    }
  }
})
