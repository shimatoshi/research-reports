#!/usr/bin/env python3
"""adb-pilot — Android 自動操作エンジン

Claude Code から Bash ツール経由で呼び出す想定。
adb が接続済みの状態で使う。

usage:
  python3 pilot.py screenshot [保存先]
  python3 pilot.py tap <x> <y>
  python3 pilot.py swipe <x1> <y1> <x2> <y2> [duration_ms]
  python3 pilot.py open-url <url>
  python3 pilot.py dump-ui [保存先]
  python3 pilot.py find-tap <テキスト>
  python3 pilot.py find-tap-re <正規表現>
  python3 pilot.py back
  python3 pilot.py home
  python3 pilot.py text <文字列>
  python3 pilot.py key <keycode>
  python3 pilot.py scroll-down
  python3 pilot.py scroll-up
  python3 pilot.py status
  python3 pilot.py wait <秒>
"""

import os
import re
import subprocess
import sys
import time
import xml.etree.ElementTree as ET


def _run(cmd, check=True):
    """adb コマンドを実行して stdout を返す"""
    result = subprocess.run(
        cmd, shell=isinstance(cmd, str),
        capture_output=True, timeout=30,
    )
    if check and result.returncode != 0:
        err = result.stderr.decode('utf-8', errors='replace').strip()
        raise RuntimeError(f'adb error: {err}')
    return result.stdout


def _adb(*args):
    return _run(['adb'] + list(args))


# === 基本操作 ===

def screenshot(save_path='/tmp/adb-screen.png'):
    """スクショ撮影 → ローカル保存"""
    remote = '/sdcard/adb-pilot-screen.png'
    _adb('shell', 'screencap', '-p', remote)
    _adb('pull', remote, save_path)
    _adb('shell', 'rm', remote)
    print(save_path)
    return save_path


def tap(x, y):
    """座標タップ"""
    _adb('shell', 'input', 'tap', str(x), str(y))
    print(f'tap {x} {y}')


def swipe(x1, y1, x2, y2, duration_ms=300):
    """スワイプ"""
    _adb('shell', 'input', 'swipe',
         str(x1), str(y1), str(x2), str(y2), str(duration_ms))
    print(f'swipe {x1},{y1} -> {x2},{y2}')


def open_url(url):
    """Chrome で URL を開く"""
    _adb('shell', 'am', 'start', '-a', 'android.intent.action.VIEW',
         '-d', url, 'com.android.chrome')
    print(f'opened: {url}')


def input_text(text):
    """テキスト入力（英数字向け。日本語は別途IME操作が必要）"""
    # スペースやシェル特殊文字をエスケープ
    escaped = text.replace(' ', '%s').replace('&', '\\&').replace('<', '\\<').replace('>', '\\>')
    _adb('shell', 'input', 'text', escaped)
    print(f'text: {text}')


def key(keycode):
    """キーイベント送信"""
    _adb('shell', 'input', 'keyevent', str(keycode))
    print(f'key: {keycode}')


def back():
    """戻るボタン"""
    key(4)  # KEYCODE_BACK


def home():
    """ホームボタン"""
    key(3)  # KEYCODE_HOME


def scroll_down():
    """下スクロール（画面中央で上方向にスワイプ）"""
    # Pixel 5: 1080x2340
    swipe(540, 1500, 540, 500, 300)


def scroll_up():
    """上スクロール"""
    swipe(540, 500, 540, 1500, 300)


def wait(seconds):
    """待機"""
    time.sleep(float(seconds))
    print(f'waited {seconds}s')


def status():
    """接続状態を表示"""
    out = _run(['adb', 'devices'], check=False).decode('utf-8', errors='replace')
    print(out.strip())
    # デバイス情報も
    try:
        model = _adb('shell', 'getprop', 'ro.product.model').decode().strip()
        android_ver = _adb('shell', 'getprop', 'ro.build.version.release').decode().strip()
        resolution = _adb('shell', 'wm', 'size').decode().strip()
        print(f'model: {model}')
        print(f'android: {android_ver}')
        print(f'resolution: {resolution}')
    except Exception:
        pass


# === UI階層操作 ===

def dump_ui(save_path='/tmp/adb-ui-dump.xml'):
    """UI階層XMLを取得してパースし、保存"""
    remote = '/sdcard/adb-pilot-ui.xml'
    _adb('shell', 'uiautomator', 'dump', remote)
    _adb('pull', remote, save_path)
    _adb('shell', 'rm', remote)
    print(save_path)
    return save_path


