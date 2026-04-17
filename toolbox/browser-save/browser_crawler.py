"""BrowserCrawler — 永続ブラウザでページをシングルファイル保存

bin/browser-save.js をサーバーモードで起動し、Chromiumを1回だけ立ち上げる。
各ページはタブで開閉 → DOM+キャッシュ済みリソースからインライン化 → HTML保存。
追加リクエストなし。サーバーから見たら普通のブラウジング。

構成:
  Python (browser_crawler.py)
    → subprocess: proot-distro内で browser-save.js --server <port>
    → HTTP POST /save {"url": "...", "output": "..."} でページ保存を依頼
    → ブラウザは起動しっぱなし、タブだけ開閉
"""

import json
import os
import re
import subprocess
import time
from collections import deque
from urllib.parse import urlparse, urljoin, unquote
from urllib.request import urlopen, Request
from urllib.error import URLError
from html.parser import HTMLParser

from config import CACHE_BASE, AD_DOMAINS

_AD_SET = set(AD_DOMAINS)
_BROWSER_PORT = 3100
_BIN_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'bin')


class _LinkExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []

    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            for name, val in attrs:
                if name == 'href' and val:
                    self.links.append(val)


def _is_proot_available():
    try:
        r = subprocess.run(
            ['proot-distro', 'list'],
            capture_output=True, text=True, timeout=10,
        )
        return r.returncode == 0
    except FileNotFoundError:
        return False


def check_environment(distro='ubuntu'):
    """環境チェック。問題があればエラーメッセージを返す"""
    if not _is_proot_available():
        return 'proot-distro が見つかりません。Termux で pkg install proot-distro を実行してください'

    # Node.js + puppeteer チェック
    try:
        r = subprocess.run(
            ['proot-distro', 'login', distro, '--',
             'node', '-e', "require('puppeteer')"],
            capture_output=True, text=True, timeout=15,
        )
        if r.returncode != 0:
            return (
                f'proot ({distro}) に Node.js + puppeteer が見つかりません。\n'
                f'セットアップ:\n'
                f'  proot-distro login {distro}\n'
                f'  apt update && apt install -y chromium nodejs npm\n'
                f'  npm install -g puppeteer'
            )
    except Exception as e:
        return f'環境チェックエラー: {e}'
    return None


