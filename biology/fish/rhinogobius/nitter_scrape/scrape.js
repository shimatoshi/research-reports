#!/usr/bin/env node
// Scrape nitter.tiekoetter.com for Rhinogobius-related tweets, profiles, and images.
// Uses node https + cheerio. No browser needed.

const https = require('https');
const http  = require('http');
const fs    = require('fs');
const path  = require('path');
const cheerio = require('cheerio');

const INSTANCE = 'https://nitter.tiekoetter.com';
const OUT_DIR  = '/tmp/yoshi_out';
const IMG_DIR  = path.join(OUT_DIR, 'images');
const JSONL    = path.join(OUT_DIR, 'tweets.jsonl');
const USERS    = path.join(OUT_DIR, 'users.jsonl');
const ERR      = path.join(OUT_DIR, 'err.log');

fs.mkdirSync(IMG_DIR, { recursive: true });

const HEADERS = {
  'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36',
  'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
  'Accept-Language': 'ja,en;q=0.9',
  'Accept-Encoding': 'gzip, deflate, br',
  'sec-ch-ua': '"Chromium";v="147", "Not A(Brand";v="99"',
  'sec-ch-ua-mobile': '?0',
  'sec-ch-ua-platform': '"Linux"',
  'sec-fetch-dest': 'document',
  'sec-fetch-mode': 'navigate',
  'sec-fetch-site': 'none',
  'upgrade-insecure-requests': '1',
};

function fetch(url, opts = {}) {
  return new Promise((resolve, reject) => {
    const u = new URL(url);
    const lib = u.protocol === 'https:' ? https : http;
    const req = lib.request(u, { method: opts.method || 'GET', headers: { ...HEADERS, ...(opts.headers||{}) } }, (res) => {
      if ([301, 302, 303, 307, 308].includes(res.statusCode) && res.headers.location) {
        const loc = res.headers.location.startsWith('http') ? res.headers.location : new URL(res.headers.location, url).toString();
        res.resume();
        return fetch(loc, opts).then(resolve, reject);
      }
      const chunks = [];
      let stream = res;
      const enc = res.headers['content-encoding'];
      if (enc === 'gzip') stream = res.pipe(require('zlib').createGunzip());
      else if (enc === 'deflate') stream = res.pipe(require('zlib').createInflate());
      else if (enc === 'br') stream = res.pipe(require('zlib').createBrotliDecompress());
      stream.on('data', c => chunks.push(c));
      stream.on('end', () => resolve({ statusCode: res.statusCode, headers: res.headers, body: Buffer.concat(chunks) }));
      stream.on('error', reject);
    });
    req.on('error', reject);
    req.setTimeout(20000, () => { req.destroy(new Error('timeout')); });
    req.end();
  });
}

function logErr(tag, e) {
  fs.appendFileSync(ERR, `[${new Date().toISOString()}] ${tag}: ${e && e.stack || e}\n`);
}

function parseTweets(html) {
  const $ = cheerio.load(html);
  const rows = [];
  $('.timeline-item').each((_, el) => {
    const $i = $(el);
    if ($i.hasClass('show-more')) return;
    const username = ($i.attr('data-username') || '').trim();
    const fullname = $i.find('.fullname').attr('title') || '';
    const dateA = $i.find('.tweet-date a').first();
    const date_iso = dateA.attr('title') || '';
    const date_rel = dateA.text().trim();
    const tweetLink = $i.find('a.tweet-link').attr('href') || '';
    const m = tweetLink.match(/\/([^/]+)\/status\/(\d+)/);
    const tweet_id = m ? m[2] : '';
    const replying = $i.find('.replying-to').text().trim();
    const retweet_header = $i.find('.retweet-header').text().trim();
    const text = $i.find('.tweet-content').first().text().trim();
    const images_orig = $i.find('.attachments a.still-image').map((_, a) => $(a).attr('href') || '').get().filter(Boolean);
    const images_thumb = $i.find('.attachments .attachment img').map((_, e) => $(e).attr('src') || '').get().filter(Boolean);
    const videos = $i.find('.attachments video source, .attachments video').map((_, e) => $(e).attr('src') || '').get().filter(Boolean);
    const quote_user = $i.find('.quote .username').text().trim();
    const quote_text = $i.find('.quote .quote-text').text().trim();
    const stats = {};
    $i.find('.tweet-stats .tweet-stat').each((_, s) => {
      const $s = $(s);
      const iconEl = $s.find('.icon-container [class*="icon-"]').first();
      if (!iconEl.length) return;
      const cls = (iconEl.attr('class') || '').split(/\s+/).find(c => c.startsWith('icon-'));
      if (cls) stats[cls] = $s.text().trim();
    });
    rows.push({ username, fullname, tweet_id, tweet_link: tweetLink, date_iso, date_rel,
                replying_to: replying, retweet_header, text,
                images_orig, images_thumb, videos,
                quote_user, quote_text, stats });
  });
  const more = $('.show-more a').attr('href') || '';
  const timelineEnd = $('.timeline-end').text().trim();
  return { rows, more, timelineEnd };
}

