#!/usr/bin/env bash
set -euo pipefail

out_dir="${1:-generation-loop-benchmark}"
mkdir -p "$out_dir"

rate=48000

generation_expr='0.42*sin(2*PI*173*t)+0.21*sin(2*PI*509*t)+0.12*sin(2*PI*(71*t+3*t*t))+0.06*sin(2*PI*1901*t)*sin(2*PI*1.7*t)'
loop_expr='0.52*sin(2*PI*480*t)+0.19*sin(2*PI*960*t)+0.07*sin(2*PI*1440*t)'

ffmpeg -hide_banner -loglevel error -y \
  -f lavfi -i "aevalsrc=${generation_expr}:s=${rate}:d=20" \
  -c:a pcm_s24le "$out_dir/generation-source.wav"

ffmpeg -hide_banner -loglevel error -y \
  -f lavfi -i "aevalsrc=${loop_expr}:s=${rate}:d=10" \
  -c:a pcm_s24le "$out_dir/loop-source.wav"

cp "$out_dir/generation-source.wav" "$out_dir/alac-input.wav"
cp "$out_dir/generation-source.wav" "$out_dir/aac-input.wav"

for generation in $(seq 1 10)
do
  ffmpeg -hide_banner -loglevel error -y -i "$out_dir/alac-input.wav" \
    -c:a alac "$out_dir/alac-${generation}.m4a"
  ffmpeg -hide_banner -loglevel error -y -i "$out_dir/alac-${generation}.m4a" \
    -c:a pcm_s24le "$out_dir/alac-output.wav"
  cp "$out_dir/alac-output.wav" "$out_dir/alac-input.wav"

  ffmpeg -hide_banner -loglevel error -y -i "$out_dir/aac-input.wav" \
    -c:a aac -b:a 192k "$out_dir/aac-${generation}.m4a"
  ffmpeg -hide_banner -loglevel error -y -i "$out_dir/aac-${generation}.m4a" \
    -c:a pcm_s24le "$out_dir/aac-output.wav"
  cp "$out_dir/aac-output.wav" "$out_dir/aac-input.wav"

  if [[ "$generation" == 1 || "$generation" == 5 || "$generation" == 10 ]]
  then
    cp "$out_dir/alac-output.wav" "$out_dir/generation-alac-${generation}-decoded.wav"
    cp "$out_dir/aac-output.wav" "$out_dir/generation-aac-${generation}-decoded.wav"
  fi
done

ffmpeg -hide_banner -loglevel error -y -i "$out_dir/loop-source.wav" \
  -c:a alac "$out_dir/loop-alac.m4a"
ffmpeg -hide_banner -loglevel error -y -i "$out_dir/loop-alac.m4a" \
  -c:a pcm_s24le "$out_dir/loop-alac-decoded.wav"

ffmpeg -hide_banner -loglevel error -y -i "$out_dir/loop-source.wav" \
  -c:a aac -b:a 192k "$out_dir/loop-aac.m4a"
ffmpeg -hide_banner -loglevel error -y -i "$out_dir/loop-aac.m4a" \
  -c:a pcm_s24le "$out_dir/loop-aac-decoded.wav"

python3 "$(dirname "$0")/analyze_generation_loop.py" "$out_dir"
