# THE PIPE型 BODY / LEAD engines — 最小DSP試作

SOMA THE PIPEの公開説明にあるORPHEUSとFILTERRAの考え方を検証する、独立したオフラインDSP試作。

これはTHE PIPEの内部DSPの複製ではない。公開されていない係数や処理を推測で「再現済み」としない。声をピッチへ変換せず、入力波形そのものによって仮想共鳴体または動的フィルターを駆動する設計仮説を、実行可能なコードへしたもの。

## LEAD（FILTERRA仮説）

`lead-engine.js` は入力音を発振器へ置換しない。声量の高速／低速包絡と、隣接サンプル差分によるピッチ非依存の明るさ代理値を取り出し、安定型レゾナント・ローパスのカットオフとQを連続駆動する。

- `tone`: 基準カットオフ。
- `motion`: 包絡／明るさによる動きと共振量。
- `space`: 8〜37 msの短い残響層。

強入力ではQを逆方向へ戻す安全域を設けた。公開資料から正確なFILTERRA係数は取得できていないため、これは「動くフィルターを声で演奏する」核だけを分離した独自仮説である。SYNTH系のオクターブ層はまだ含めず、FILTERRA核と混同しない。

## 信号経路

```text
voice / breath / consonant
  -> DC・低域衝撃の整理
  -> 高速／低速を兼ねた包絡追従
  -> 入力波形を保った励振信号
  -> 共鳴体A（6モード）
  -> 共鳴体B（6モード、微小離調）
  -> BODYで混合
  -> dry音を少量混合
  -> tanh安全飽和
```

共鳴比の初期値は `[1, 9/8, 5/4, 3/2, 5/3, 2]`。THE PIPE公式の正確なORPHEUSモード比ではなく、ペンタトニックな関係を検証するための仮置き。

## 三つの演奏マクロ

- `size`: 共鳴体の基音。大きいほど低くなる。
- `decay`: 共鳴が残る時間。
- `body`: 二つ目の共鳴体の比率と混合量。

安全・比較用に `dry` と `drive` も持つが、画面へ常時出す前提ではない。

## 実行

Node.js 18以降:

```sh
cd prototype/body-engine
npm test
npm run render-demo
```

`BodyEngine.process(Float32Array)` は録音済みのモノラル音声を処理する。`processSample(number)` は将来AudioWorkletまたはiOSのリアルタイム音声コールバックへ移す境界。

## リアルタイム処理

- `body-realtime-core.js`: 音声コールバックから独立した可変ブロック処理。
- `body-worklet-processor.js`: Web Audioの `AudioWorkletProcessor` 接続部。
- processor名: `soma-body`。
- `size / decay / body / dry / drive`: ブロック単位制御。
- `gate`: サンプル単位制御。

`gate` を閉じても共鳴体をresetしない。新しいマイク入力だけを短く減衰させ、すでに鳴ったBODYの尾は自然減衰させる。固定128サンプルを前提にせず、渡された出力ブロック長を使う。

```js
await audioContext.audioWorklet.addModule("body-worklet-processor.js");
const body = new AudioWorkletNode(audioContext, "soma-body");
source.connect(body).connect(audioContext.destination);

body.parameters.get("gate").setValueAtTime(1, audioContext.currentTime);
body.parameters.get("gate").setValueAtTime(0, audioContext.currentTime + 1);
```

このコード例は接続構造であり、iPhone Safariでマイク許可、音声ルート、実時間発音を確認した記録ではない。

## ブラウザのマイクセッション

`body-browser-session.js` は次を固定する。

- `start()` を呼ぶまでマイク許可を要求しない。
- `start()` はユーザー操作のイベント内から呼ぶ前提。
- `echoCancellation / noiseSuppression / autoGainControl` は `ideal: false` として要求する。
- 未対応制約でマイク取得全体を失敗させない。
- `track.getSettings()` を取得し、要求値と実際値を別々に返す。
- AudioWorkletロード後も、出力先へ自動接続しない。
- `setMonitoring(true)` が呼ばれたときだけスピーカー／イヤホン出力へ接続する。
- `gate` は初期値0。
- 録音機能を持たず、自動録音もしない。
- `stop()` で全MediaStreamTrackを停止する。

W3C Media Capture仕様では、裸の制約値は理想値として扱われ、未知の制約はWebIDLで捨てられる。要求した音声処理OFFが実際に採用されたとは限らないため、`requested / supported / actual` を分離して保持する。

参照:

- https://www.w3.org/TR/mediacapture-streams/
- https://www.w3.org/TR/webaudio-1.1/

### iPhone向けマイク診断ページ

`mic-test.html` は最終UIではなく、実機でマイク取得と発音経路を分離確認する一画面の診断ページ。

