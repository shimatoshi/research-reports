#!/bin/bash
# UI階層XMLを取得
# usage: dump-ui.sh [保存先パス]

OUT="${1:-/tmp/adb-ui-dump.xml}"
adb shell uiautomator dump /sdcard/adb-pilot-ui.xml
adb pull /sdcard/adb-pilot-ui.xml "$OUT" 2>/dev/null
adb shell rm /sdcard/adb-pilot-ui.xml
echo "$OUT"
