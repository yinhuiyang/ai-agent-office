import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";

export default defineConfig({
  plugins: [vue()],
  server: {
    port: 19000
  },
  resolve: {
    alias: {
      "@": "/src"
    }
  }
});
