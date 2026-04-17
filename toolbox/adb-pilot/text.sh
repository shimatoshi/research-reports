#!/bin/bash
# テキスト入力（英数字のみ。日本語はpilot.py経由で）
# usage: text.sh <text>

if [ $# -lt 1 ]; then echo "usage: text.sh <text>"; exit 1; fi
adb shell input text "$1"