- `MIC START` を押すまで `AudioContext` を作らず、マイク許可も要求しない。
- 出力は初期OFF。`MONITOR` を明示的にONにした場合だけ接続する。
- `HOLD VOICE GATE` は押している間だけ開き、指が外れた場合、割込み、画面離脱時には閉じる。
- 操作マクロは `SIZE / DECAY / BODY` だけを出す。
- 録音、ルーパー、自動再生を持たない。
- 診断欄は `requested / supported / actual` を表示するが、`deviceId / groupId` は表示しない。
- AudioWorkletが処理した入力とBODY出力のRMSを、波形ではなくdBFS数値で表示する。
- Node上でAudioWorklet実行環境を模擬し、processor登録、閉ゲート時の入力観測、開ゲート時のBODY発音を接続層まで検証する。
- 2秒以上レベル報告が来なければ `INPUT／BODY レベル報告なし` と表示し、Safari側の処理停止を数値0と混同しない。
- 開始失敗は段階と原因を保持し、`INSECURE_CONTEXT / MIC_PERMISSION_DENIED / MIC_NOT_FOUND / MIC_UNAVAILABLE / MIC_CONSTRAINT_FAILED / WORKLET_LOAD_FAILED` などを別コードで表示する。

W3C Web Audio API 1.1は、AudioNodeの入力処理と内部処理は出力接続の有無やAudioContextの最終出力へ到達するかにかかわらず、AudioContext時間に沿って継続すると規定する。このため、診断を動かす目的でスピーカー出力や無音Gainを自動接続しない。

マイク取得にはsecure contextが必要なため、`mic-test.html` と同じディレクトリのJavaScriptを保ったままHTTPSで配信して開く。`file://` で直接開いた結果は実機検証の証拠にしない。フィードバックを避けるため、`MONITOR` をONにする前にイヤホンまたは外部出力を使う。

配備前の欠品検査:

```sh
npm run verify-browser-assets
```

`mic-test.html` から通常のES module import、`script src`、AudioWorklet用 `new URL(..., import.meta.url)` を再帰的に辿る。現在必要な静的資産9件のどれかが欠ける、または診断ページのディレクトリ外を参照すると失敗する。これはHTTPS配備済み、Safariで取得可能、マイクが動作する、という検証ではない。

2026-08-28のNode基準測定では、48 kHz / 128 samplesで30秒分を132.25 msで処理し、実時間に対する処理時間比は0.00441だった。これは同じコード経路がオフラインで十分速いことだけを示す。iPhoneのCPU負荷、AudioWorkletスケジューリング、入出力レイテンシー、発熱は未測定。

## 録音WAVを処理する

```sh
node process-wav.js INPUT.wav OUTPUT.wav light
node process-wav.js INPUT.wav OUTPUT.wav deep
```

入力は16-bit integer PCMのWAV。モノラルはそのまま、ステレオは左右を平均してモノラル化する。元のサンプルレートを維持し、レベルを自動ノーマライズせずBODY処理後の値を書き出す。圧縮音声や32-bit float WAVは、形式変換を黙って行わずエラーにする。

録音処理用の `light / deep` は、合成デモより駆動量を低くしてある。合成試験入力では `light` がpeak 0.9142 / RMS 0.3737、`deep` がpeak 0.7351 / RMS 0.2429。声の強弱を飽和で潰さず、処理後の自動ノーマライズも行わないための初期値であり、人声での妥当性は未検証。

`render-demo.js` は外部音源や依存パッケージを使わず、母音フォルマント、子音に似た開始過渡、息ノイズを含む合成試験信号を作る。同じ入力を次の順に並べた `demo-output/body-comparison.wav` を生成する。

1. 合成入力
2. 軽いBODY: `size 0.42 / decay 0.26 / body 0.38`
3. 深いBODY: `size 0.78 / decay 0.70 / body 0.82`

各区間は0.55秒の無音で区切る。48 kHz、16-bit PCM、モノラル、全長12.65秒。

## 今回検証する範囲

- 無音入力が勝手に発振しない。
- インパルス後に共鳴が減衰する。
- 息に似た非周期ノイズでも発音する。
- 出力が有限値かつ `-1...1` 内に収まる。
- 異常入力や範囲外マクロで内部状態が壊れない。
- WAVのエンコード／デコードが量子化誤差内で往復する。
- 壊れたWAVと未対応形式を拒否する。

2026-08-28の合成試験結果:

| 区間 | 長さ | RMS | Peak |
|---|---:|---:|---:|
| 入力 | 3.85秒 | 0.1727 | 0.7200 |
| 軽いBODY | 3.85秒 | 0.4880 | 0.8200 |
| 深いBODY | 3.85秒 | 0.3758 | 0.8200 |

この差は処理が入力と異なることを示すが、音楽的に有効、THE PIPEに似ている、人声で機能する、という証明にはならない。

## まだ検証していない範囲

- 人間の録音音声による母音、子音、息の比較。
- iPhone実機の内蔵マイクとイヤホンマイク。
- iPhone SafariでのAudioWorklet実行、AVAudioEngine、AUv3への接続。
- 端末レイテンシー、CPU負荷、フィードバック耐性。
- THE PIPE実機との聴感比較。
- 4トラックField Looperへの統合。

次は同一の録音素材を原音・BODY処理後で保存し、`size / decay / body` の差が聴いて区別できるかを検証する。
