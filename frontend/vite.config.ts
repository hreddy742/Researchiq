import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    proxy: {
      "/research": "http://localhost:8010",
      "/health": "http://localhost:8010",
    },
  },
});
