import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// Dev server proxies API calls to the Tinkle FastAPI backend (uvicorn on :8000)
// so the React 3D client can talk to /api/v1/visual3d/* without CORS setup.
export default defineConfig({
  root: 'src',
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/api': 'http://localhost:8000',
    },
  },
  build: {
    outDir: '../dist',
    emptyOutDir: true,
  },
});
