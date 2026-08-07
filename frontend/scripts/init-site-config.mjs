/**
 * 站点配置初始化脚本
 *
 * 用途：确保 `public/site.config.json` 存在（该文件已被 .gitignore，不入仓库）。
 * 不存在时从 `public/site.config.example.json`（模板，入库）复制生成，
 * 供部署用户在 dev / build 后直接编辑，实现站点配置的本地文件覆盖。
 *
 * 用法：`npm run config:init`（在 frontend/ 目录下执行）
 * 说明：跨平台（Windows / macOS / Linux 均可运行），仅依赖 node 内置模块。
 */
import { copyFileSync, existsSync, mkdirSync } from 'node:fs'
import { dirname, join } from 'node:path'
import { fileURLToPath } from 'node:url'

// 当前脚本所在目录（scripts/），项目根目录为上一级
const scriptDir = dirname(fileURLToPath(import.meta.url))
const projectRoot = join(scriptDir, '..')

// public 目录与目标 / 模板文件路径
const publicDir = join(projectRoot, 'public')
const targetPath = join(publicDir, 'site.config.json')
const templatePath = join(publicDir, 'site.config.example.json')

// 确保 public 目录存在（不存在则递归创建）
mkdirSync(publicDir, { recursive: true })

if (existsSync(targetPath)) {
  // 已存在：无需覆盖，直接提示（避免误覆盖用户的已编辑配置）
  console.log('[站点配置] public/site.config.json 已存在，跳过生成。如需重置请删除该文件后重试。')
} else {
  // 不存在：从模板复制生成
  copyFileSync(templatePath, targetPath)
  console.log('[站点配置] 已从模板生成 public/site.config.json，可编辑该文件覆盖站点配置（字段参考 site.config.example.json）。')
}
