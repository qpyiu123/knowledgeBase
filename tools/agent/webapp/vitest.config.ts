import react from '@vitejs/plugin-react';
import { defineConfig } from 'vitest/config';

export default defineConfig({
  plugins: [react()],
  test: {
    environment: 'jsdom',
    globals: false,
    include: ['src/**/*.test.{ts,tsx}'],
    setupFiles: ['src/test/setup.ts'],
    restoreMocks: true,
    // 本机 Windows 上 fork worker 常因启动超时报错；线程池 + 2 并发稳定。
    pool: 'threads',
    maxWorkers: 2,
  },
});
