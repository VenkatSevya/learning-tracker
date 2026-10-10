import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// "npm run dev" forwards /api calls to the API on your own machine.
// In Docker, Nginx does that job instead.
export default defineConfig({
  plugins: [react()],
  server: { proxy: { "/api": "http://localhost:8000" } },
});
