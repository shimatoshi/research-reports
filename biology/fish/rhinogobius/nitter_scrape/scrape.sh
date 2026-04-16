#!/usr/bin/env bash
# Runs inside proot-distro ubuntu on pixel5.
# Scrapes nitter.tiekoetter.com for Rhinogobius-related tweets + images + user profile location.
set -u

INSTANCE="https://nitter.tiekoetter.com"
SESSION="yoshi"
OUT_DIR=/tmp/yoshi_out
IMG_DIR=$OUT_DIR/images
JSONL=$OUT_DIR/tweets.jsonl
USERS=$OUT_DIR/users.jsonl
ERR=$OUT_DIR/err.log

rm -rf "$OUT_DIR"
mkdir -p "$IMG_DIR"
: >"$JSONL"; : >"$USERS"; : >"$ERR"

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

# Tweet extraction
EXTRACT_TWEETS='(() => {
  const items = Array.from(document.querySelectorAll(".timeline-item"));
  const rows = items.filter(i => !i.classList.contains("show-more")).map(i => {
    const username = (i.getAttribute("data-username") || "").trim();
    const fullname = i.querySelector(".fullname")?.getAttribute("title") || "";
    const dateAnchor = i.querySelector(".tweet-date a");
    const date_iso = dateAnchor?.getAttribute("title") || "";
    const date_rel = (dateAnchor?.innerText||"").trim();
    const tweetLink = i.querySelector("a.tweet-link")?.getAttribute("href") || "";
    const m = tweetLink.match(/\/([^/]+)\/status\/(\d+)/);
    const tweet_id = m ? m[2] : "";
    const replying = (i.querySelector(".replying-to")?.innerText||"").trim();
    const text = (i.querySelector(".tweet-content")?.innerText||"").trim();
    const images_orig = Array.from(i.querySelectorAll(".attachments a.still-image"))
      .map(a => a.getAttribute("href") || "").filter(Boolean);
    const images_thumb = Array.from(i.querySelectorAll(".attachments .attachment img"))
      .map(img => img.getAttribute("src") || "").filter(Boolean);
    const videos = Array.from(i.querySelectorAll(".attachments video source, .attachments video"))
      .map(v => v.getAttribute("src") || "").filter(Boolean);
    const quote_user = (i.querySelector(".quote .username")?.innerText||"").trim();
    const quote_text = (i.querySelector(".quote .quote-text")?.innerText||"").trim();
    const retweet_header = (i.querySelector(".retweet-header")?.innerText||"").trim();
    const stats = {};
    i.querySelectorAll(".tweet-stats .tweet-stat").forEach(s => {
      const icon = s.querySelector(".icon-container [class*=icon-]");
      if (!icon) return;
      const cls = Array.from(icon.classList).find(c => c.startsWith("icon-"));
      stats[cls] = s.innerText.trim();
    });
    return { username, fullname, tweet_id, tweet_link: tweetLink, date_iso, date_rel,
             replying_to: replying, retweet_header,
             text, images_orig, images_thumb, videos,
             quote_user, quote_text, stats };
  });
  const more = document.querySelector(".show-more a")?.getAttribute("href") || "";
  return { rows, more };
})()'

# Open session
FIRST_Q="%E3%83%A8%E3%82%B7%E3%83%8E%E3%83%9C%E3%83%AA"
playwright-cli --session="$SESSION" --browser=chromium --headed \
  open "$INSTANCE/search?f=tweets&q=$FIRST_Q" >/tmp/pw_open.log 2>&1
sleep 5

