#!/bin/bash
# キーイベント送信
# usage: key.sh <keycode>
# よく使うもの: KEYCODE_BACK(4) KEYCODE_HOME(3) KEYCODE_ENTER(66)

if [ $# -lt 1 ]; then echo "usage: key.sh <keycode>"; exit 1; fi
adb shell input keyevent "$1"
