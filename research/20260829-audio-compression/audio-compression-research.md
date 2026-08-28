# iPhone音楽アプリ：音声圧縮形式研究

更新日：2026-08-28

## 現段階の研究候補（仕様決定ではない）

- 演奏中の作業形式：`CAF + Float32 PCM / 48 kHz`
- 確定済み音声の圧縮候補：`24-bit整数PCMへ確定 → ALAC`
- DAW交換：`WAV 24-bit / 48 kHz`
- 軽量共有：`M4A + AAC-LC`
- 可逆交換：`FLAC`
- AAC、MP3、Opusをリアルタイム編集素材にはしない

4トラックを圧縮状態のままレンダーコールバック内で直接再生する案は不利。保存時はALAC、プロジェクトを開いたときはFloat32 PCMの作業キャッシュへ展開する案を検証対象にする。

## Float32と「可逆圧縮」の境界

ALACとFLACは整数PCMを可逆圧縮する。Float32の作業音声を直接渡すと、エンコーダー前で整数PCMへの変換が入る。今回使用したFFmpegでは、Float32入力がALAC／FLACとも24-bit整数として符号化された。

したがって「ALACだから作業中のFloat32まで完全に同一」という表現は誤り。正確には次の二段階になる。

1. Float32から24-bit整数PCMへの確定では量子化が起きる。
2. 確定後の24-bit整数PCMとALAC／FLACの往復はビット同一にできる。

演奏中のヘッドルームや処理途中の微小値を残す必要がある間はFloat32 PCMを保持する。ユーザーがテイクまたはレイヤーを確定した後だけ24-bitへ変換する。

## 合成素材による圧縮試験

条件：48 kHz、モノラル、60秒、Float32 PCM。測定環境はx86_64 Linux上のFFmpegであり、iPhone実機性能ではない。

| 素材 | Float32 PCM | ALAC | FLAC | AAC 192 kbps |
|---|---:|---:|---:|---:|
| ピンクノイズ | 11.52 MB | 7.53 MB（65.4%） | 7.53 MB（65.4%） | 1.46 MB |
| 加工ミックス | 11.52 MB | 6.91 MB（59.9%） | 6.91 MB（59.9%） | 1.46 MB |
| 単純な持続音 | 11.52 MB | 3.91 MB（33.9%） | 3.18 MB（27.6%） | 1.02 MB |
| 声に似せた帯域制限ノイズ | 11.52 MB | 6.22 MB（54.0%） | 6.12 MB（53.1%） | 1.46 MB |

可逆圧縮率は素材依存。予測しやすい持続音は大きく縮むが、ノイズやMicrocosm／Skulptur系の複雑な処理音は縮みにくい。プロジェクト容量計算では「ALACなら半分」と固定せず、元PCMの60〜70%を安全側の見積もりにする。

### 処理時間（参考値）

60秒素材1本に対する測定：

| 形式 | 符号化 | 復号 |
|---|---:|---:|
| ALAC | 0.34〜0.58秒 | 0.11〜0.28秒 |
| FLAC level 5 | 0.26〜0.47秒 | 0.11〜0.14秒 |
| AAC | 0.90〜4.15秒 | 0.27〜0.37秒 |

この時間は形式間の傾向を見るためのもの。iPhone上の実時間、発熱、電池消費は未検証。

## 可逆性の検証

加工ミックスを24-bit WAVへ変換し、そのWAVからALACとFLACを生成した。三形式を再び24-bit raw PCMへ復号したMD5はすべて次で一致した。

`fb92600b19b95ce3f3ed54e277eb372f`

この試験範囲では、24-bitへ確定した後のALAC／FLAC往復はビット同一。

## 16-bit／24-bit量子化試験

Float32の440 Hz正弦波を10秒ごとに−6、−60、−90、−110、−130、−150 dBFSへ切り替え、16-bitと24-bitへ量子化した。TPDFは三角分布ディザを加えた条件。差分はFFmpegのPSNR表示ではなく、WAVサンプルをFloat64へ正規化して直接計算した。

