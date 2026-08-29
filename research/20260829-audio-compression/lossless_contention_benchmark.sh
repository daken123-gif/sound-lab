#!/usr/bin/env bash
set -euo pipefail

source_dir="${1:-lossless-access-benchmark}"
out_dir="${2:-lossless-contention-benchmark}"
mkdir -p "$out_dir"

pcm="$source_dir/source.wav"
results="$out_dir/results.csv"
printf 'format,mode,run,user_cpu_seconds,system_cpu_seconds,wall_seconds,max_rss_kb\n' > "$results"

metrics_from_log() {
  sed -n 's/^bench: utime=\([0-9.]*\)s stime=\([0-9.]*\)s rtime=\([0-9.]*\)s$/\1,\2,\3/p' <<< "$1"
}

rss_from_log() {
  sed -n 's/^bench: maxrss=\([0-9]*\)kB$/\1/p' <<< "$1"
}

for descriptor in 'alac:alac:m4a' 'flac:flac:flac'
do
  IFS=: read -r format codec extension <<< "$descriptor"
  compressed="$source_dir/source.$extension"
  encode_options=(-c:a "$codec")
  if [[ "$format" == flac ]]
  then
    encode_options+=(-compression_level 5)
  fi

  for run in 1 2 3 4 5
  do
    log="$(ffmpeg -hide_banner -benchmark -i "$pcm" -map 0:a \
      "${encode_options[@]}" -f null - 2>&1)"
    printf '%s,encode_codec_only,%s,%s,%s\n' \
      "$format" "$run" "$(metrics_from_log "$log")" \
      "$(rss_from_log "$log")" >> "$results"
  done

  for run in 1 2 3
  do
    log="$(ffmpeg -hide_banner -benchmark \
      -i "$compressed" -i "$compressed" -i "$compressed" -i "$compressed" \
      -filter_complex '[0:a][1:a][2:a][3:a]amix=inputs=4:normalize=0[mix]' \
      -map '[mix]' -f null - 2>&1)"
    printf '%s,four_decode,%s,%s,%s\n' \
      "$format" "$run" "$(metrics_from_log "$log")" \
      "$(rss_from_log "$log")" >> "$results"
  done

  for run in 1 2 3
  do
    log="$(ffmpeg -hide_banner -benchmark \
      -i "$compressed" -i "$compressed" -i "$compressed" -i "$compressed" \
      -i "$pcm" \
      -filter_complex '[0:a][1:a][2:a][3:a]amix=inputs=4:normalize=0[mix]' \
      -map '[mix]' -f null /dev/null \
      -map 4:a "${encode_options[@]}" -f null /dev/null 2>&1)"
    printf '%s,four_decode_plus_encode_codec_only,%s,%s,%s\n' \
      "$format" "$run" "$(metrics_from_log "$log")" \
      "$(rss_from_log "$log")" >> "$results"
  done
done
