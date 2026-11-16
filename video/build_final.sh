#!/bin/bash
# Build the final video from rendered animation + narration. Run from video/ after:
#   .venv/bin/python narration.py && .venv/bin/manim -r 2560,1440 --fps 30 scenes.py ArchitectureScene && .venv/bin/python mix_sfx.py
# Usage: ./build_final.sh <out-name>      e.g. ./build_final.sh DevReceipts-Video1-FINAL-v3
set -euo pipefail
NAME="${1:-DevReceipts-Video1-FINAL-v3}"
VID="${VID:-media/videos/scenes/1440p30/ArchitectureScene.mp4}"   # e.g. VID=media/videos/scenes/2160p30/ArchitectureScene.mp4 for 4K
CRF="${CRF:-16}"
mkdir -p out
for variant in sfx nosfx; do
  if [ "$variant" = sfx ]; then AUD=build/narration_sfx.wav; OUT="out/$NAME.mp4"; else AUD=build/narration.wav; OUT="out/$NAME-nosfx.mp4"; fi
  ffmpeg -y -loglevel error -i "$VID" -i "$AUD" -map 0:v -map 1:a \
    -c:v libx264 -crf "$CRF" -preset slow -tune animation -pix_fmt yuv420p -movflags +faststart \
    -af "loudnorm=I=-14:TP=-1.5:LRA=11,apad" -c:a aac -b:a 256k -ar 48000 -ac 2 -shortest "$OUT"
  echo "wrote $OUT"
done
cp build/captions.srt "out/$NAME.srt"
