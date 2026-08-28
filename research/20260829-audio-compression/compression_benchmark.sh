#!/usr/bin/env bash
set -euo pipefail

out_dir="${1:-compression-benchmark}"
mkdir -p "$out_dir"

duration=60
rate=48000

ffmpeg -hide_banner -loglevel error -y \
  -f lavfi -i "sine=frequency=110:sample_rate=${rate}:duration=${duration}" \
  -af "volume=0.7,afade=t=in:d=0.02,afade=t=out:st=59.98:d=0.02" \
  -c:a pcm_f32le "$out_dir/tonal.wav"

ffmpeg -hide_banner -loglevel error -y \
  -f lavfi -i "anoisesrc=color=pink:sample_rate=${rate}:duration=${duration}:amplitude=0.45" \
  -c:a pcm_f32le "$out_dir/noise.wav"

ffmpeg -hide_banner -loglevel error -y \
  -f lavfi -i "anoisesrc=color=pink:sample_rate=${rate}:duration=${duration}:amplitude=0.7" \
  -af "highpass=f=90,lowpass=f=6500,acompressor=threshold=-24dB:ratio=3:attack=5:release=80,tremolo=f=4:d=0.75" \
  -c:a pcm_f32le "$out_dir/voice_proxy.wav"

ffmpeg -hide_banner -loglevel error -y \
  -f lavfi -i "sine=frequency=55:sample_rate=${rate}:duration=${duration}" \
  -f lavfi -i "sine=frequency=173:sample_rate=${rate}:duration=${duration}" \
  -f lavfi -i "anoisesrc=color=pink:sample_rate=${rate}:duration=${duration}:amplitude=0.12" \
  -filter_complex "[0:a]tremolo=f=0.7:d=0.6[a0];[1:a]tremolo=f=3.7:d=0.8[a1];[a0][a1][2:a]amix=inputs=3:normalize=0,alimiter=limit=0.9" \
  -c:a pcm_f32le "$out_dir/processed_mix.wav"

printf 'source,format,bytes,encode_seconds,decode_seconds\n' > "$out_dir/results.csv"

for source_path in "$out_dir"/*.wav
do
  source_name="$(basename "$source_path" .wav)"
  pcm_bytes="$(stat -c %s "$source_path")"
  printf '%s,pcm_f32_wav,%s,0,0\n' "$source_name" "$pcm_bytes" >> "$out_dir/results.csv"

  for format in alac flac aac
  do
    case "$format" in
      alac)
        output_path="$out_dir/${source_name}.m4a"
        codec_args=(-c:a alac)
        ;;
      flac)
        output_path="$out_dir/${source_name}.flac"
        codec_args=(-c:a flac -compression_level 5)
        ;;
      aac)
        output_path="$out_dir/${source_name}.aac.m4a"
        codec_args=(-c:a aac -b:a 192k)
        ;;
    esac

    start_ns="$(date +%s%N)"
    ffmpeg -hide_banner -loglevel error -y -i "$source_path" "${codec_args[@]}" "$output_path"
    end_ns="$(date +%s%N)"
    encode_seconds="$(awk -v start="$start_ns" -v end="$end_ns" 'BEGIN { printf "%.3f", (end-start)/1000000000 }')"

    start_ns="$(date +%s%N)"
    ffmpeg -hide_banner -loglevel error -y -i "$output_path" -f null -
    end_ns="$(date +%s%N)"
    decode_seconds="$(awk -v start="$start_ns" -v end="$end_ns" 'BEGIN { printf "%.3f", (end-start)/1000000000 }')"
    output_bytes="$(stat -c %s "$output_path")"
    printf '%s,%s,%s,%s,%s\n' "$source_name" "$format" "$output_bytes" "$encode_seconds" "$decode_seconds" >> "$out_dir/results.csv"
  done
done