| 形式 | −90 dBFSのSNR | −110 dBFSのSNR | −130 dBFSのSNR | 量子化誤差／雑音床 |
|---|---:|---:|---:|---:|
| 16-bit・ディザなし | 9.5 dB | 0 dB・全サンプル消失 | 0 dB・全サンプル消失 | 約−101 dBFS |
| 16-bit・TPDF | 3.3 dB | −16.6 dB | −36.6 dB | 約−96.4 dBFS |
| 24-bit・ディザなし | 50.3 dB | 30.3 dB | 10.5 dB | 約−143 dBFS |
| 24-bit・TPDF | 48.5 dB | 28.5 dB | 8.5 dB | 約−141.5 dBFS |

16-bitは通常の完成音配布には使えるが、非常に小さい残響、フィードバック、粒子化素材を再加工する保存形式としては情報を早く失う。24-bitは−110 dBFSの信号も明確に残した。Strymon、Microcosm、Dedalus、Skulptur系の減衰尾部を後から増幅・再循環させる用途では差が出る。

60秒・モノラルの合成素材に対する容量：

| 形式 | PCM | ALAC |
|---|---:|---:|
| 16-bit・ディザなし | 5.76 MB | 0.45 MB |
| 16-bit・TPDF | 5.76 MB | 0.76 MB |
| 24-bit・ディザなし | 8.64 MB | 3.40 MB |
| 24-bit・TPDF | 8.64 MB | 3.49 MB |

この合成音は長い低レベル区間を含むため、実録音より圧縮しやすい。容量の一般値には使わない。全4条件で、量子化後PCMとALAC復号後PCMのMD5は一致した。

ディザは量子化歪みを雑音へ変えるが、その後さらに編集する中間素材へ毎回加えると雑音を重ねる。候補運用は、作業中はFloat32、確定保存で24-bit化するときに一度だけTPDF、または最終WAV書き出し時だけディザ、の二案。実機素材の差分試聴で選ぶ。

## アプリ内の流れ

1. マイク、内部音声、他アプリ入力をFloat32 PCMへ統一する。
2. 録音中はCAFへ追記し、4トラックの直接操作はPCM上で行う。
3. 波形編集、逆再生、粒子化、Skulptur処理はサンプル位置を直接参照する。
4. プロジェクトを閉じるとき、確定済みテイクだけ24-bit化してALACへ圧縮する。
5. 非破壊編集情報とエフェクト状態は音声へ焼き込まず、別のプロジェクト記録へ保持する。
6. 再度開くときはALACをFloat32作業キャッシュへ展開する。
7. 共有時だけAACを生成する。AACから編集用素材へ戻さない。

## iPhone実機で残る試験

- iPhone 13 mini相当で4トラックを同時展開したときの時間とメモリ
- ALAC保存中に録音、再生、Skulptur処理を継続した場合の音切れ
- 1分、10分、30分録音時の発熱と電池消費
- アプリ強制終了、着信、容量不足時のCAF復旧率
- iPhoneマイク、Bluetooth入力、内部音声それぞれの実素材圧縮率
- 24-bit量子化前後の差分測定と試聴
- FLAC書き出しをApple標準経路だけで実装できる範囲の確認

## 録音中断・破損試験

60秒の同一素材を4形式へ書き出し、ファイルの末尾を段階的に切断して復号できた時間を測定した。これはFFmpegによるコンテナ試験であり、iOSの`AVAudioFile`による実機試験ではない。

| 残存率 | CAF + Float32 PCM | 通常ALAC/M4A | CAF + ALAC | 2秒断片ALAC/fMP4 |
|---:|---:|---:|---:|---:|
| 25% | 15.0秒 | 0秒 | 0秒 | 14.9秒 |
| 50% | 30.0秒 | 0秒 | 0秒 | 30.0秒 |
| 75% | 45.0秒 | 0秒 | 0秒 | 45.0秒 |
| 95% | 57.0秒 | 0秒 | 0秒 | 57.0秒 |
| 99% | 59.4秒 | 0秒 | 0秒 | 59.4秒 |
| 100% | 60.0秒 | 60.0秒 | 0秒* | 60.0秒 |

通常のM4Aは末尾の`moov`が完成しないと読めず、Float32 PCMのCAFは残っている音声データにほぼ比例して回収できた。

`*` CAF内ALACは再現試験で、FFmpegが成功終了したにもかかわらず完成ファイルから必須のPacket Tableが欠け、100%のファイルも復号不能になった。先行の単発試験では読めた結果と矛盾するため、この形式の回収性能は判定不能。少なくとも今回のFFmpeg経路は採用しない。

