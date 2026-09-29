/**
 * REEL レンダラ：HTML（window.__duration / window.__seek(t)）→ MP4
 * 画面録画ではなく「時刻を送ってから1枚撮る」＝コマ落ちなし・何度撮っても同じ絵。
 * 元＝~/projects/video-lab/scripts/render.mjs（60fps・?render・一時フレームを /tmp に）
 *
 *   node reel/scripts/render.mjs <作品フォルダ>   → <作品フォルダ>/reel.mp4 と poster.jpg
 */
import { chromium } from 'playwright';
import { mkdirSync, rmSync, statSync } from 'node:fs';
import { execFileSync } from 'node:child_process';
import path from 'node:path';
import os from 'node:os';

const dir = path.resolve(process.argv[2] || '.');
const W = 1920, H = 1080, FPS = 60;
const FR = path.join(os.tmpdir(), 'reel-frames-' + path.basename(dir));
rmSync(FR, { recursive: true, force: true }); mkdirSync(FR, { recursive: true });

const browser = await chromium.launch({ args: ['--enable-gpu-rasterization', '--ignore-gpu-blocklist'] });
const page = await browser.newPage({ viewport: { width: W, height: H }, deviceScaleFactor: 1 });
let errors = 0;
page.on('pageerror', e => { console.error('[pageerror]', e.message); errors++; });
page.on('console', m => { if (m.type() === 'error') { console.error('[console]', m.text()); errors++; } });
await page.goto('file://' + path.join(dir, 'source.html') + '?render', { waitUntil: 'load' });
await page.waitForFunction(() => typeof window.__seek === 'function' && typeof window.__duration === 'number', null, { timeout: 30000 });
await page.evaluate(() => document.fonts.ready);
await page.waitForTimeout(500);
const dur = await page.evaluate(() => window.__duration);
if (Math.abs(dur - 15) > 1e-6) { console.error(`__duration must be 15 (got ${dur})`); process.exit(2); }
const total = Math.round(dur * FPS);
const t0 = Date.now();
for (let i = 0; i < total; i++) {
  await page.evaluate(async t => { await window.__seek(t); }, i / FPS);
  await page.screenshot({ path: path.join(FR, String(i).padStart(5, '0') + '.png') });
  if (i % 60 === 0) process.stdout.write(`\r  ${i}/${total}`);
}
process.stdout.write(`\r  ${total}/${total}  (${((Date.now() - t0) / 1000).toFixed(0)}s)\n`);
await browser.close();
if (errors) { console.error(`🔴 page errors: ${errors}`); process.exit(3); }

// 書き出し：8MB を超えたら crf を上げて撮り直す（配信先 GitHub Pages の容量を守る）
const out = path.join(dir, 'reel.mp4');
for (const crf of [20, 23, 26, 29]) {
  execFileSync('ffmpeg', ['-y', '-v', 'error', '-framerate', String(FPS), '-i', path.join(FR, '%05d.png'),
    '-c:v', 'libx264', '-preset', 'slow', '-crf', String(crf), '-pix_fmt', 'yuv420p', '-movflags', '+faststart', out]);
  const mb = statSync(out).size / 1e6;
  console.log(`  crf ${crf}: ${mb.toFixed(2)} MB`);
  if (mb <= 8) break;
}
// ポスター＝一番「その作品らしい」1枚を HTML 側が window.__poster で指定（無ければ 40%地点）
execFileSync('ffmpeg', ['-y', '-v', 'error', '-ss', String(await posterTime()), '-i', out, '-frames:v', '1', '-q:v', '3', path.join(dir, 'poster.jpg')]);
// コンタクトシート（1秒ごと15枚・点検と自己レビュー用）
execFileSync('ffmpeg', ['-y', '-v', 'error', '-i', out, '-vf', 'fps=1,scale=384:-1,tile=5x3', '-frames:v', '1', '-q:v', '4', path.join(dir, 'contact.jpg')]);
rmSync(FR, { recursive: true, force: true });
console.log(out);

async function posterTime() {
  const b = await chromium.launch(); const p = await b.newPage();
  await p.goto('file://' + path.join(dir, 'source.html') + '?render');
  const v = await p.evaluate(() => typeof window.__poster === 'number' ? window.__poster : 6);
  await b.close(); return Math.min(14.9, Math.max(0, v));
}