function parseProfile(html) {
  const $ = cheerio.load(html);
  return {
    name:       $('.profile-card-fullname').first().text().trim(),
    handle:     $('.profile-card-username').first().text().trim(),
    loc:        $('.profile-location').first().text().trim(),
    website:    $('.profile-website a').first().attr('href') || '',
    bio:        $('.profile-bio').first().text().trim(),
    joined:     $('.profile-joindate').first().attr('title') || '',
    tweets:     $('.profile-statlist .posts .profile-stat-num').first().text().trim(),
    following:  $('.profile-statlist .following .profile-stat-num').first().text().trim(),
    followers:  $('.profile-statlist .followers .profile-stat-num').first().text().trim(),
  };
}

async function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }

async function scrapeKeyword(kw, label, maxPages = 15) {
  let url = `${INSTANCE}/search?f=tweets&q=${encodeURIComponent(kw)}`;
  let added = 0;
  for (let p = 1; p <= maxPages; p++) {
    let resp;
    try { resp = await fetch(url); } catch (e) { logErr(`${label} p${p} fetch`, e); break; }
    if (resp.statusCode !== 200) {
      console.error(`[${label}] p${p} status=${resp.statusCode} — stop`);
      break;
    }
    const html = resp.body.toString('utf8');
    const { rows, more, timelineEnd } = parseTweets(html);
    for (const r of rows) { r.kw = label; fs.appendFileSync(JSONL, JSON.stringify(r) + '\n'); }
    added += rows.length;
    console.error(`[${label}] p${p} rows=${rows.length} more=${more ? 'Y' : 'N'}${timelineEnd ? ' END' : ''}`);
    if (!more || rows.length === 0) break;
    url = INSTANCE + more;
    await sleep(1500);
  }
  return added;
}

async function scrapeProfile(username) {
  const url = `${INSTANCE}/${encodeURIComponent(username)}`;
  try {
    const r = await fetch(url);
    if (r.statusCode !== 200) return { username, err: `status ${r.statusCode}` };
    const p = parseProfile(r.body.toString('utf8'));
    p.username = username;
    return p;
  } catch (e) { logErr(`profile ${username}`, e); return { username, err: e.message }; }
}

async function downloadImage(url, outPath) {
  try {
    const r = await fetch(url, { headers: { 'Referer': INSTANCE + '/' } });
    if (r.statusCode !== 200) return false;
    fs.writeFileSync(outPath, r.body);
    return true;
  } catch (e) { logErr(`img ${url}`, e); return false; }
}

function loadJsonl(p) {
  if (!fs.existsSync(p)) return [];
  return fs.readFileSync(p, 'utf8').split('\n').filter(Boolean).map(l => { try { return JSON.parse(l); } catch { return null; } }).filter(Boolean);
}

