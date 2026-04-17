#!/bin/bash
# スワイプ
# usage: swipe.sh <x1> <y1> <x2> <y2> [duration_ms]

if [ $# -lt 4 ]; then echo "usage: swipe.sh <x1> <y1> <x2> <y2> [duration_ms]"; exit 1; fi
DUR="${5:-300}"
adb shell input swipe "$1" "$2" "$3" "$4" "$DUR"