断片化MP4は部分復号できた。Appleも`AVAssetWriter`の断片化されたMPEG-4について、クラッシュ等で中断されても書き込み済み断片へアクセスできる構造と説明している。ただしAppleの公開例はHLS用であり、このアプリのローカル録音形式としてALACを使えるか、サンプル単位編集と両立するかは未検証。そのため中核形式にはまだ採用しない。

### 保存トランザクション

録音停止後の圧縮は次の順序にする。

1. `take-UUID.recording.caf`へのPCM追記を終了する。
2. 読めるフレーム数を検査して`take-UUID.pcm.caf`へ確定する。
3. `take-UUID.alac.tmp`へALACを書き出す。
4. ALACを24-bit PCMへ戻し、フレーム数とPCMハッシュを原本と照合する。
5. 合格した一時ファイルだけ`take-UUID.m4a`へ原子的に改名する。
6. PCM原本は即時削除せず、次回の正常起動または容量管理まで保持する。

途中で落ちた場合は、完成済みALACではなく`*.recording.caf`を回収対象にする。圧縮と原本削除を同じ処理にしない。

### 開いたプロジェクトでの扱い

- 短い4トラックループ：ALACからFloat32へ全展開して演奏する。
- 長い録音：全展開せず、数秒単位のPCMリングキャッシュを使う。
- 逆再生や粒子化を触り始めた領域：先読みしてPCM化する。
- 圧縮、ファイル読み込み、ハッシュ計算をオーディオレンダーコールバック内で行わない。

## 再保存劣化とループ境界試験

24-bit PCMの決定論的な20秒合成音を、ALACまたはAAC 192 kbpsへ符号化し、24-bit PCMへ戻す処理を10世代繰り返した。AACはFFmpeg標準エンコーダーによる結果で、AppleのAACエンコーダー実機結果ではない。

| 形式・世代 | 復号フレーム | 元との差 | 元音とのSNR | 最大サンプル誤差 |
|---|---:|---:|---:|---:|
| ALAC 1回 | 960,000 | 0 | 完全一致 | 0 |
| ALAC 5回 | 960,000 | 0 | 完全一致 | 0 |
| ALAC 10回 | 960,000 | 0 | 完全一致 | 0 |
| AAC 1回 | 960,512 | +512 | 62.2 dB | 0.0228 |
| AAC 5回 | 960,512 | +512 | 53.2 dB | 0.0743 |
| AAC 10回 | 960,512 | +512 | 50.5 dB | 0.1212 |

AACは同じ設定で保存し直すたびに誤差が増えた。圧縮済みAACを再編集し、再びAACへ保存する世代劣化を実測できた。ALACは10世代後も24-bit PCMと同一だった。

別に、480 Hzを基礎とする10秒の完全周期波形でループ境界を測った。

| 形式 | 復号フレーム | 元との差 | SNR | 指定長へ切った後の境界誤差 |
|---|---:|---:|---:|---:|
| ALAC | 480,000 | 0 | 完全一致 | 0 |
| AAC 192 kbps | 480,256 | +256 | 58.4 dB | 0.02343（約−32.6 dBFS） |

このFFmpeg経路では、AACを元の480,000フレームへ切り戻しても境界サンプルに誤差が残った。短いクロスフェードでクリックを隠せる可能性はあるが、それは元のループを正確に保存したことにはならない。

この結果は、AACを完成ミックスの共有や試聴用に置き、直接触るループ、再録音される素材、フィードバックへ戻す素材から外す根拠になる。Apple実機エンコーダーは未検証。

## AACビットレート別・ステレオ試験

最初にモノラルで128／192／256／320 kbpsを指定したところ、FFmpegが192 kbps以上を約140 kbpsへ制限したため、その比較値は採用しなかった。左右で異なる決定論的合成音を使ったステレオ条件で再試験し、ファイルが実際に持つビットレートも取得した。

