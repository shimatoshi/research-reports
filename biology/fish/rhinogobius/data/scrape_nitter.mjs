import { chromium } from 'playwright';

const QUERIES = [
  'クロダハゼ',
  'クロダハゼ 採集',
  'トウヨシノボリ 採集',
  'トウヨシノボリ 橙色',
  'カズサヨシノボリ',
  'オウミヨシノボリ',
  'ヨシノボリ 関東 池',
  'ヨシノボリ ため池',
];

const BASE = 'https://nitter.net';
const allResults = [];

const browser = await chromium.launch({
  headless: false,
  args: ['--disable-blink-features=AutomationControlled', '--no-sandbox'],
});
const context = await browser.newContext({
  userAgent: 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
  viewport: { width: 1920, height: 1080 },
  locale: 'ja-JP',
  extraHTTPHeaders: { 'Accept-Language': 'ja,en;q=0.9' },
});
await context.addInitScript(() => {
  Object.defineProperty(navigator, 'webdriver', { get: () => false });
});

for (const query of QUERIES) {
  console.error(`[searching] ${query}`);
  const page = await context.newPage();
  try {
    const url = `${BASE}/search?f=tweets&q=${encodeURIComponent(query)}`;
    await page.goto(url, { waitUntil: 'networkidle', timeout: 30000 });
    await page.waitForTimeout(2000);

    const tweets = await page.$$eval('.timeline-item', items =>
      items.map(item => {
        const username = item.querySelector('.username')?.textContent?.trim() || '';
        const fullname = item.querySelector('.fullname')?.textContent?.trim() || '';
        const date = item.querySelector('.tweet-date a')?.getAttribute('title') ||
                     item.querySelector('.tweet-date a')?.textContent?.trim() || '';
        const text = item.querySelector('.tweet-content')?.textContent?.trim() || '';
        const images = [...item.querySelectorAll('.still-image')]
          .map(a => a.getAttribute('href') || '');
        const link = item.querySelector('.tweet-link')?.getAttribute('href') || '';
        return { username, fullname, date, text, images, link };
      })
    );

    for (const t of tweets) {
      if (t.text) allResults.push({ query, ...t });
    }
    console.error(`  -> ${tweets.filter(t => t.text).length} tweets`);
  } catch (e) {
    console.error(`  -> ERROR: ${e.message}`);
  } finally {
    await page.close();
  }
  // Be polite
  await new Promise(r => setTimeout(r, 1500));
}

await browser.close();

// Deduplicate by link
const seen = new Set();
const unique = allResults.filter(r => {
  if (seen.has(r.link)) return false;
  seen.add(r.link);
  return true;
});

console.log(JSON.stringify(unique, null, 2));
console.error(`\n=== Total: ${unique.length} unique tweets ===`);
