#!/bin/bash
# Resume Chromium-based search scraping. Restarts chromium per keyword to avoid LMK.
set -u

INSTANCE="https://nitter.tiekoetter.com"
OUT_DIR=/tmp/yoshi_out
JSONL=$OUT_DIR/tweets.jsonl
ERR=$OUT_DIR/err_search.log
mkdir -p "$OUT_DIR"
: >"$ERR"

EXTRACT='(() => {
  const items = Array.from(document.querySelectorAll(".timeline-item"));
  const rows = items.filter(i => !i.classList.contains("show-more")).map(i => {
    const username = (i.getAttribute("data-username") || "").trim();
    const fullname = i.querySelector(".fullname")?.getAttribute("title") || "";
    const dateA = i.querySelector(".tweet-date a");
    const date_iso = dateA?.getAttribute("title") || "";
    const date_rel = (dateA?.innerText||"").trim();
    const tweetLink = i.querySelector("a.tweet-link")?.getAttribute("href") || "";
    const m = tweetLink.match(/\/([^/]+)\/status\/(\d+)/);
    const tweet_id = m ? m[2] : "";
    const replying = (i.querySelector(".replying-to")?.innerText||"").trim();
    const retweet_header = (i.querySelector(".retweet-header")?.innerText||"").trim();
    const text = (i.querySelector(".tweet-content")?.innerText||"").trim();
    const images_orig = Array.from(i.querySelectorAll(".attachments a.still-image"))
      .map(a => a.getAttribute("href") || "").filter(Boolean);
    const images_thumb = Array.from(i.querySelectorAll(".attachments .attachment img"))
      .map(img => img.getAttribute("src") || "").filter(Boolean);
    const videos = Array.from(i.querySelectorAll(".attachments video source, .attachments video"))
      .map(v => v.getAttribute("src") || "").filter(Boolean);
    const quote_user = (i.querySelector(".quote .username")?.innerText||"").trim();
    const quote_text = (i.querySelector(".quote .quote-text")?.innerText||"").trim();
    const stats = {};
    i.querySelectorAll(".tweet-stats .tweet-stat").forEach(s => {
      const icon = s.querySelector(".icon-container [class*=icon-]");
      if (!icon) return;
      const cls = Array.from(icon.classList).find(c => c.startsWith("icon-"));
      stats[cls] = s.innerText.trim();
    });
    return { username, fullname, tweet_id, tweet_link: tweetLink, date_iso, date_rel,
             replying_to: replying, retweet_header, text,
             images_orig, images_thumb, videos, quote_user, quote_text, stats };
  });
  const more = document.querySelector(".show-more a")?.getAttribute("href") || "";
  return { rows, more, title: document.title };
})()'