| 指定値 | 実効値・1世代目 | 1回後SNR | 10回後SNR | 10世代での低下 | ループ境界誤差 |
|---:|---:|---:|---:|---:|---:|
| 128 kbps | 129.7 kbps | 30.5 dB | 23.3 dB | 7.2 dB | 0.02805 |
| 192 kbps | 193.1 kbps | 38.0 dB | 28.3 dB | 9.8 dB | 0.02461 |
| 256 kbps | 252.3 kbps | 44.0 dB | 31.7 dB | 12.3 dB | 0.01591 |
| 320 kbps | 264.4 kbps | 61.6 dB | 49.8 dB | 11.8 dB | 0.01052 |

FFmpegのAACエンコーダーでは320 kbps指定も約264 kbpsで頭打ちになった。ビットレートを上げると一世代目の平均誤差とループ境界誤差は減ったが、どの条件でも次は残った。

- 20秒素材の復号結果が512フレーム増えた。
- 10秒ループの復号結果が256フレーム増えた。
- 10世代の再保存でSNRが7.2〜12.3 dB低下した。
- 最高条件でもループ境界はALACのような完全一致にならなかった。

したがって、ビットレートを上げてもAACが可逆編集形式へ変わるわけではない。一方、ここでのSNRは合成信号とのサンプル差であり、そのまま人間の知覚品質評点にはならない。共有用AACの候補値は、Apple実機エンコーダーと実際のミックスによるブラインド試聴を経て選ぶ。

## ALAC／FLACの長尺アクセス試験

48 kHz・24-bit・ステレオの決定論的合成音を120秒へ反復し、PCM、ALAC、FLAC（FFmpeg圧縮レベル5）を比較した。CPU時間はFFmpeg自身の`-benchmark`で取得し、利用者CPU時間とシステムCPU時間の合計の中央値を示す。壁時計時間はストレージキャッシュや同時実行の影響を受けるため、同じPC内の相対値としてのみ扱う。

| 形式 | 容量 | PCM比 | 単独復号CPU時間 | 4トラック復号CPU時間 | 単独の壁時計時間 | 4トラックの壁時計時間 |
|---|---:|---:|---:|---:|---:|---:|
| 24-bit PCM | 34,560,102 bytes | 100.0% | 0.355秒 | 1.524秒 | 0.312秒 | 1.676秒 |
| ALAC | 20,004,182 bytes | 57.9% | 0.444秒 | 1.806秒 | 0.168秒 | 0.786秒 |
| FLAC | 12,492,308 bytes | 36.1% | 0.216秒 | 0.880秒 | 0.086秒 | 0.442秒 |

5、30、60、90、115秒地点から各1秒を入力側シークで復号し、24-bit PCM原本とMD5を比較した。PCM、ALAC、FLACの全15件が完全一致した。この素材とFFmpeg 6.1.1では、長尺途中アクセスによるサンプルずれは観測されなかった。

今回のPC試験ではFLACが容量と復号CPU時間の両方でALACを下回った。ただし、これはiPhone上のAudioToolbox／AVFoundation経路、実機の電力、メモリ圧、同時録音中の負荷を測った結果ではない。したがってFLAC採用の決定にはせず、実機で同じ4トラック試験を行う根拠に留める。

最初の一回だけ、FLACレベル5の出力が3,932,160 bytesで途切れ、復号エラーになった。同じ入力でレベル1〜8を再生成すると全件正常で、レベル5も12,492,308 bytesで再現しなかった。原因は判定不能。壊れたファイルを高速な復号結果として数えないよう、ベンチマークへ全体復号による整合性検査を追加した。この一回をFLAC形式一般の欠陥とは判定しない。

## iPhone実機試験の実装

PC上のFFmpeg結果をiPhone性能へ読み替えないため、Appleの`AVAudioFile`で同じ120秒素材を読むXCTestを作成した。Appleの現行APIにはFLACを示す`kAudioFormatFLAC`があり、`AVAudioFile(forReading:commonFormat:interleaved:)`はファイル内の形式を指定した処理用PCM形式へ変換して読み出す。試験ではPCM、ALAC、FLACをすべて非インターリーブInt32 PCMとして読み、比較経路を揃える。

実装した測定は次の三つ。

- 1ファイルの全復号を各5回測定する。
- 4個の独立した`AVAudioFile`を並列に全復号し、各形式3回測定する。
- 5、30、60、90、115秒から各1秒を読み、PCMを基準にALAC／FLACのSHA-256を照合する。

XCTestの`XCTClockMetric`、`XCTCPUMetric`、`XCTMemoryMetric`を別々に記録する。容量、経過時間、CPU、メモリ、サンプル一致を一つの「性能」へ潰さず判定できる構造にした。

