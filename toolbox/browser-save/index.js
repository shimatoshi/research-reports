#!/usr/bin/env node
/**
 * browser-save.js — 永続Chromiumでページをシングルファイル保存
 *
 * 使い方:
 *   node browser-save.js <url> <output-path>
 *   node browser-save.js --server <port>    # サーバーモード（ブラウザ起動しっぱなし）
 *
 * サーバーモード: HTTP経由でリクエストを受け、ブラウザを使い回す
 *   POST http://localhost:<port>/save  { "url": "...", "output": "..." }
 *   POST http://localhost:<port>/quit
 */

const puppeteer = require('puppeteer');
const http = require('http');
const fs = require('fs');
const path = require('path');

const BROWSER_ARGS = [
  '--no-sandbox',
  '--disable-gpu',
  '--disable-dev-shm-usage',
  '--disable-extensions',
  '--disable-background-networking',
  '--disable-sync',
  '--disable-translate',
  '--no-first-run',
  '--disable-features=TranslateUI',
];

// ページを開いてDOM+リソースをインライン化したHTMLを返す
async function savePage(browser, url, timeoutMs = 30000) {
  const page = await browser.newPage();
  try {
    await page.setUserAgent(
      'Mozilla/5.0 (Linux; Android 11; Pixel 5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36'
    );

    await page.goto(url, {
      waitUntil: 'networkidle2',
      timeout: timeoutMs,
    });

    // ブラウザ内でDOM+リソースをインライン化
    const html = await page.evaluate(inlinePage);
    return html;
  } finally {
    await page.close();
  }
}

// ブラウザコンテキスト内で実行: リソースをインライン化
async function inlinePage() {
  const MAX_IMG_SIZE = 2 * 1024 * 1024; // 2MB

  // 1. 画像 → data URI (canvasから。既にデコード済みなので追加リクエストなし)
  const imgs = document.querySelectorAll('img');
  for (const img of imgs) {
    if (!img.src || img.src.startsWith('data:') || !img.naturalWidth) continue;
    try {
      const canvas = document.createElement('canvas');
      canvas.width = img.naturalWidth;
      canvas.height = img.naturalHeight;
      const ctx = canvas.getContext('2d');
      ctx.drawImage(img, 0, 0);
      // サイズチェック (data URI の概算)
      const dataUri = canvas.toDataURL('image/png');
      if (dataUri.length < MAX_IMG_SIZE * 1.37) { // base64は約1.37倍
        img.src = dataUri;
      }
    } catch (e) {
      // cross-origin → スキップ
    }
    img.removeAttribute('srcset');
    img.removeAttribute('loading');
  }

  // 2. <link stylesheet> → <style> (CSSOMから取得。追加リクエストなし)
  const links = document.querySelectorAll('link[rel="stylesheet"]');
  for (const link of links) {
    try {
      // CSSOMから取得を試みる
      let cssText = '';
      for (const sheet of document.styleSheets) {
        if (sheet.href === link.href || sheet.ownerNode === link) {
          try {
            const rules = sheet.cssRules || sheet.rules;
            for (const rule of rules) {
              cssText += rule.cssText + '\n';
            }
          } catch (e) {
            // cross-origin stylesheet → fetchで取得 (キャッシュから)
            try {
              const resp = await fetch(link.href, { cache: 'force-cache' });
              cssText = await resp.text();
            } catch (e2) {
              continue;
            }
          }
          break;
        }
      }
      if (cssText) {
        const style = document.createElement('style');
        style.textContent = cssText;
        link.replaceWith(style);
      }
    } catch (e) {
      // skip
    }
  }

  // 3. background-image の url() → data URI (fetch from cache)
  // 重いので<style>タグ内のみ、inline styleは省略
  for (const style of document.querySelectorAll('style')) {
    if (!style.textContent.includes('url(')) continue;
    style.textContent = await resolveUrlsInCss(style.textContent);
  }

  // 4. 不要な要素削除
  document.querySelectorAll('script, noscript, iframe[src*="ads"], iframe[src*="tracking"]')
    .forEach(el => el.remove());

  // 5. metaタグ追加
  let meta = document.querySelector('meta[charset]');
  if (!meta) {
    meta = document.createElement('meta');
    meta.setAttribute('charset', 'utf-8');
    const head = document.querySelector('head');
    if (head) head.prepend(meta);
  }

  return '<!DOCTYPE html>\n' + document.documentElement.outerHTML;
}