# Already-completed keywords (have records)
EXISTING=$(node -e '
  const fs=require("fs"); const set=new Set();
  fs.readFileSync("/tmp/yoshi_out/tweets.jsonl","utf8").split("\n").filter(Boolean).forEach(l=>{
    try { set.add(JSON.parse(l).kw); } catch(e){}
  });
  console.log([...set].join(","));
')
echo "Already-scraped kws: $EXISTING" >&2

KEYWORDS=(
  "ヨシノボリ|yoshinobori_kata|6"
  "よしのぼり|yoshinobori_hira|4"
  "Rhinogobius|rhinogobius_en|4"
  "オオヨシノボリ|ooyoshinobori|4"
  "カワヨシノボリ|kawayoshinobori|4"
  "シマヨシノボリ|shimayoshinobori|4"
  "クロヨシノボリ|kuroyoshinobori|4"
  "ルリヨシノボリ|ruriyoshinobori|4"
  "トウヨシノボリ|touyoshinobori|4"
  "カジカヨシノボリ|kajikayoshinobori|3"
  "ヒラヨシノボリ|hirayoshinobori|3"
  "アオバラヨシノボリ|aobarayoshinobori|3"
  "アヤヨシノボリ|ayayoshinobori|3"
  "ヨシノボリ属|yoshinobori_genus|3"
)

scrape_one_keyword() {
  local kw="$1" label="$2" max_pages="$3"
  local SESSION="s_$label"

  # Per-keyword chromium boot
  pgrep -x Xvfb | xargs -r kill 2>/dev/null
  pgrep -f "chrome.*--type=" | xargs -r kill -9 2>/dev/null
  sleep 1
  Xvfb :99 -screen 0 800x600x24 >/tmp/xvfb.log 2>&1 &
  sleep 2
  export DISPLAY=:99

  local enc_kw
  enc_kw=$(node -e "console.log(encodeURIComponent(process.argv[1]))" "$kw")
  local url="$INSTANCE/search?f=tweets&q=$enc_kw"

  echo "[$label] booting chromium..." >&2
  playwright-cli --session="$SESSION" --browser=chromium --headed open "$url" >/tmp/pw_open.log 2>&1
  sleep 8

  for ((page=1; page<=max_pages; page++)); do
    if (( page > 1 )); then
      playwright-cli -s "$SESSION" goto "$url" >/tmp/pw_goto.log 2>&1
      sleep 5
    fi
    # Anubis check
    local title
    title=$(playwright-cli -s "$SESSION" --raw eval 'document.title' 2>>"$ERR" | tr -d '"')
    if [[ "$title" == *"ボット"* || "$title" == *"Making sure"* ]]; then
      echo "[$label p$page] anubis, +10s" >&2
      sleep 10
    fi

    local raw next count
    raw=$(playwright-cli -s "$SESSION" --raw eval "$EXTRACT" 2>>"$ERR")
    if [[ -z "$raw" ]]; then echo "[$label p$page] empty raw — stop" >&2; break; fi

    read next count <<<$(printf '%s' "$raw" | node -e '
      let s=""; process.stdin.on("data",d=>s+=d); process.stdin.on("end",()=>{
        try{
          let o = JSON.parse(s);
          if (typeof o === "string") o = JSON.parse(o);
          const fs=require("fs"); const jsonl=process.argv[1], kw=process.argv[2];
          for (const r of (o.rows||[])) { r.kw=kw; fs.appendFileSync(jsonl, JSON.stringify(r)+"\n"); }
          process.stdout.write((o.more||"-") + " " + (o.rows||[]).length);
        }catch(e){ process.stderr.write("ParseErr: "+e.message+"\n"); process.stdout.write("- 0"); }
      });' "$JSONL" "$label")

    local total=$(wc -l <"$JSONL")
    echo "[$label] p$page added=$count total=$total more=${next:0:30}" >&2
    if [[ "$next" == "-" || "$count" == "0" ]]; then break; fi
    if [[ "$next" == \?* ]]; then url="$INSTANCE/search$next"
    elif [[ "$next" == /* ]]; then url="$INSTANCE$next"
    else url="$INSTANCE/search/$next"; fi
    sleep 1
  done

  playwright-cli -s "$SESSION" close >/dev/null 2>&1 || true
  pgrep -f "chrome.*--type=" | xargs -r kill -9 2>/dev/null
  pgrep -x Xvfb | xargs -r kill 2>/dev/null
  sleep 1
}

for spec in "${KEYWORDS[@]}"; do
  IFS='|' read -r kw label pages <<<"$spec"
  if [[ ",$EXISTING," == *",$label,"* ]]; then
    echo "[$label] SKIP (already have data)" >&2
    continue
  fi
  scrape_one_keyword "$kw" "$label" "$pages"
  free -m | head -2 >&2
done

echo "=== DONE ===" >&2
echo "tweets total: $(wc -l <"$JSONL")" >&2
node -e '
  const fs=require("fs"); const c={};
  fs.readFileSync("/tmp/yoshi_out/tweets.jsonl","utf8").split("\n").filter(Boolean).forEach(l=>{
    try { const o=JSON.parse(l); c[o.kw]=(c[o.kw]||0)+1; } catch(e){}
  });
  console.error(JSON.stringify(c,null,2));
'
