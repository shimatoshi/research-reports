#!/bin/bash
# Chrome で URL を開く
# usage: open-url.sh <url>

if [ $# -lt 1 ]; then echo "usage: open-url.sh <url>"; exit 1; fi
adb shell am start -a android.intent.action.VIEW -d "$1" com.android.chrome