現在の作業環境にはSwift、Xcode、iOS SDK、接続済みiPhoneがない。したがって、テストコードと手順は作成済みだが、コンパイル、実機性能、実機でのFLAC読込み、発熱は未検証。形式選定はこの結果が得られるまで保留する。

## 一次資料

- [Apple Core Audio Format Specification](https://developer.apple.com/library/archive/documentation/MusicAudio/Reference/CAFSpec/CAF_spec/CAF_spec.html)
- [Apple Core Audio Essentials](https://developer.apple.com/library/archive/documentation/MusicAudio/Conceptual/CoreAudioOverview/CoreAudioEssentials/CoreAudioEssentials.html)
- [Apple: Encoding and decoding audio](https://developer.apple.com/documentation/audiotoolbox/encoding-and-decoding-audio)
- [Apple: kAudioFormatFLAC](https://developer.apple.com/documentation/coreaudiotypes/kaudioformatflac)
- [Apple: AVAudioFile reading with a common PCM format](https://developer.apple.com/documentation/avfaudio/avaudiofile/init(forreading:commonformat:interleaved:))
- [Apple: AVAudioFile read(into:frameCount:)](https://developer.apple.com/documentation/avfaudio/avaudiofile/read(into:framecount:))
- [Apple: XCTest Performance Tests](https://developer.apple.com/documentation/xctest/performance-tests)
- [RFC 9639: Free Lossless Audio Codec](https://www.rfc-editor.org/rfc/rfc9639.html)
- [RFC 6716: Definition of the Opus Audio Codec](https://www.rfc-editor.org/rfc/rfc6716.html)

## 再現用ファイル

- `compression_benchmark.sh`：合成音生成、ALAC／FLAC／AAC変換、容量・処理時間測定
- `compression-benchmark/results.csv`：測定生データ
- `crash_recovery_benchmark.sh`：CAF、通常M4A、CAF内ALAC、断片化MP4の切断回収試験
- `crash-recovery-benchmark/results.csv`：切断試験の測定生データ
- `bit_depth_benchmark.sh`：16-bit／24-bit、ディザ有無、ALAC容量、可逆性試験
- `analyze_bit_depth.py`：WAVサンプル差分による誤差とSNRの計算
- `bit-depth-benchmark/storage.csv`：容量とALAC往復MD5
- `bit-depth-benchmark/quality.csv`：レベル別の誤差、SNR、非ゼロサンプル率
- `generation_loop_benchmark.sh`：ALAC／AACの10世代再保存とループ境界試験
- `analyze_generation_loop.py`：フレーム数、SNR、最大誤差、境界誤差の計算
- `generation-loop-benchmark/generation-results.csv`：世代別の劣化測定
- `generation-loop-benchmark/loop-results.csv`：ループ長と境界誤差の測定
- `aac_bitrate_benchmark.sh`／`analyze_aac_bitrate.py`：モノラル試験。高ビットレートが実効約140 kbpsへ制限されたことの検出用
- `aac_stereo_benchmark.sh`／`analyze_aac_stereo.py`：ステレオAACの128／192／256／320 kbps、10世代、ループ境界比較
- `aac-stereo-benchmark/generation-results.csv`：指定値と実効値、世代劣化
- `aac-stereo-benchmark/loop-results.csv`：実効値、フレーム増加、ループ境界誤差
- `lossless_access_benchmark.sh`：120秒・24-bitステレオの容量、復号CPU、4トラック同時復号、途中シーク試験
- `lossless-access-benchmark/decode-results.csv`：容量と壁時計による復号時間
- `lossless-access-benchmark/cpu-results.csv`：単独5回、4トラック3回のCPU時間と壁時計時間
- `lossless-access-benchmark/seek-results.csv`：5地点のシーク時間と24-bit PCM MD5一致判定
- `ios-lossless-benchmark/LosslessDecodeBenchmarks.swift`：AVAudioFileによるiPhone実機XCTest
- `ios-lossless-benchmark/README.md`：実機への組込み、条件固定、測定手順
- `ios-lossless-benchmark/ios-results-template.csv`：機種、iOS、熱状態、CPU、時間、メモリ、シーク一致の記録欄
