#!/usr/bin/env bash
# Rebuild the game video end to end: renders/art-or-artifice.mp4 (1080x1080, 30 fps).
# Needs: python3, node, ffmpeg, npm packages (npm ci), game/.key and Chrome (set CHROME, see record.mjs).
# Starts its own local Worker with an empty game state, so the live leaderboard never sees the recording.
set -euo pipefail
cd "$(dirname "$0")"
PORT="${PORT:-8812}"
STATE="$(mktemp -d)"
WORKER=""
stop() { [ -n "$WORKER" ] && kill -- "-$WORKER" 2>/dev/null; rm -rf "$STATE"; }
trap stop EXIT

(cd ../.. && python3 -m artgen studio build >/dev/null)
setsid bash -c "cd ../.. && exec npx wrangler dev --port $PORT --local-protocol https --persist-to '$STATE' >'$STATE/wrangler.log' 2>&1" &
WORKER=$!
for _ in $(seq 60); do curl -sk -o /dev/null "https://127.0.0.1:$PORT/game" && break; sleep 1; done
PORT="$PORT" node record.mjs                      # one round -> raw/game.mp4 + recording.json
kill -- "-$WORKER"; WORKER=""

python3 scripts/build_index.py                    # clip, timeline.json, index.html
python3 scripts/make-music.py                     # music to the timeline
bash ../demo/scripts/make-sfx.sh . 1 0.1 1 >/dev/null
rm -f audio/sfx/pad.wav audio/sfx/rush.wav audio/sfx/typing.wav
ffmpeg -y -loglevel error -f lavfi -i "sine=frequency=70:sample_rate=48000:duration=0.5" \
  -f lavfi -i "anoisesrc=color=brown:seed=11:sample_rate=48000:duration=0.5" \
  -filter_complex "[0:a]afade=t=out:st=0.01:d=0.45:curve=exp,volume=0.9[a];[1:a]lowpass=f=700,afade=t=out:st=0.0:d=0.12:curve=exp,volume=0.8[b];[a][b]amix=inputs=2:normalize=0" \
  audio/sfx/stamp.wav
npx hyperframes check .
npx hyperframes render . --output renders/art-or-artifice.mp4 --quality standard --fps 30
