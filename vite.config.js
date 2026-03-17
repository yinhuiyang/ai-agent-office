/*
 * @Author: yinhuiyang 1061929244@qq.com
 * @Date: 2026-03-16 13:45:16
 * @LastEditors: yinhuiyang 1061929244@qq.com
 * @LastEditTime: 2026-03-16 19:05:47
 * @FilePath: /ai-agent-office/vite.config.js
 * @Description: 这是默认设置,请设置`customMade`, 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
 */
import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";

export default defineConfig({
  plugins: [vue()],
  server: {
    port: 19000,
    host: "0.0.0.0"
  },
  resolve: {
    alias: {
      "@": "/src"
    }
  }
});
