import { fileURLToPath } from 'node:url'
import { mergeConfig, defineConfig, configDefaults } from 'vitest/config'
import viteConfigFn from './vite.config'

// vite.config.ts 是函数式配置（defineConfig(({ mode }) => ...)），
// mergeConfig 只接受对象，故以 test 模式求值后再合并（与 vitest 内部行为一致）
const viteConfig = viteConfigFn({ mode: 'test', command: 'serve' })

export default mergeConfig(
  viteConfig,
  defineConfig({
    test: {
      environment: 'jsdom',
      exclude: [...configDefaults.exclude, 'e2e/**'],
      root: fileURLToPath(new URL('./', import.meta.url)),
    },
  }),
)