scrape_keyword() {
  local kw="$1"  label="$2"  max_pages="${3:-15}"
  local url="$INSTANCE/search?f=tweets&q=$kw"
  local page=1 prev_count=0
  while (( page <= max_pages )); do
    echo "[$label] page=$page" >&2
    playwright-cli -s "$SESSION" goto "$url" >>/tmp/pw_goto.log 2>&1
    sleep 3
    local raw
    raw=$(playwright-cli -s "$SESSION" --raw eval "$EXTRACT_TWEETS" 2>>"$ERR")
    if [[ -z "$raw" ]]; then echo "[$label] empty — stop" >&2; break; fi

    local next
    next=$(printf '%s' "$raw" | node -e '
      let s=""; process.stdin.on("data",d=>s+=d); process.stdin.on("end",()=>{
        try{
          const o=JSON.parse(s);
          const fs=require("fs");
          const jsonl=process.argv[1]; const kw=process.argv[2];
          for (const r of (o.rows||[])) { r.kw=kw; fs.appendFileSync(jsonl, JSON.stringify(r)+"\n"); }
          process.stdout.write(o.more || "");
        }catch(e){process.stderr.write("ParseErr: "+e.message+"\n"+s.slice(0,300)+"\n");}
      });' "$JSONL" "$label")

    local total=$(wc -l <"$JSONL")
    local added=$((total - prev_count))
    prev_count=$total
    echo "[$label] p$page added=$added total=$total" >&2
    [[ -z "$next" || $added -eq 0 ]] && break
    url="$INSTANCE$next"
    ((page++))
    sleep 1
  done
}

# Keywords — カタカナ種名群 + ひらがな + 学名 + 代表6種
# ヨシノボリ
scrape_keyword "%E3%83%A8%E3%82%B7%E3%83%8E%E3%83%9C%E3%83%AA"        "yoshinobori_kata" 15
# よしのぼり
scrape_keyword "%E3%82%88%E3%81%97%E3%81%AE%E3%81%BC%E3%82%8A"        "yoshinobori_hira" 8
# Rhinogobius
scrape_keyword "Rhinogobius"                                          "rhinogobius_en"   8
# オオヨシノボリ
scrape_keyword "%E3%82%AA%E3%82%AA%E3%83%A8%E3%82%B7%E3%83%8E%E3%83%9C%E3%83%AA" "ooyoshinobori" 8
# カワヨシノボリ
scrape_keyword "%E3%82%AB%E3%83%AF%E3%83%A8%E3%82%B7%E3%83%8E%E3%83%9C%E3%83%AA" "kawayoshinobori" 8
# シマヨシノボリ
scrape_keyword "%E3%82%B7%E3%83%9E%E3%83%A8%E3%82%B7%E3%83%8E%E3%83%9C%E3%83%AA" "shimayoshinobori" 8
# クロヨシノボリ
scrape_keyword "%E3%82%AF%E3%83%AD%E3%83%A8%E3%82%B7%E3%83%8E%E3%83%9C%E3%83%AA" "kuroyoshinobori" 8
# ルリヨシノボリ
scrape_keyword "%E3%83%AB%E3%83%AA%E3%83%A8%E3%82%B7%E3%83%8E%E3%83%9C%E3%83%AA" "ruriyoshinobori" 8
# トウヨシノボリ
scrape_keyword "%E3%83%88%E3%82%A6%E3%83%A8%E3%82%B7%E3%83%8E%E3%83%9C%E3%83%AA" "touyoshinobori"  8

echo "=== SCRAPED TWEETS ===" >&2
wc -l "$JSONL" >&2

# --- User profile location fetching (unique usernames) ---
echo "=== FETCHING PROFILE LOCATIONS ===" >&2
mapfile -t UNIQ_USERS < <(node -e '
  const fs=require("fs");
  const set=new Set();
  fs.readFileSync(process.argv[1],"utf8").split("\n").filter(Boolean).forEach(l=>{
    try{ const o=JSON.parse(l); if (o.username) set.add(o.username); }catch(e){}
  });
  for (const u of set) console.log(u);
' "$JSONL")

echo "unique users: ${#UNIQ_USERS[@]}" >&2

PROFILE_EXTRACT='(() => {
  const loc = (document.querySelector(".profile-location")?.innerText||"").trim();
  const bio = (document.querySelector(".profile-bio")?.innerText||"").trim();
  const website = document.querySelector(".profile-website a")?.getAttribute("href") || "";
  const joined = document.querySelector(".profile-joindate")?.getAttribute("title") || "";
  const nm = (document.querySelector(".profile-card-fullname")?.innerText||"").trim();
  return { loc, bio, website, joined, name: nm };
})()'

