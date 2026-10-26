#!/usr/bin/env node
/**
 * 影盒界面语言的样式检查（独立版，不依赖仓库里的基线文件）。
 *
 * 查 .css 文件和 .vue 的 <style> 块：
 *   - font-size / border-radius / 间距属性里的裸 px（0、1px 除外）
 *   - transition / animation 里的字面时长
 *   - 数字 z-index（0、1、-1 除外）
 *   - 令牌文件以外的颜色字面量（#hex、rgb()、rgba()、hsl()）
 *   - font-weight 不在 400 / 500 / 600 / 令牌里
 * 查 .vue / .jsx / .tsx 模板（组件库目录除外）：
 *   - 原生 <button>、<select>、<textarea>，以及 type 不是 file / range / hidden 的 <input>
 *   - 静态 style="..."（动态 :style 不受限）
 * 同一行写 `style-tokens:` 注释就跳过那一行。
 *
 *   node check-style.mjs --src src --tokens src/styles/tokens.css --ui src/components/ui
 *
 * 有违规时退出码为 1。
 */
import { readdirSync, readFileSync, statSync } from 'node:fs'
import path from 'node:path'

/** 读命令行参数 --name value */
function arg(name, fallback) {
  const i = process.argv.indexOf(`--${name}`)
  return i > -1 && process.argv[i + 1] ? process.argv[i + 1] : fallback
}

const srcDir = path.resolve(arg('src', 'src'))
const tokensFile = path.resolve(arg('tokens', path.join(srcDir, 'styles/tokens.css')))
const uiDir = path.resolve(arg('ui', path.join(srcDir, 'components/ui'))) + path.sep
const SKIP_DIRS = new Set(['node_modules', 'dist', 'out', '.git'])

const SPACING =
  /^(padding|margin|gap|row-gap|column-gap|inset|top|right|bottom|left)(-(top|right|bottom|left|inline|block)(-(start|end))?)?$/
const RAW_PX = /(?<![\w.-])(\d*\.?\d+)px/g
const COLOR = /#[0-9a-fA-F]{3,8}\b|\b(rgba?|hsla?)\(/
// 0 和 0.01ms（减少动态效果时的全局归零写法）放过
const DURATION = /(?<![\w.-])(?!0?\.01ms\b|0m?s\b)\d*\.?\d+m?s\b/

/** 列出目录下所有文件 */
function walk(dir, out = []) {
  for (const name of readdirSync(dir)) {
    if (SKIP_DIRS.has(name)) continue
    const full = path.join(dir, name)
    if (statSync(full).isDirectory()) walk(full, out)
    else out.push(full)
  }
  return out
}

/** 一行声明里不合规的 px（0 和 1px 发丝线放过） */
function rawPx(value) {
  return [...value.matchAll(RAW_PX)].filter(m => Number(m[1]) > 1)
}

/** 检查一行 CSS 声明，返回问题说明列表 */
function checkDeclaration(line, isTokens) {
  const m = line.match(/^\s*([a-z-]+)\s*:\s*(.+?);?\s*$/)
  if (!m || m[1].startsWith('--')) return []
  const [, prop, value] = m
  const found = []
  if ((prop === 'font-size' || prop === 'border-radius') && rawPx(value).length)
    found.push(`${prop} 用了裸 px，改用 ${prop === "font-size" ? "--text-*" : "--radius-*"}`)
  if (SPACING.test(prop) && !value.includes('var(') && rawPx(value).length)
    found.push(`${prop} 用了裸 px，改用 --space-*`)
  if (/^(transition|animation)(-duration|-delay)?$/.test(prop) && DURATION.test(value.replace(/var\([^)]*\)/g, '')))
    found.push(`${prop} 写了字面时长，改用 --duration-*`)
  if (prop === 'z-index' && /^-?\d+$/.test(value.trim()) && !['0', '1', '-1'].includes(value.trim()))
    found.push('z-index 写了数字，改用 --z-*')
  if (prop === 'font-weight' && /^\d+$/.test(value.trim()) && !['400', '500', '600'].includes(value.trim()))
    found.push(`font-weight ${value.trim()} 不在 400 / 500 / 600 里`)
  if (!isTokens && COLOR.test(value))
    found.push(`${prop} 写了颜色字面量，改用颜色令牌`)
  return found
}

/** 检查一段 CSS 文本，startLine 是它在文件里的起始行号；一行可以有多条声明 */
function checkCss(text, startLine, isTokens) {
  const out = []
  text.split('\n').forEach((line, i) => {
    if (line.includes('style-tokens:')) return
    const clean = line.replace(/\/\*.*?\*\//g, '').replace(/^[^{]*\{/, '').replace(/\}.*$/, '')
    for (const decl of clean.split(';'))
      for (const msg of checkDeclaration(decl, isTokens)) out.push([startLine + i, msg])
  })
  return out
}

/** 检查模板文本里的原生控件和静态 style（标签可以跨行） */
function checkTemplate(text, startLine) {
  const out = []
  const lines = text.split('\n')
  const lineOf = index => text.slice(0, index).split('\n').length - 1
  const exempt = i => lines[i]?.includes('style-tokens:')
  for (const m of text.matchAll(/<(button|select|textarea|input)\b[^>]*>/g)) {
    const i = lineOf(m.index)
    if (exempt(i)) continue
    if (m[1] === 'input' && /type=["'](file|range|hidden)["']/.test(m[0])) continue
    out.push([startLine + i, `手写了原生 <${m[1]}>，改用组件库里的对应组件`])
  }
  for (const m of text.matchAll(/(?<![:\w-])style=["']/g)) {
    const i = lineOf(m.index)
    if (!exempt(i)) out.push([startLine + i, '静态 style="..."，改用类名和令牌'])
  }
  return out.sort((x, y) => x[0] - y[0])
}

/** 取出 .vue 文件里的某类块及其起始行号 */
function blocks(text, tag) {
  // 模板里会嵌套 <template>，取第一个开标签到最后一个闭标签；style 块不嵌套，逐个取
  const lazy = tag === 'template' ? '' : '?'
  const re = new RegExp(`<${tag}[^>]*>([\\s\\S]*${lazy})</${tag}>`, 'g')
  return [...text.matchAll(re)].map(m => ({
    body: m[1],
    line: text.slice(0, m.index + m[0].indexOf(m[1])).split('\n').length,
  }))
}

const problems = []
for (const file of walk(srcDir)) {
  const ext = path.extname(file)
  if (!['.css', '.vue', '.jsx', '.tsx'].includes(ext)) continue
  const text = readFileSync(file, 'utf8')
  const inUi = file.startsWith(uiDir)
  const isTokens = file === tokensFile
  const add = list => list.forEach(([line, msg]) => problems.push(`${path.relative(process.cwd(), file)}:${line}  ${msg}`))
  if (ext === '.css') add(checkCss(text, 1, isTokens))
  if (ext === '.vue') {
    for (const b of blocks(text, 'style')) add(checkCss(b.body, b.line, false))
    if (!inUi) for (const b of blocks(text, 'template')) add(checkTemplate(b.body, b.line))
  }
  if ((ext === '.jsx' || ext === '.tsx') && !inUi) add(checkTemplate(text, 1))
}

if (problems.length) {
  console.log(problems.join('\n'))
  console.log(`\n${problems.length} 处不合规。同一行写 style-tokens: 注释可豁免。`)
  process.exit(1)
}
console.log('样式检查通过')