def _parse_bounds(bounds_str):
    """UIAutomator の bounds 文字列 "[x1,y1][x2,y2]" をパース"""
    m = re.match(r'\[(\d+),(\d+)\]\[(\d+),(\d+)\]', bounds_str)
    if not m:
        return None
    x1, y1, x2, y2 = int(m.group(1)), int(m.group(2)), int(m.group(3)), int(m.group(4))
    return x1, y1, x2, y2


def _center_of(bounds):
    """bounds (x1,y1,x2,y2) の中心座標を返す"""
    x1, y1, x2, y2 = bounds
    return (x1 + x2) // 2, (y1 + y2) // 2


def _find_elements(xml_path, text=None, text_re=None,
                   resource_id=None, class_name=None):
    """UI XMLから要素を検索"""
    tree = ET.parse(xml_path)
    root = tree.getroot()
    results = []

    for node in root.iter('node'):
        # フィルタ
        if text is not None:
            node_text = node.get('text', '')
            content_desc = node.get('content-desc', '')
            if text not in node_text and text not in content_desc:
                continue

        if text_re is not None:
            node_text = node.get('text', '')
            content_desc = node.get('content-desc', '')
            if not re.search(text_re, node_text) and not re.search(text_re, content_desc):
                continue

        if resource_id is not None:
            if resource_id not in node.get('resource-id', ''):
                continue

        if class_name is not None:
            if class_name not in node.get('class', ''):
                continue

        bounds = _parse_bounds(node.get('bounds', ''))
        if not bounds:
            continue

        results.append({
            'text': node.get('text', ''),
            'content_desc': node.get('content-desc', ''),
            'resource_id': node.get('resource-id', ''),
            'class': node.get('class', ''),
            'bounds': bounds,
            'center': _center_of(bounds),
            'clickable': node.get('clickable') == 'true',
        })

    return results


def find_and_tap(search_text):
    """テキストでUI要素を探してタップ"""
    xml_path = dump_ui('/tmp/adb-ui-find.xml')
    elements = _find_elements(xml_path, text=search_text)

    if not elements:
        print(f'NOT FOUND: "{search_text}"')
        # 見つかった全テキスト要素を表示（デバッグ用）
        all_els = _find_elements(xml_path)
        texts = [e['text'] for e in all_els if e['text']]
        if texts:
            print(f'visible texts: {texts[:20]}')
        return False

    # 最初にマッチした要素をタップ
    el = elements[0]
    cx, cy = el['center']
    print(f'found: "{el["text"] or el["content_desc"]}" at ({cx}, {cy})')
    tap(cx, cy)
    return True


def find_and_tap_re(pattern):
    """正規表現でUI要素を探してタップ"""
    xml_path = dump_ui('/tmp/adb-ui-find.xml')
    elements = _find_elements(xml_path, text_re=pattern)

    if not elements:
        print(f'NOT FOUND (regex): "{pattern}"')
        return False

    el = elements[0]
    cx, cy = el['center']
    print(f'found: "{el["text"] or el["content_desc"]}" at ({cx}, {cy})')
    tap(cx, cy)
    return True


# === CLI エントリポイント ===

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    cmd = sys.argv[1]
    args = sys.argv[2:]

    commands = {
        'screenshot':   lambda: screenshot(args[0] if args else '/tmp/adb-screen.png'),
        'tap':          lambda: tap(int(args[0]), int(args[1])),
        'swipe':        lambda: swipe(int(args[0]), int(args[1]), int(args[2]), int(args[3]),
                                      int(args[4]) if len(args) > 4 else 300),
        'open-url':     lambda: open_url(args[0]),
        'dump-ui':      lambda: dump_ui(args[0] if args else '/tmp/adb-ui-dump.xml'),
        'find-tap':     lambda: find_and_tap(' '.join(args)),
        'find-tap-re':  lambda: find_and_tap_re(args[0]),
        'back':         back,
        'home':         home,
        'text':         lambda: input_text(' '.join(args)),
        'key':          lambda: key(args[0]),
        'scroll-down':  scroll_down,
        'scroll-up':    scroll_up,
        'status':       status,
        'wait':         lambda: wait(args[0] if args else 1),
    }

    if cmd not in commands:
        print(f'unknown command: {cmd}')
        print(f'available: {", ".join(sorted(commands.keys()))}')
        sys.exit(1)

    try:
        commands[cmd]()
    except Exception as e:
        print(f'ERROR: {e}', file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