for u in "${UNIQ_USERS[@]}"; do
  playwright-cli -s "$SESSION" goto "$INSTANCE/$u" >>/tmp/pw_prof.log 2>&1
  sleep 2
  raw=$(playwright-cli -s "$SESSION" --raw eval "$PROFILE_EXTRACT" 2>>"$ERR")
  if [[ -n "$raw" ]]; then
    printf '%s' "$raw" | node -e '
      let s=""; process.stdin.on("data",d=>s+=d); process.stdin.on("end",()=>{
        try{
          const o=JSON.parse(s); o.username=process.argv[1];
          require("fs").appendFileSync(process.argv[2], JSON.stringify(o)+"\n");
        }catch(e){process.stderr.write("profErr: "+e.message+"\n");}
      });' "$u" "$USERS"
  fi
  echo "profile: $u" >&2
done

echo "=== USERS ===" >&2
wc -l "$USERS" >&2

# --- Image download ---
echo "=== IMAGE DOWNLOAD ===" >&2
node -e '
  const fs=require("fs"), https=require("https"), http=require("http"), path=require("path");
  const lines=fs.readFileSync(process.argv[1],"utf8").split("\n").filter(Boolean);
  const imgRoot=process.argv[2];
  const instance=process.argv[3];
  const jobs=[];
  for (const l of lines) {
    try {
      const r=JSON.parse(l);
      const slug=(r.username||"_")+"_"+(r.tweet_id||"x");
      const urls=(r.images_orig && r.images_orig.length) ? r.images_orig : (r.images_thumb||[]);
      for (let i=0;i<urls.length;i++) {
        let u=urls[i];
        if (u.startsWith("/")) u=instance+u;
        const ext=u.match(/\.(jpg|jpeg|png|gif|webp)/i)?.[1] || "jpg";
        jobs.push({u, out: path.join(imgRoot, slug+"_"+i+"."+ext)});
      }
    } catch(e){}
  }
  console.error("image jobs:", jobs.length);
  let ok=0, done=0;
  const dlOne=(j,cb)=>{
    const lib = j.u.startsWith("https") ? https : http;
    const req=lib.get(j.u, {headers:{"User-Agent":"Mozilla/5.0","Referer":instance+"/"}}, res=>{
      if (res.statusCode>=300 && res.statusCode<400 && res.headers.location) {
        // Redirect handling
        const loc=res.headers.location.startsWith("http")?res.headers.location:instance+res.headers.location;
        res.resume();
        const r2=(loc.startsWith("https")?https:http).get(loc,{headers:{"User-Agent":"Mozilla/5.0"}},r=>{
          if (r.statusCode!==200){r.resume();done++;cb();return;}
          const ws=fs.createWriteStream(j.out);r.pipe(ws);ws.on("finish",()=>{ok++;done++;cb();});
        });
        r2.on("error",()=>{done++;cb();});
        return;
      }
      if (res.statusCode!==200) { res.resume(); done++; cb(); return; }
      const ws=fs.createWriteStream(j.out);
      res.pipe(ws); ws.on("finish",()=>{ok++;done++;cb();});
    });
    req.on("error", ()=>{done++;cb();});
    req.setTimeout(15000,()=>{req.destroy();done++;cb();});
  };
  let idx=0, active=0, CC=4;
  const pump=()=>{
    while (active<CC && idx<jobs.length) { active++; dlOne(jobs[idx++], ()=>{active--;pump();}); }
    if (idx>=jobs.length && active===0) { console.error("imgs ok:", ok, "/", jobs.length); }
  };
  pump();
' "$JSONL" "$IMG_DIR" "$INSTANCE"

echo "=== DONE ===" >&2
echo "tweets: $(wc -l <"$JSONL")" >&2
echo "users:  $(wc -l <"$USERS")" >&2
echo "images: $(ls "$IMG_DIR" | wc -l)" >&2
