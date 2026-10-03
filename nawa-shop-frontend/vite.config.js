import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],

  server: {
    port: 5173,
    proxy: {
      // === Proxy API → Django ===
      "/api": {
        target: "http://localhost:8000",
        changeOrigin: false,
        secure: false,
        cookieDomainRewrite: "localhost",
      },
      // === Proxy média (images uploadées) ===
      "/media": {
        target: "http://localhost:8000",
        changeOrigin: false,
        secure: false,
      },
      // === Proxy statiques Django ===
      "/static": {
        target: "http://localhost:8000",
        changeOrigin: false,
        secure: false,
      },
      // === Proxy admin Django (optionnel, pour /admin) ===
      "/admin": {
        target: "http://localhost:8000",
        changeOrigin: false,
        secure: false,
      },
    },
  },

  build: {
    outDir: "dist",
    sourcemap: false,
    minify: "esbuild",
    target: "es2020",
    chunkSizeWarningLimit: 800,
    rollupOptions: {
      output: {
        manualChunks: {
          "react-vendor": ["react", "react-dom", "react-router-dom"],
          "puck-vendor": ["@puckeditor/core"],
          "vendor": ["axios"],
        },
        chunkFileNames: "assets/[name]-[hash].js",
        entryFileNames: "assets/[name]-[hash].js",
        assetFileNames: "assets/[name]-[hash].[ext]",
      },
    },
    cssCodeSplit: true,
    assetsInlineLimit: 4096,
  },

  optimizeDeps: {
    include: ["react", "react-dom", "react-router-dom", "axios"],
  },

});