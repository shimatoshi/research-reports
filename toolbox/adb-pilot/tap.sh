#!/bin/bash
# 座標タップ
# usage: tap.sh <x> <y>

if [ $# -lt 2 ]; then echo "usage: tap.sh <x> <y>"; exit 1; fi
adb shell input tap "$1" "$2"
