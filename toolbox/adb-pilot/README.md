# adb-pilot

Android 端末を adb 経由で自動操作するツール群。
Claude Code から Bash ツール経由で呼び出して、実機 UI のデバッグ・確認に使う。

## 前提条件

- adb が使える環境（PC + USB 接続、またはネットワーク経由）
- Android 端末で USB デバッグ ON

## セットアップ

### パターン A: PC + USB 接続

```bash
# PC に adb インストール（Ubuntu）
sudo apt install android-tools-adb

# USB 接続して確認
adb devices
```

### パターン B: ネットワーク経由（Tailscale 等）

```bash
# 端末側で TCP/IP モード有効化（USB 接続時に1回）
adb tcpip 5555

# PC から接続
adb connect <端末のIP>:5555
```

### パターン C: Termux 内から自分自身を操作

```bash
# Termux
pkg install android-tools

# ワイヤレスデバッグを ON にして接続
# 設定 → 開発者向けオプション → ワイヤレスデバッグ → ペア設定コードによるデバイスのペア設定
adb pair localhost:<ペアリングポート> <ペアリングコード>
adb connect localhost:<接続ポート>
```

## 使い方

### シェルスクリプト（単発操作）

```bash
./screenshot.sh /tmp/screen.png    # スクショ撮影
./tap.sh 540 1200                  # 座標タップ
./swipe.sh 540 1500 540 500        # スワイプ
./open-url.sh "https://example.com" # Chrome で URL を開く
./dump-ui.sh /tmp/ui.xml           # UI階層 XML 取得
./text.sh "hello"                  # テキスト入力
./key.sh 4                         # キーイベント（4=戻る, 3=ホーム）
```

### pilot.py（操作エンジン）

```bash
python3 pilot.py status                    # 接続状態確認
python3 pilot.py screenshot /tmp/s.png     # スクショ
python3 pilot.py open-url "https://..."    # Chrome で開く
python3 pilot.py tap 540 1200              # タップ
python3 pilot.py find-tap "設定"            # テキストで要素を探してタップ
python3 pilot.py find-tap-re "スケジュール.*編集"  # 正規表現で探してタップ
python3 pilot.py scroll-down               # 下スクロール
python3 pilot.py back                      # 戻る
python3 pilot.py dump-ui /tmp/ui.xml       # UI階層取得
python3 pilot.py wait 2                    # 2秒待機
```

## Claude Code での使い方

```
ユーザー: 「スケジュール画面の遷移確認して」

Claude:
1. python3 pilot.py open-url "http://localhost:8789/#/schedule"
2. python3 pilot.py wait 2
3. python3 pilot.py screenshot /tmp/screen1.png
4. → Read ツールでスクショを見る
5. python3 pilot.py find-tap "スケジュール編集"
6. python3 pilot.py wait 1
7. python3 pilot.py screenshot /tmp/screen2.png
8. → Read ツールで確認 → フィードバック
```

## コマンド一覧

| コマンド | 説明 |
|----------|------|
| `status` | 接続状態・デバイス情報表示 |
| `screenshot [path]` | スクショ撮影 |
| `tap <x> <y>` | 座標タップ |
| `swipe <x1> <y1> <x2> <y2> [ms]` | スワイプ |
| `open-url <url>` | Chrome で URL を開く |
| `find-tap <text>` | テキストで UI 要素を探してタップ |
| `find-tap-re <regex>` | 正規表現で探してタップ |
| `dump-ui [path]` | UI 階層 XML 取得 |
| `text <string>` | テキスト入力 |
| `key <keycode>` | キーイベント送信 |
| `back` | 戻る（KEYCODE_BACK） |
| `home` | ホーム（KEYCODE_HOME） |
| `scroll-down` | 下スクロール |
| `scroll-up` | 上スクロール |
| `wait <seconds>` | 待機 |

## キーコード早見表

| コード | キー |
|--------|------|
| 3 | HOME |
| 4 | BACK |
| 24 | VOLUME_UP |
| 25 | VOLUME_DOWN |
| 26 | POWER |
| 66 | ENTER |
| 82 | MENU |
| 187 | APP_SWITCH（最近のアプリ） |