// CSS内のurl()をdata URIに変換（ブラウザキャッシュから）
async function resolveUrlsInCss(css) {
  const urlRegex = /url\(["']?(?!data:)([^"')]+)["']?\)/g;
  const matches = [...css.matchAll(urlRegex)];
  if (matches.length === 0) return css;

  // 最大20個まで
  const limited = matches.slice(0, 20);
  for (const match of limited) {
    try {
      const resp = await fetch(match[1], { cache: 'force-cache' });
      const blob = await resp.blob();
      if (blob.size > 2 * 1024 * 1024) continue; // 2MB超スキップ
      const reader = new FileReader();
      const dataUri = await new Promise((resolve) => {
        reader.onloadend = () => resolve(reader.result);
        reader.readAsDataURL(blob);
      });
      css = css.replace(match[0], `url(${dataUri})`);
    } catch (e) {
      // skip
    }
  }
  return css;
}


// === サーバーモード ===

async function runServer(port) {
  console.log(`Launching browser...`);
  const browser = await puppeteer.launch({
    headless: 'new',
    args: BROWSER_ARGS,
  });
  console.log(`Browser ready. Server on port ${port}`);

  const server = http.createServer(async (req, res) => {
    // CORS
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
    if (req.method === 'OPTIONS') { res.writeHead(200); res.end(); return; }

    if (req.method !== 'POST') {
      res.writeHead(405); res.end('Method Not Allowed'); return;
    }

    let body = '';
    for await (const chunk of req) body += chunk;

    try {
      const data = JSON.parse(body);

      if (req.url === '/quit') {
        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ ok: true }));
        await browser.close();
        server.close();
        process.exit(0);
        return;
      }

      if (req.url === '/save') {
        const { url, output, timeout } = data;
        if (!url || !output) {
          res.writeHead(400, { 'Content-Type': 'application/json' });
          res.end(JSON.stringify({ error: 'url and output required' }));
          return;
        }

        try {
          const html = await savePage(browser, url, timeout || 30000);
          // ディレクトリ作成
          fs.mkdirSync(path.dirname(output), { recursive: true });
          fs.writeFileSync(output, html, 'utf-8');
          res.writeHead(200, { 'Content-Type': 'application/json' });
          res.end(JSON.stringify({ ok: true, size: html.length }));
        } catch (e) {
          res.writeHead(500, { 'Content-Type': 'application/json' });
          res.end(JSON.stringify({ error: e.message }));
        }
        return;
      }

      res.writeHead(404); res.end('Not Found');
    } catch (e) {
      res.writeHead(400, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ error: 'Invalid JSON' }));
    }
  });

  server.listen(port, '127.0.0.1');
}


// === ワンショットモード ===

async function runOnce(url, outputPath) {
  const browser = await puppeteer.launch({
    headless: 'new',
    args: BROWSER_ARGS,
  });
  try {
    const html = await savePage(browser, url);
    fs.mkdirSync(path.dirname(outputPath), { recursive: true });
    fs.writeFileSync(outputPath, html, 'utf-8');
    console.log(`Saved: ${outputPath} (${html.length} bytes)`);
  } finally {
    await browser.close();
  }
}


// === エントリポイント ===

const args = process.argv.slice(2);

if (args[0] === '--server') {
  const port = parseInt(args[1]) || 3100;
  runServer(port).catch(e => { console.error(e); process.exit(1); });
} else if (args.length >= 2) {
  runOnce(args[0], args[1]).catch(e => { console.error(e); process.exit(1); });
} else {
  console.log('Usage:');
  console.log('  node browser-save.js <url> <output-path>');
  console.log('  node browser-save.js --server <port>');
  process.exit(1);
}
