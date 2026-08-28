#!/usr/bin/env bash
set -euo pipefail

out_dir="${1:-crash-recovery-benchmark}"
mkdir -p "$out_dir"

rate=48000
duration=60

ffmpeg -hide_banner -loglevel error -y \
  -f lavfi -i "anoisesrc=color=pink:sample_rate=${rate}:duration=${duration}:amplitude=0.35" \
  -c:a pcm_f32le "$out_dir/source.caf"

ffmpeg -hide_banner -loglevel error -y \
  -i "$out_dir/source.caf" -c:a alac "$out_dir/source.m4a"

ffmpeg -hide_banner -loglevel error -y \
  -i "$out_dir/source.caf" -c:a alac "$out_dir/source.alac.caf"

ffmpeg -hide_banner -loglevel error -y \
  -i "$out_dir/source.caf" -c:a alac \
  -movflags +frag_keyframe+empty_moov+default_base_moof -frag_duration 2000000 \
  "$out_dir/source.fragmented.m4a"

printf 'source,retained_percent,file_bytes,decoded_frames,decoded_seconds,decoder_exit\n' > "$out_dir/results.csv"

for source_path in \
  "$out_dir/source.caf" \
  "$out_dir/source.m4a" \
  "$out_dir/source.alac.caf" \
  "$out_dir/source.fragmented.m4a"
do
  source_name="$(basename "$source_path")"
  full_size="$(stat -c %s "$source_path")"

  for percent in 25 50 75 90 95 99 100
  do
    retained_bytes="$((full_size * percent / 100))"
    truncated_path="$out_dir/${source_name}.${percent}.partial"
    head -c "$retained_bytes" "$source_path" > "$truncated_path"

    set +e
    decoded_bytes="$(ffmpeg -hide_banner -loglevel error -i "$truncated_path" -f f32le -c:a pcm_f32le - 2> "$out_dir/decode-error.txt" | wc -c)"
    decoder_exit="${PIPESTATUS[0]}"
    set -e

    decoded_frames="$((decoded_bytes / 4))"
    decoded_seconds="$(awk -v frames="$decoded_frames" -v rate="$rate" 'BEGIN { printf "%.3f", frames/rate }')"
    printf '%s,%s,%s,%s,%s,%s\n' \
      "$source_name" "$percent" "$retained_bytes" "$decoded_frames" "$decoded_seconds" "$decoder_exit" \
      >> "$out_dir/results.csv"
  done
done

rm -f "$out_dir/decode-error.txt"
