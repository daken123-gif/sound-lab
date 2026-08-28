#!/usr/bin/env bash
set -euo pipefail

out_dir="${1:-aac-stereo-benchmark}"
mkdir -p "$out_dir"

rate=48000
left_generation='0.42*sin(2*PI*173*t)+0.21*sin(2*PI*509*t)+0.12*sin(2*PI*(71*t+3*t*t))+0.06*sin(2*PI*1901*t)*sin(2*PI*1.7*t)'
right_generation='0.38*sin(2*PI*199*t)+0.18*sin(2*PI*701*t)+0.11*sin(2*PI*(83*t+2.4*t*t))+0.05*sin(2*PI*2309*t)*sin(2*PI*2.1*t)'
left_loop='0.52*sin(2*PI*480*t)+0.19*sin(2*PI*960*t)+0.07*sin(2*PI*1440*t)'
right_loop='0.47*sin(2*PI*600*t)+0.17*sin(2*PI*1200*t)+0.06*sin(2*PI*1800*t)'

ffmpeg -hide_banner -loglevel error -y \
  -f lavfi -i "aevalsrc=${left_generation}|${right_generation}:s=${rate}:d=20" \
  -c:a pcm_s24le "$out_dir/generation-source.wav"

ffmpeg -hide_banner -loglevel error -y \
  -f lavfi -i "aevalsrc=${left_loop}|${right_loop}:s=${rate}:d=10" \
  -c:a pcm_s24le "$out_dir/loop-source.wav"

for bitrate in 128 192 256 320
do
  cp "$out_dir/generation-source.wav" "$out_dir/current-${bitrate}.wav"
  for generation in $(seq 1 10)
  do
    ffmpeg -hide_banner -loglevel error -y -i "$out_dir/current-${bitrate}.wav" \
      -c:a aac -b:a "${bitrate}k" "$out_dir/current-${bitrate}.m4a"
    ffmpeg -hide_banner -loglevel error -y -i "$out_dir/current-${bitrate}.m4a" \
      -c:a pcm_s24le "$out_dir/current-${bitrate}-decoded.wav"
    if [[ "$generation" == 1 || "$generation" == 10 ]]
    then
      cp "$out_dir/current-${bitrate}.m4a" "$out_dir/generation-${bitrate}-${generation}.m4a"
      cp "$out_dir/current-${bitrate}-decoded.wav" "$out_dir/generation-${bitrate}-${generation}-decoded.wav"
    fi
    cp "$out_dir/current-${bitrate}-decoded.wav" "$out_dir/current-${bitrate}.wav"
  done

  ffmpeg -hide_banner -loglevel error -y -i "$out_dir/loop-source.wav" \
    -c:a aac -b:a "${bitrate}k" "$out_dir/loop-${bitrate}.m4a"
  ffmpeg -hide_banner -loglevel error -y -i "$out_dir/loop-${bitrate}.m4a" \
    -c:a pcm_s24le "$out_dir/loop-${bitrate}-decoded.wav"
done

python3 "$(dirname "$0")/analyze_aac_stereo.py" "$out_dir"