(async () => {
  const mode = process.argv[2] || 'all';

  if (mode === 'all' || mode === 'scrape') {
    // Reset tweets if fresh scrape requested
    if (process.argv.includes('--fresh')) { fs.writeFileSync(JSONL, ''); }

    const keywords = [
      ['ヨシノボリ',        'yoshinobori_kata',  15],
      ['よしのぼり',        'yoshinobori_hira',  8],
      ['Rhinogobius',       'rhinogobius_en',    8],
      ['オオヨシノボリ',    'ooyoshinobori',     10],
      ['カワヨシノボリ',    'kawayoshinobori',   10],
      ['シマヨシノボリ',    'shimayoshinobori',  10],
      ['クロヨシノボリ',    'kuroyoshinobori',   10],
      ['ルリヨシノボリ',    'ruriyoshinobori',   10],
      ['トウヨシノボリ',    'touyoshinobori',    10],
      ['カジカヨシノボリ',  'kajikayoshinobori', 5],
      ['ゴクラクハゼ',      'gokurakuhaze',      5],
      ['ヒラヨシノボリ',    'hirayoshinobori',   5],
      ['アオバラヨシノボリ','aobarayoshinobori', 5],
      ['アヤヨシノボリ',    'ayayoshinobori',    5],
      ['ヨシノボリ属',      'yoshinobori_genus', 5],
    ];
    for (const [kw, label, pg] of keywords) {
      await scrapeKeyword(kw, label, pg);
      await sleep(1500);
    }
    // Dedup
    const raw = loadJsonl(JSONL);
    const seen = new Set(); const uniq = [];
    for (const t of raw) {
      const key = (t.tweet_id || t.tweet_link) + '|' + (t.username||'');
      if (seen.has(key)) continue;
      seen.add(key); uniq.push(t);
    }
    fs.writeFileSync(JSONL, uniq.map(t => JSON.stringify(t)).join('\n') + '\n');
    console.error(`dedup: ${raw.length} -> ${uniq.length}`);
  }

  if (mode === 'all' || mode === 'profiles') {
    const tweets = loadJsonl(JSONL);
    const already = new Set(loadJsonl(USERS).map(u => u.username));
    const needed = [...new Set(tweets.map(t => t.username).filter(Boolean))].filter(u => !already.has(u));
    console.error(`profiles: have ${already.size}, need ${needed.length}`);
    const CC = 3;
    let idx = 0;
    async function worker() {
      while (idx < needed.length) {
        const u = needed[idx++];
        const p = await scrapeProfile(u);
        fs.appendFileSync(USERS, JSON.stringify(p) + '\n');
        if (idx % 10 === 0) console.error(`profiles: ${idx}/${needed.length}`);
        await sleep(400);
      }
    }
    await Promise.all(Array.from({length: CC}, () => worker()));
  }

  if (mode === 'all' || mode === 'images') {
    const tweets = loadJsonl(JSONL);
    const jobs = [];
    for (const r of tweets) {
      const slug = (r.username || '_') + '_' + (r.tweet_id || 'x');
      const urls = (r.images_orig && r.images_orig.length) ? r.images_orig : (r.images_thumb || []);
      for (let i = 0; i < urls.length; i++) {
        let u = urls[i];
        if (u.startsWith('/')) u = INSTANCE + u;
        const ext = (u.match(/\.(jpg|jpeg|png|gif|webp)/i) || [])[1] || 'jpg';
        const out = path.join(IMG_DIR, `${slug}_${i}.${ext.toLowerCase()}`);
        if (!fs.existsSync(out)) jobs.push({ u, out });
      }
    }
    console.error(`image jobs: ${jobs.length}`);
    const CC = 4;
    let done = 0, ok = 0, idx = 0;
    async function worker() {
      while (idx < jobs.length) {
        const j = jobs[idx++];
        const r = await downloadImage(j.u, j.out);
        done++; if (r) ok++;
        if (done % 25 === 0) console.error(`img: ${done}/${jobs.length} ok=${ok}`);
      }
    }
    await Promise.all(Array.from({length: CC}, () => worker()));
    console.error(`images ok: ${ok}/${jobs.length}`);
  }

  console.error('=== DONE ===');
  console.error('tweets:', loadJsonl(JSONL).length);
  console.error('users:',  loadJsonl(USERS).length);
  console.error('images:', fs.readdirSync(IMG_DIR).length);
})();
