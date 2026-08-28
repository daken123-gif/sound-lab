#!/usr/bin/env bash
set -euo pipefail

source_path="${1:-aac-stereo-benchmark/generation-source.wav}"
out_dir="${2:-lossless-access-benchmark}"
mkdir -p "$out_dir"

ffmpeg -hide_banner -loglevel error -y -stream_loop 5 -i "$source_path" -t 120 \
  -c:a pcm_s24le "$out_dir/source.wav"
ffmpeg -hide_banner -loglevel error -y -i "$out_dir/source.wav" \
  -c:a alac "$out_dir/source.m4a"
ffmpeg -hide_banner -loglevel error -y -i "$out_dir/source.wav" \
  -c:a flac -compression_level 5 "$out_dir/source.flac"

# Do not benchmark a truncated or corrupt encode as if it were a fast decode.
ffmpeg -hide_banner -loglevel error -xerror -i "$out_dir/source.m4a" -f null -
ffmpeg -hide_banner -loglevel error -xerror -i "$out_dir/source.flac" -f null -

elapsed_ms() {
  local start_ns="$1"
  local end_ns="$2"
  awk -v start="$start_ns" -v end="$end_ns" 'BEGIN { printf "%.3f", (end-start)/1000000 }'
}

printf 'format,bytes,decode_1_ms,decode_2_ms,decode_3_ms,four_track_decode_ms\n' > "$out_dir/decode-results.csv"
for entry in "pcm:$out_dir/source.wav" "alac:$out_dir/source.m4a" "flac:$out_dir/source.flac"
do
  format="${entry%%:*}"
  path="${entry#*:}"
  decode_times=()
  for run in 1 2 3
  do
    start_ns="$(date +%s%N)"
    ffmpeg -hide_banner -loglevel error -i "$path" -f null -
    end_ns="$(date +%s%N)"
    decode_times+=("$(elapsed_ms "$start_ns" "$end_ns")")
  done

  start_ns="$(date +%s%N)"
  ffmpeg -hide_banner -loglevel error \
    -i "$path" -i "$path" -i "$path" -i "$path" \
    -filter_complex "amix=inputs=4:normalize=0" -f null -
  end_ns="$(date +%s%N)"
  four_track_ms="$(elapsed_ms "$start_ns" "$end_ns")"

  printf '%s,%s,%s,%s,%s,%s\n' \
    "$format" "$(stat -c %s "$path")" \
    "${decode_times[0]}" "${decode_times[1]}" "${decode_times[2]}" "$four_track_ms" \
    >> "$out_dir/decode-results.csv"
done

printf 'format,position_seconds,seek_decode_ms,reference_md5,decoded_md5,exact_match\n' > "$out_dir/seek-results.csv"
for position in 5 30 60 90 115
do
  reference_md5="$(ffmpeg -hide_banner -loglevel error -ss "$position" -i "$out_dir/source.wav" -t 1 -f s24le -c:a pcm_s24le - | md5sum | cut -d' ' -f1)"
  for entry in "pcm:$out_dir/source.wav" "alac:$out_dir/source.m4a" "flac:$out_dir/source.flac"
  do
    format="${entry%%:*}"
    path="${entry#*:}"
    raw_path="$out_dir/seek.raw"
    start_ns="$(date +%s%N)"
    ffmpeg -hide_banner -loglevel error -y -ss "$position" -i "$path" -t 1 \
      -f s24le -c:a pcm_s24le "$raw_path"
    end_ns="$(date +%s%N)"
    seek_ms="$(elapsed_ms "$start_ns" "$end_ns")"
    decoded_md5="$(md5sum "$raw_path" | cut -d' ' -f1)"
    exact_match=no
    if [[ "$decoded_md5" == "$reference_md5" ]]
    then
      exact_match=yes
    fi
    printf '%s,%s,%s,%s,%s,%s\n' \
      "$format" "$position" "$seek_ms" "$reference_md5" "$decoded_md5" "$exact_match" \
      >> "$out_dir/seek-results.csv"
  done
done

rm -f "$out_dir/seek.raw"

printf 'mode,format,run,user_cpu_seconds,system_cpu_seconds,wall_seconds\n' > "$out_dir/cpu-results.csv"
for entry in "pcm:$out_dir/source.wav" "alac:$out_dir/source.m4a" "flac:$out_dir/source.flac"
do
  format="${entry%%:*}"
  path="${entry#*:}"
  for run in 1 2 3 4 5
  do
    values="$(ffmpeg -hide_banner -benchmark -i "$path" -f null - 2>&1 |
      sed -n 's/^bench: utime=\([0-9.]*\)s stime=\([0-9.]*\)s rtime=\([0-9.]*\)s$/\1,\2,\3/p')"
    printf 'single,%s,%s,%s\n' "$format" "$run" "$values" >> "$out_dir/cpu-results.csv"
  done

  for run in 1 2 3
  do
    values="$(ffmpeg -hide_banner -benchmark \
      -i "$path" -i "$path" -i "$path" -i "$path" \
      -filter_complex 'amix=inputs=4:normalize=0' -f null - 2>&1 |
      sed -n 's/^bench: utime=\([0-9.]*\)s stime=\([0-9.]*\)s rtime=\([0-9.]*\)s$/\1,\2,\3/p')"
    printf 'four_track,%s,%s,%s\n' "$format" "$run" "$values" >> "$out_dir/cpu-results.csv"
  done
done
