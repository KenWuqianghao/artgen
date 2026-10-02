#!/usr/bin/env bash
# Rebuild the Studio demo video end to end.
# Needs: the Studio served at http://127.0.0.1:8780 (python3 -m artgen studio serve), node, ffmpeg.
set -euo pipefail
cd "$(dirname "$0")"
node record.mjs                                   # real Studio -> raw/studio.mp4 + actions.json
ffmpeg -y -loglevel error -i raw/studio.mp4 -vf "setpts=PTS/1.2,scale=1920:1080:flags=lanczos,fps=30" \
  -an -c:v libx264 -crf 17 -preset slow -pix_fmt yuv420p -movflags +faststart assets/clip.mp4
python3 scripts/build_index.py                    # timeline.json + index.html
python3 scripts/make-music.py                     # music to the timeline
bash scripts/make-sfx.sh . 19 1.6 "$(python3 -c "import json; print(json.load(open('timeline.json'))['total'])")" >/dev/null
rm -f audio/sfx/pad.wav audio/sfx/rush.wav
python3 scripts/build_index.py                    # again, with the real music length
npx hyperframes check .
npx hyperframes render . --output renders/artgen-studio-demo.mp4 --quality standard --fps 30