class BrowserCrawler:
    """永続ブラウザ + HTTP API でクロール"""

    def __init__(self, start_url, max_depth=0, delay=2.0,
                 log=None, exclude=None, distro='ubuntu',
                 timeout=30, port=_BROWSER_PORT):
        self.start_url = start_url
        self.domain = urlparse(start_url).netloc
        self.max_depth = max_depth
        self.delay = delay
        self._log = log or print
        self.exclude = exclude or []
        self.distro = distro
        self.timeout = timeout
        self.port = port

        self.cache_dir = os.path.join(CACHE_BASE, self.domain)
        os.makedirs(self.cache_dir, exist_ok=True)

        self._stopped = False
        self._browser_proc = None
        self.page_count = 0

    def stop(self):
        self._stopped = True
        self._stop_browser()

    def _stop_browser(self):
        """ブラウザサーバーを停止"""
        # まずHTTPで正常終了を試みる
        try:
            body = json.dumps({}).encode()
            req = Request(
                f'http://127.0.0.1:{self.port}/quit',
                data=body, method='POST',
                headers={'Content-Type': 'application/json'},
            )
            urlopen(req, timeout=5)
        except Exception:
            pass

        # プロセスをkill
        proc = self._browser_proc
        if proc and proc.poll() is None:
            try:
                proc.kill()
                proc.wait(timeout=5)
            except Exception:
                pass
        self._browser_proc = None

    def _start_browser(self):
        """proot内でbrowser-save.jsをサーバーモードで起動"""
        script = os.path.join(_BIN_DIR, 'browser-save.js')

        cmd = [
            'proot-distro', 'login', self.distro, '--',
            'node', script, '--server', str(self.port),
        ]

        self._browser_proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )

        # サーバー起動を待つ（最大30秒）
        for i in range(60):
            if self._stopped:
                return False
            try:
                req = Request(f'http://127.0.0.1:{self.port}/save',
                              data=b'{}', method='POST',
                              headers={'Content-Type': 'application/json'})
                urlopen(req, timeout=2)
                # 400でもサーバーが応答してれば起動済み
                return True
            except URLError:
                time.sleep(0.5)
            except Exception:
                return True  # 応答があった = 起動済み

        self._log("ブラウザサーバー起動タイムアウト")
        return False

    def _save_page(self, url, filepath):
        """ブラウザサーバーにページ保存を依頼"""
        body = json.dumps({
            'url': url,
            'output': filepath,
            'timeout': self.timeout * 1000,  # ms
        }).encode()

        try:
            req = Request(
                f'http://127.0.0.1:{self.port}/save',
                data=body, method='POST',
                headers={'Content-Type': 'application/json'},
            )
            resp = urlopen(req, timeout=self.timeout + 10)
            result = json.loads(resp.read())
            return result.get('ok', False)
        except Exception as e:
            self._log(f"  保存エラー: {e}")
            return False

    def _is_excluded(self, url):
        lower = url.lower()
        if any(ad in lower for ad in _AD_SET):
            return True
        if re.search(r'(ads|tracking|affiliate|pixel|beacon|popup)', lower):
            return True
        for pat in self.exclude:
            if re.search(pat, url):
                return True
        return False

    def _is_same_domain(self, url):
        return urlparse(url).netloc == self.domain

    def _url_to_filepath(self, url):
        parsed = urlparse(url)
        path = unquote(parsed.path).lstrip('/')
        if not path or path.endswith('/'):
            path += 'index.html'
        if not os.path.splitext(path)[1]:
            path += '.html'
        return os.path.join(self.cache_dir, self.domain, path)

    def _extract_links(self, filepath, base_url):
        try:
            with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
                html = f.read()
        except Exception:
            return []

        parser = _LinkExtractor()
        try:
            parser.feed(html)
        except Exception:
            return []

        links = []
        for href in parser.links:
            if href.startswith(('javascript:', 'mailto:', 'tel:', '#', 'data:')):
                continue
            abs_url = urljoin(base_url, href).split('#')[0]
            if self._is_same_domain(abs_url):
                links.append(abs_url)
        return links

    def run(self, resume=False):
        self._log(f"\U0001f680 クロール開始: {self.start_url}")
        self._log(f"\U0001f4c2 出力先: {self.cache_dir}")
        depth_str = '無制限' if self.max_depth == 0 else str(self.max_depth)
        self._log(f"\u23f1\ufe0f  遅延: {self.delay}s / 深さ: {depth_str}")
        self._log("(Browser crawler — 永続Chromium)")

        # ブラウザ起動
        self._log("Chromium 起動中...")
        if not self._start_browser():
            self._log("\u274c ブラウザ起動失敗")
            return

        self._log("\u2705 Chromium 起動完了（タブ使い回し）")

        try:
            self._crawl_loop(resume)
        finally:
            self._stop_browser()

    def _crawl_loop(self, resume):
        self.page_count = 0
        queue = deque([(self.start_url, 0)])
        visited = set()

        if resume:
            base = os.path.join(self.cache_dir, self.domain)
            if os.path.exists(base):
                existing = sum(1 for _, _, files in os.walk(base) for f in files)
                self.page_count = existing
                self._log(f"  既存 {existing} ファイル検出済み、新規のみ取得")

        while queue and not self._stopped:
            url, depth = queue.popleft()
            url = url.split('#')[0]
            if not url or url in visited:
                continue
            visited.add(url)

            if not self._is_same_domain(url):
                continue
            if self._is_excluded(url):
                continue
            if self.max_depth > 0 and depth > self.max_depth:
                continue

            filepath = self._url_to_filepath(url)

            # resume: 既存はリンク抽出のみ
            if resume and os.path.exists(filepath):
                for link in self._extract_links(filepath, url):
                    if link not in visited:
                        queue.append((link, depth + 1))
                continue

            display = unquote(url)
            if len(display) > 75:
                display = display[:72] + '...'

            ok = self._save_page(url, filepath)

            if self._stopped:
                break

            if ok:
                self.page_count += 1
                self._log(f"[{self.page_count}] {display}")

                for link in self._extract_links(filepath, url):
                    if link not in visited:
                        queue.append((link, depth + 1))
            else:
                self._log(f"[SKIP] {display}")

            time.sleep(self.delay)

        if self._stopped:
            self._log(f"\u23f8\ufe0f 手動停止: {self.page_count} 件取得済み")
        else:
            self._log(f"\u2705 完了: {self.page_count} 件取得")

    def get_file_base(self):
        base = os.path.join(self.cache_dir, self.domain)
        if not os.path.exists(base):
            base = self.cache_dir
        return base
