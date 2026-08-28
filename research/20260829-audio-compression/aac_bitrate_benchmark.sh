#!/usr/bin/env bash
set -euo pipefail

source_dir="${1:-generation-loop-benchmark}"
out_dir="${2:-aac-bitrate-benchmark}"
mkdir -p "$out_dir"

cp "$source_dir/generation-source.wav" "$out_dir/generation-source.wav"
cp "$source_dir/loop-source.wav" "$out_dir/loop-source.wav"

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

python3 "$(dirname "$0")/analyze_aac_bitrate.py" "$out_dir"
