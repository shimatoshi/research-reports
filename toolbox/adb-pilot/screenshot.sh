#!/bin/bash
# スクショ撮影 → ローカルに保存
# usage: screenshot.sh [保存先パス]

OUT="${1:-/tmp/adb-screen.png}"
adb shell screencap -p /sdcard/adb-pilot-screen.png
adb pull /sdcard/adb-pilot-screen.png "$OUT" 2>/dev/null
adb shell rm /sdcard/adb-pilot-screen.png
echo "$OUT"
