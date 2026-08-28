#!/usr/bin/env bash
set -euo pipefail

out_dir="${1:-bit-depth-benchmark}"
mkdir -p "$out_dir"

rate=48000
source_expr='sin(2*PI*440*t)*if(lt(t\,10)\,0.501187\,if(lt(t\,20)\,0.001\,if(lt(t\,30)\,0.0000316228\,if(lt(t\,40)\,0.00000316228\,if(lt(t\,50)\,0.000000316228\,0.0000000316228)))))'

ffmpeg -hide_banner -loglevel error -y \
  -f lavfi -i "aevalsrc=${source_expr}:s=${rate}:d=60" \
  -c:a pcm_f32le "$out_dir/source-f32.wav"

ffmpeg -hide_banner -loglevel error -y -i "$out_dir/source-f32.wav" \
  -af "aresample=osf=s16:dither_method=0" \
  -c:a pcm_s16le "$out_dir/pcm16-none.wav"

ffmpeg -hide_banner -loglevel error -y -i "$out_dir/source-f32.wav" \
  -af "aresample=osf=s16:dither_method=triangular" \
  -c:a pcm_s16le "$out_dir/pcm16-tpdf.wav"

ffmpeg -hide_banner -loglevel error -y -i "$out_dir/source-f32.wav" \
  -af "aresample=osf=s32:output_sample_bits=24:dither_method=0" \
  -c:a pcm_s24le "$out_dir/pcm24-none.wav"

ffmpeg -hide_banner -loglevel error -y -i "$out_dir/source-f32.wav" \
  -af "aresample=osf=s32:output_sample_bits=24:dither_method=triangular" \
  -c:a pcm_s24le "$out_dir/pcm24-tpdf.wav"

printf 'variant,wav_bytes,alac_bytes,pcm_md5,decoded_md5,lossless_roundtrip\n' > "$out_dir/storage.csv"
for wav_path in "$out_dir"/pcm*.wav
do
  name="$(basename "$wav_path" .wav)"
  alac_path="$out_dir/${name}.m4a"
  ffmpeg -hide_banner -loglevel error -y -i "$wav_path" -c:a alac "$alac_path"

  bits=24
  codec=pcm_s24le
  raw_format=s24le
  if [[ "$name" == pcm16-* ]]
  then
    bits=16
    codec=pcm_s16le
    raw_format=s16le
  fi

  original_md5="$(ffmpeg -hide_banner -loglevel error -i "$wav_path" -f "$raw_format" -c:a "$codec" - | md5sum | cut -d' ' -f1)"
  decoded_md5="$(ffmpeg -hide_banner -loglevel error -i "$alac_path" -f "$raw_format" -c:a "$codec" - | md5sum | cut -d' ' -f1)"
  roundtrip=no
  if [[ "$original_md5" == "$decoded_md5" ]]
  then
    roundtrip=yes
  fi

  printf '%s,%s,%s,%s,%s,%s\n' \
    "$name" "$(stat -c %s "$wav_path")" "$(stat -c %s "$alac_path")" \
    "$original_md5" "$decoded_md5" "$roundtrip" >> "$out_dir/storage.csv"
done

python3 "$(dirname "$0")/analyze_bit_depth.py" "$out_dir"
