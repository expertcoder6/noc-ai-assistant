// vite.config.js for Network AI Assistant frontend
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import tailwindcss from '@tailwindcss/vite';

export default defineConfig({
  plugins: [react(), tailwindcss()
  ],
  server: {
    port: 5173,
    proxy: {
      // Proxy API requests to FastAPI backend
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false,
        // rewrite removes the leading /api if needed; backend expects /api/v1
        // keep as is because the backend router prefix includes /api/v1
      },
    },
  },
});
