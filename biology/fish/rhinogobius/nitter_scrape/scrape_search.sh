#!/bin/bash
# Chromium-based search scraper for nitter.tiekoetter.com (handles Anubis).
# Outputs tweets to /tmp/yoshi_out/tweets.jsonl
set -u

INSTANCE="https://nitter.tiekoetter.com"
SESSION="srch"
OUT_DIR=/tmp/yoshi_out
JSONL=$OUT_DIR/tweets.jsonl
ERR=$OUT_DIR/err_search.log
mkdir -p "$OUT_DIR"
: >"$JSONL"; : >"$ERR"

pgrep -x Xvfb | xargs -r kill 2>/dev/null
sleep 1
Xvfb :99 -screen 0 1280x900x24 >/tmp/xvfb.log 2>&1 &
sleep 2
export DISPLAY=:99

cleanup() {
  playwright-cli -s "$SESSION" close >/dev/null 2>&1 || true
  pgrep -x Xvfb | xargs -r kill 2>/dev/null
}
trap cleanup EXIT

# Extract: returns JSON-serializable object (playwright --raw will stringify it once)
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
  const title = document.title;
  return { rows, more, title };
})()'

# Open chromium + root page → lets Anubis solve
playwright-cli --session="$SESSION" --browser=chromium --headed \
  open "$INSTANCE/" >/tmp/pw_open.log 2>&1
sleep 8

extract_and_save() {
  local label="$1"
  local raw
  raw=$(playwright-cli -s "$SESSION" --raw eval "$EXTRACT" 2>>"$ERR")
  if [[ -z "$raw" ]]; then echo "NEXT="; return; fi
  local next
  next=$(printf '%s' "$raw" | node -e '
    let s=""; process.stdin.on("data",d=>s+=d); process.stdin.on("end",()=>{
      try{
        // Unwrap double-stringified JSON if needed
        let o = JSON.parse(s);
        if (typeof o === "string") o = JSON.parse(o);
        const fs=require("fs");
        const jsonl=process.argv[1], kw=process.argv[2];
        for (const r of (o.rows||[])) { r.kw=kw; fs.appendFileSync(jsonl, JSON.stringify(r)+"\n"); }
        process.stdout.write((o.more||"") + "\t" + (o.rows||[]).length + "\t" + (o.title||""));
      }catch(e){process.stderr.write("ParseErr: "+e.message+" src="+s.slice(0,200)+"\n");}
    });' "$JSONL" "$label")
  echo "NEXT=$next"
}

scrape_keyword() {
  local kw="$1"  label="$2"  max_pages="${3:-12}"
  # Build initial search URL
  local url="$INSTANCE/search?f=tweets&q=$(node -e "console.log(encodeURIComponent(process.argv[1]))" "$kw")"
  local page=1
  while (( page <= max_pages )); do
    playwright-cli -s "$SESSION" goto "$url" >/tmp/pw_goto.log 2>&1
    sleep 5
    # Check if we hit Anubis challenge, wait more if so
    local title
    title=$(playwright-cli -s "$SESSION" --raw eval "document.title" 2>>"$ERR" | tr -d '"')
    if [[ "$title" == *"ボット"* || "$title" == *"Making sure"* ]]; then
      echo "[$label] Anubis challenge, wait 10s..." >&2
      sleep 10
    fi
    local r
    r=$(extract_and_save "$label")
    local next_tab=${r#NEXT=}
    local more=$(echo "$next_tab" | cut -f1)
    local count=$(echo "$next_tab" | cut -f2)
    local ttl=$(echo "$next_tab" | cut -f3)
    local total=$(wc -l <"$JSONL")
    echo "[$label] p$page rows=$count total=$total more=${more:+Y} title=\"${ttl:0:50}\"" >&2
    if [[ -z "$more" || "$count" == "0" ]]; then break; fi
    # Pagination URL: href is "?f=tweets&q=...&cursor=..." — needs /search prefix
    if [[ "$more" == \?* ]]; then
      url="$INSTANCE/search$more"
    elif [[ "$more" == /* ]]; then
      url="$INSTANCE$more"
    else
      url="$INSTANCE/search/$more"
    fi
    ((page++))
    sleep 1
  done
}

KEYWORDS=(
  "ヨシノボリ|yoshinobori_kata|15"
  "よしのぼり|yoshinobori_hira|8"
  "Rhinogobius|rhinogobius_en|8"
  "オオヨシノボリ|ooyoshinobori|10"
  "カワヨシノボリ|kawayoshinobori|10"
  "シマヨシノボリ|shimayoshinobori|10"
  "クロヨシノボリ|kuroyoshinobori|10"
  "ルリヨシノボリ|ruriyoshinobori|10"
  "トウヨシノボリ|touyoshinobori|10"
  "カジカヨシノボリ|kajikayoshinobori|5"
  "ヒラヨシノボリ|hirayoshinobori|5"
  "アオバラヨシノボリ|aobarayoshinobori|5"
  "アヤヨシノボリ|ayayoshinobori|5"
  "ヨシノボリ属|yoshinobori_genus|5"
)

for spec in "${KEYWORDS[@]}"; do
  IFS='|' read -r kw label pages <<<"$spec"
  scrape_keyword "$kw" "$label" "$pages"
  sleep 2
done

echo "=== SEARCH DONE ===" >&2
echo "tweets: $(wc -l <"$JSONL")" >&2
