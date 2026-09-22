// MIDDLE STUDIES II — 基準の作品を手元に撮る（2026-09-23）
//
//   node ii/scripts/ref.mjs <URL> <出力.png> [--full] [--w 1440] [--h 900]
//
// 画像URL（.jpg/.png/.webp）ならそのまま落とす。ページURLなら 1440×900 で撮る（--full で全編）。
// 🔴 撮ったものは ii/refs/（.gitignore 済み）に置く。**他人の作品を public リポジトリに上げない。**
//    リポジトリに残すのは URL だけ（SOURCES.md・works.json の source）。
// playwright はこのリポジトリに入れず、video-lab の node_modules を借りる（Drive外・launchdから読める）。
import { createRequire } from 'node:module'
import { writeFileSync, mkdirSync } from 'node:fs'
import { dirname } from 'node:path'
import { homedir } from 'node:os'

const [url, out, ...rest] = process.argv.slice(2)
if (!url || !out) { console.error('usage: node ref.mjs <URL> <out.png> [--full]'); process.exit(2) }
const opt = (k, d) => { const i = rest.indexOf(k); return i >= 0 ? Number(rest[i + 1]) : d }
mkdirSync(dirname(out), { recursive: true })

if (/\.(jpe?g|png|webp|avif)(\?|$)/i.test(url)) {
  const r = await fetch(url, { headers: { 'user-agent': 'Mozilla/5.0' } })
  if (!r.ok) { console.error(`🔴 ${r.status} ${url}`); process.exit(1) }
  writeFileSync(out, Buffer.from(await r.arrayBuffer()))
  console.log(`>> saved image ${out}`)
  process.exit(0)
}

const require = createRequire(`${homedir()}/projects/video-lab/package.json`)
const { chromium } = require('playwright')
const browser = await chromium.launch()
const page = await browser.newPage({ viewport: { width: opt('--w', 1440), height: opt('--h', 900) } })
try {
  await page.goto(url, { waitUntil: 'networkidle', timeout: 45000 })
} catch { await page.goto(url, { waitUntil: 'load', timeout: 45000 }).catch(() => {}) }
await page.waitForTimeout(3500)   // プリローダー・フェードイン待ち（26%はプリローダー＝reference_preloader_blank_shot）
await page.screenshot({ path: out, fullPage: rest.includes('--full') })
// og:image も拾っておく（作品ページは本体画像がこれのことが多い）
const og = await page.$eval('meta[property="og:image"]', m => m.content).catch(() => null)
await browser.close()
console.log(`>> saved page ${out}${og ? `\n>> og:image ${og}` : ''}`)
