# Abbey Road Studios 機材・信号経路研究

- research-id: `20260828-abbey-road-equipment`
- 研究対象: Abbey Road Studiosの歴史的・現行機材、回路順序、空間処理、4トラックiPhone録音機への応用
- 更新日時: 2026-08-28
- 状態: 研究記録。製品への統合・実機検証は未実施
- 実装変更: なし

## 現在の問い

1. Abbey Roadらしい音は、どの機材名ではなく、どの信号経路から生じるか。
2. REDD、TG12345、RS124、RS56、J37、エコー室、プレートの役割を混同せず分離できるか。
3. 4トラックiPhone録音機へ移す場合、何を残し、何を省き、どの順序で処理するか。
4. iPhoneマイクのRAW音質を損なわず、演奏の強弱が回路の色へ変わる設計にできるか。

## 証拠区分

- **確認事実**: Abbey Road Studios、AMS Neve、Apple、Waves/Abbey Road共同マニュアルで取得できた内容。
- **計算**: 確認事実として公開された電圧・VU値をデジタル基準へ変換した値。
- **設計判断**: Field Looper / 4トラックiPhone録音機へ採用するための判断。原機の仕様とは主張しない。
- **未検証**: 回路図、実機測定、インパルス応答または聴感試験が不足している部分。

---

## 1. 研究の中心判断

Abbey Roadの音を一個の「ヴィンテージ・サチュレーター」として扱わない。

音色は、おおむね次の積として成立する。

1. 部屋とマイク配置
2. REDDまたはTGの入力増幅
3. 少数帯域のEQ
4. RS124またはTGダイナミクス
5. グループ／メイン段による再処理
6. チャンバーまたはプレートのセンド・リターン
7. J37などへの記録とバウンス
8. 必要に応じたRS56型の仕上げ

特定EQカーブ、真空管歪み、テープノイズを単独で足しても、この段間関係は再現されない。

---

## 2. 現行スタジオの機材配置

### Studio One

確認できた現行資料では、Studio Oneは2025年の改修後、84チャンネルのAMS Neve 88RS SP3Dを中核とする。大編成録音とイマーシブ制作を扱う現代的な構成であり、歴史的REDD卓を常設中核として使う部屋ではない。

### Studio Two

Studio Twoは2011年導入の60チャンネルAMS Neve 88RSを中核とする。歴史的空間、エコー室、プレート、マイク、アウトボードと、現代コンソールを組み合わせる。

### Studio Three

Studio ThreeはカスタムSSL G+を中心にしつつ、TG12345 Mk III、Neve 1081、Fairchild 660などの歴史的・外部機材へ接続できる。現代のルーティングと歴史的色付けを併存させる構成。

### Gatehouse / Penthouse

GatehouseではNeve BCM10/2 Mk2、PenthouseではDolby Atmosを含むデジタル制作環境が中心。現在のAbbey Roadを「1960年代の機材だけのスタジオ」と固定しない。

### 2026年の追加機材

Abbey Roadは2026年、100点を超える楽器・制作ツールを追加したと発表している。Teenage Engineering OP-1、SOMA、Hologram、Chase Bliss、OTO、Strymon、ヴィンテージ・シンセ、ドラムマシンなどが含まれる。これは本プロジェクトの他研究と接続するが、Abbey Road回路の代用品として一括しない。

---

## 3. REDD.17 / REDD.37 / REDD.51

### 確認事実

- REDDはRecord Engineering Development Departmentを指す。
- REDD.37は1958年設計、8入力・4出力。
- 製造はプロトタイプを含む3台で、Studio OneとStudio Twoのコントロールルームに置かれた。
- REDD.37はSiemens V72真空管アンプ群で駆動された。
- REDD.51ではREDD.47アンプを使用し、V72系より低歪み・高ヘッドルームになった。
- 低域EQは100 Hzのシェルフ。
- `Pop`高域ブーストは5 kHzのベル型。
- `Classic`は高域シェルフ。
- 高域カットは10 kHzのシェルフ。
- Abbey RoadはREDD.17をより強く色付き、REDD.37/.51を比較的整った音として説明している。
- 『Revolution 1』では楽器をREDD.51へ直接入力し、入力段の過負荷を歪みとして利用した。

### 推論

REDDの色は後段に一定量を加えるエフェクトではなく、入力レベル依存で変わる。弱い演奏は比較的きれいに残り、強い演奏だけが太く崩れる構造が必要。

### Field Looperへの採用

画面上ではREDD.37とREDD.51を別機種として選択させず、`VALVE`経路の`PUSH`で内部状態を移行する。

| PUSH | 設計上の内部状態 |
|---:|---|
| 0–30% | REDD.51型の低歪み領域 |
| 30–65% | REDD.51型を強く駆動 |
| 65–85% | V72型の色を増加 |
| 85–100% | REDD.37型の強い過負荷 |

暫定処理順:

`入力トリム → REDD.47型非線形段 → 100 Hz EQ → Classic/Pop高域 → V72型再増幅 → 出力補正`

### 暫定DSP値

以下は設計値であり、原機測定値ではない。

- 内部4倍オーバーサンプリング
- REDD.51型: 2次倍音を中心とした穏やかなソフトクリップ
- REDD.37型: 2次・3次倍音を増やした早めのソフトクリップ
- 120 Hz以下は駆動量を最大3 dB抑える
- バイパスとの聴感音量差を0.5 dB以内へ補正
- ノイズ／ハムは初期値ゼロ

低域抑制は、iPhoneマイクの風、接触音、机の振動をサチュレーションが過剰に増幅するのを防ぐための設計判断。

---

## 4. EMI TG12345

### 確認事実

- 24マイク入力、8出力、4エコーセンド、2 Cue/Foldback。
- 12個のマイク・カセットがあり、それぞれ2入力を持つ。
- 各チャンネルにコンプレッサー／リミッターを搭載した最初期のコンソール。
- REDDとの比較試験では、TGはよりクリーン、明るい、パンチがあり、高域に光沢があると評価された。
- 低域EQ: 50 Hz固定シェルフ。
- 高域ブースト: 5 kHz固定ベル。
- 高域カット: 10 kHz固定シェルフ。
- Presence: 500 Hz～10 kHz。
- コンプレッサー比率: 2:1。
- リミッター比率: 7:1。
- アタック: 1 ms固定。
- Recovery: 100 / 250 / 500 ms / 1 / 2 / 5秒。
- VCA出力を検出器へ戻すフィードバック型。
- 約1.5 V以下の小信号を持ち上げ、それ以上を抑える領域を持つ。
- マイク・カセットにはプリアンプ、Bass/Treble EQ、ダイナミクス、センド／リターン、Spread、Pan、Faderがあった。
- グループ・カセットにも別のダイナミクスとPresenceがあった。
- メイン・カセットにもテープ前のPresenceがあった。
- EQ、Presence、Dynamicsは機種・段により順序が変わる。
- Sidechain HP、Wet/Dry、Drive、Noiseは現代プラグインで追加された機能で、原卓そのものの仕様ではない。
- メーターの標準ヘッドルームは18 dB。

### 計算

資料の `0 dBFS = 13.875 V` と低レベル境界 `1.5 V` を使用する。

`20 log10(1.5 / 13.875) ≈ -19.3 dBFS`

`-18 dBFS = 0 VU`を内部基準とした場合、TGの小信号／大信号動作境界は約 `-1.3 VU`。

### Field Looperへの採用

`SOLID`経路は一個の強いサチュレーターではなく、軽い処理を二段に分ける。

`入力色 → 50 Hz EQ → 5 kHz/10 kHz EQ → フィードバック圧縮 → Presence → 軽いグループ段`

- 検出器は入力ではなく処理後出力を参照する。
- 通常は2:1。
- 7:1は強い演奏効果としてだけ使用する。
- UIでは`PUSH`と`RECOVER`へ集約する。
- 小信号上昇曲線の正確な形状は未取得。暫定的に-36～-19.3 dBFSで最大+3 dBとするが、実測値とは扱わない。
- ノイズ床付近では上昇を止める。

---

## 5. RS124 Compressor

### 確認事実

- 1960年代Abbey Roadの主要真空管コンプレッサー。
- Altec 436Bを大幅改造した機材。
- 個体ごとにアタック／リリースが異なった。
- 攻撃的な個体はトラッキング、穏やかな個体はバスやカッティングへ使われた。
- 長いアタックとリリース、大きなメイクアップゲインを持つ。
- 固定比率で、Inputが入力ゲインと逆向きThresholdを兼ねる。
- Inputを上げると圧縮量と出力が同時に増える。
- 約2～15 dBの圧縮域では、入力変化に対する出力変化がおよそ半分になる。
- Recoveryは1（速い）から6（遅い）の6段階。
- Auto Hold、Auto Makeup、SuperFuse、Sidechain HP、Wet/Dryは現代的な補助を含む。
- Auto Holdを常時使うと、RS124特有の挙動を弱める可能性がある。
- Studio型は60070Bの元の真空管による少し潰れた挙動。
- Cutter型は6AL5管の応答が遅い個体を反映する。
- HF Roll-OffはRS124出力をテープへ送ったときの高域低下を模す。

### Field Looperへの採用

独立したThresholdノブを置かない。

- `PUSH`: Input、圧縮量、メイクアップを連動
- `RECOVER`: 6段階を「速い／歌う／溶ける」の三領域へ束ねる
- Auto Hold相当は強い音が無音後に来た部分だけ補助し、常時オンにしない
- 自動出力補正で音量差による誤判定を減らす

### 未検証

各シリアルの正確な時定数は、今回取得した公開資料だけでは確定できない。数値を原機仕様として創作しない。

---

## 6. RS56 Universal Tone Control

### 確認事実

- 電源も増幅段も持たないパッシブEQ。
- Boostは対象帯域を増幅するのではなく、対象以外を減衰させることで作る。
- 3帯域を各+10 dBにできる原機では、基礎減衰が合計最大30 dBになる。
- Abbey Roadでは後段のV72アンプでメイクアップした。
- 原機は±10 dB、2 dB刻み。
- 3帯域、各4中心周波数、6形状。

| 帯域 | 中心周波数 |
|---|---|
| Bass | 32 / 64 / 128 / 256 Hz |
| Treble/Mid | 512 / 1024 / 2048 / 4096 Hz |
| Top | 5800 / 8192 / 11600 / 16400 Hz |

形状:

- Low shelf
- 非常に広いベル
- 中程度に広いベル
- 中程度に狭いベル
- 非常に狭いベル
- High shelf

1951～1970年には主にディスク・カッティング前の仕上げへ使われ、後に録音・ミックスでも使用された。

### Field Looperへの採用

一般的なデジタルEQの後へサチュレーターを足すのではなく、

`パッシブ損失のモデル → V72型再増幅 → 出力補正`

とする。

UIは`SHAPE`一つに集約するが、内部では原機の離散周波数を使用する。

- 下方向: 64～128 Hzの量感
- 中央: 中立
- 上方向: 4096 Hzおよび8192～11600 Hzの明瞭さ

RS56は各トラックの常時EQではなく、4トラック・サムまたはバウンス直前の仕上げへ置く。

---

## 7. Studer J37

### 確認事実

- 1インチ4トラック。
- 52本の真空管。
- 18 kHz付近までほぼ平坦な応答。
- Abbey Roadは1965年に4台を購入し、8トラック導入まで広く使用。
- 2台のJ37間でバウンスし、層を重ねる制作が行われた。
- EMI Tape 888: 初期60年代。粒子が粗く、1～8 kHzの歪みが多い。
- EMI Tape 811: 60年代中後期。888より高域が良く、歪みが少ない。
- EMI Tape 815: 70年代初期。さらに平坦で歪みが少ない。
- 15 ips: 高域特性が良く、THDが少ない。
- 7.5 ips: 高域は減るが低域が締まる。
- 推奨平均入力: -3～0 VU。
- 推奨ピーク上限: +1～+2 VU。
- テープ圧縮には通常のコンプレッサーのようなAttack/Release時定数がなく、通常のポンピングを起こさない。
- Input LevelとSaturationは別の制御で、同じ音にはならない。
- Wowはモーター速度変動による周波数変調。
- Flutterはヘッドに対するテープ移動による振幅変調。
- 異なるモデル・トラックを左右に使うと個体差でステレオ像が広がる。
- Noiseの標準値はOff。

### VUからdBFSへの変換

内部基準を `-18 dBFS = 0 VU` とした場合:

| J37値 | 内部デジタル値 |
|---|---:|
| 平均 -3 VU | -21 dBFS |
| 平均 0 VU | -18 dBFS |
| ピーク +1 VU | -17 dBFS |
| ピーク +2 VU | -16 dBFS |

RAW録音をこの小さい値へ固定するのではない。RAWから分岐したアナログ処理経路だけをこの基準へトリムし、処理後に出力を戻す。

### Field Looperへの採用

J37型処理は各トラックへの常時コーティングではなく、4トラックをまとめるバウンス処理へ置く。

| UI表示 | Formula | Speed | 性格 |
|---|---|---|---|
| 粗い | 888 | 7.5 ips | 中域歪み、暗さ |
| まとまる | 811 | 15 ips | 60年代後半の中心 |
| 澄む | 815 | 15 ips | 高域が平坦、歪みが少ない |

- `HIT`と`SAT`を分ける。
- Noise、Wow、Flutterは初期値ゼロ。
- バウンスを繰り返した場合だけ変化を累積する。
- 非破壊の元トラックは保持する。

---

## 8. BTR / その他のテープ機

Abbey Roadの歴史的機材にはBTR-2、Studer A80、A820なども含まれる。今回、J37ほど詳細な回路・伝達特性までは取得していない。機材名の存在と歴史的位置は記録するが、DSP仕様には未採用。

---

## 9. Studio Two Echo Chamber

### 確認事実

- Studio Twoのエコー室は、1960年代ポップ録音の特徴的な声の空間に使われた。
- Altec 605スピーカーで室内を鳴らし、Neumann KM53マイクで収音する構成が再現資料に示される。
- 実機の響きは短く密度が高い。
- S.T.E.E.D.はSend. Tape. Echo. Echo. Delay.の構成で、テープ・ディレイをエコー室と組み合わせた。
- チャンバーは現実の空気と反射を伴うため、滑らかで人工的なプレートとは異なる不規則性を持つ。

### 重要な経路訂正

初期案では空間処理をテープの後へ置いたが、通常の録音経路としては不適切だった。

修正後:

`各トラック → 空間センド → Chamber/Plate → ミックスへ戻す → マスター整形 → J37へ記録`

J37をディレイとして使うS.T.E.E.D.だけは、テープ遅延がチャンバー前段に入る別経路。

### Field Looperへの採用

実測インパルス応答を取得していないため、`Studio Twoそのもの`とは称さない。短く密度の高いアルゴリズム空間として作る。

暫定設計値:

- Decay: 0.7～1.4秒
- 不規則で明確な初期反射
- 高い後期密度
- 低域は速く減衰
- 6～8 kHzから緩やかに減衰
- 1960年代モードではモノ・リターン

---

## 10. EMT 140 Plate Reverbs

### 確認事実

- Abbey Roadの4台のEMT 140は1957年に導入。
- 四隅をスプリングで張った大きな金属板へトランスデューサーで音を入れ、2個の接触マイクで収音する。
- 内部ダンパーで残響時間を変更でき、最大約6秒。
- Plate A、B、CはEMI設計のハイブリッド・ソリッドステート駆動アンプ。
- Plate Dは駆動・出力とも真空管。
- 4台は経年変化も含めて同一の音ではない。
- プレートはチャンバーより滑らかで拡散が均質。金属的共鳴を持つ。

### Field Looperへの採用

- Decay: 暫定1.5～6秒
- 高拡散
- 初期反射を目立たせない
- 入力を120～180 Hzで整理
- Plate D型のみリターンに軽い真空管非線形処理
- 主にボーカル、スネア、単音シンセへ使用
- トラックごとに別インスタンスを作らず、共有バスとする

---

## 11. 空間系の操作

4トラックごとに持つのは空間への送り量だけ。チャンバーとプレート本体は共有する。

| SPACE | 内部状態 |
|---:|---|
| 0% | Dry |
| 1–40% | 短いチャンバー |
| 40–70% | チャンバーを保ちつつプレート追加 |
| 70–100% | プレートの長さと送りを増加 |

1960年代モードではリターンをモノ化し、音源と近い位置へ戻す。現代モードだけステレオ・リターンを許可する。

リバーブ入力にはHigh-pass / Low-passを置く。ボーカルの歯擦音、低域振動、接触音が残響を過剰に駆動しないよう、残響の前で整える。

---

## 12. iPhone入力経路

### 確認事実

Appleの`AVAudioSession.Mode.measurement`は、システムが入力／出力へ加える信号処理を最小化したい用途のモード。

### Field Looperへの採用

- RAW録音にはEQ、ノイズ除去、コンプレッサー、オートゲインをかけない。
- RAWと演奏用モニターを入力直後に分岐。
- アナログ処理側だけ基準レベルへ調整。
- 録音開始前の短い測定で入力トリムを決め、録音中は勝手に追従させない。
- 入力経路変更時は自動録音しない。
- `iPhoneマイク`、`有線入力`など、実際の入力名を明示。
- 未接続時は録音ボタンを動作させず、原因を表示する。
- Bluetooth経路とiPhone内蔵マイクを同一音質として扱わない。
- RAWを保持したまま、VALVE / SOLID / CLEANを後から変更可能にする。

---

## 13. 4トラック信号経路

```text
iPhone Mic / External Input
├── RAW file
└── Analog calibration (-18 dBFS = 0 VU)
    └── Track Path
        ├── CLEAN
        ├── VALVE (REDD.37 / REDD.51)
        └── SOLID (TG12345)
            ↓
        Track fader / pan
            ├── Dry sum
            └── Shared SPACE send
                ├── Short Chamber
                └── EMT-style Plate
                     ↓
                 Return to mix
                     ↓
              RS56-style passive master
                     ↓
                 J37-style bounce
                     ↓
               Output / new stereo file
```

各トラックの主要操作:

- `COLOR`: CLEAN / VALVE / SOLID
- `PUSH`: 入力駆動、倍音、圧縮を経路別に連動
- `RECOVER`: RS124またはTGの戻り方
- `SPACE`: 共通空間への送り量
- Fader / Pan / Mute / Solo / Record arm

マスターの主要操作:

- `SHAPE`: RS56型パッシブ整形
- `HIT`: J37へ入るレベル
- `SAT`: テープ媒体側の非線形量
- `BOUNCE`: 4トラックを新しいステレオまたはトラックへ確定

---

## 14. 採用しない点

- 「Abbey Road Warmth」という一個のつまみへ全機材を混ぜる。
- 全トラックへ常時同じテープ歪みをかける。
- ノイズ、ハム、ワウ、フラッターをヴィンテージ感の中心にする。
- 各トラックへ別々のリバーブ空間を置く。
- RS56を通常のピーキングEQとして代用する。
- TGの小信号上昇とフィードバック検出を捨て、一般的なfeed-forward compressorにする。
- RS124へ一般的なThreshold / Ratio / Attack / Releaseの四つをそのまま並べる。
- RAWへ破壊的に処理を書き込む。
- 入力が未接続でも自動的に録音を開始する。
- 公開資料のない時定数や伝達曲線を「実機と同じ」と表示する。
- 商標や外観を模倣し、Abbey Road公式製品であるように見せる。

---

## 15. 依存する他研究

- `20260828-iphone-mic-preamp`: iPhone入力品質、RAW分岐、マイク特性。
- Strymon空間研究: FDN、拡散、初期反射、高域減衰。ただしStudio Two/EMTの役割へ従属させる。
- コンプ研究: RS124と1192 Blackfaceなどの差分。固定比率、入力依存、回復挙動を混同しない。
- Chroma Console研究: 色付けのマクロ操作。ただしAbbey Road経路を単一Color macroへ潰さない。
- Loopy Pro / 4トラック研究: 録音、モニター、バウンス、非破壊保存。
- Teenage Engineering研究: 難しい回路を少数の演奏操作へ変換するUI思想。
- 統合研究: 本記録は研究段階であり、`integration/`へ採択されるまで製品の正本ではない。

---

## 16. 触る予定の実装パス

実装はこの研究ブランチでは未実施。統合時の候補:

- Audio session / input routing
- RAW recorder
- Per-track color path
- Feedback VCA dynamics
- RS124-style variable-mu behavior
- Passive-loss EQ and makeup stage
- Shared chamber / plate buses
- Tape bounce processor
- Level-matched bypass and metering

実際のパス名は統合ブランチのコード構造を確認するまで未確定。

---

## 17. 未検証事項

1. REDD.37 / REDD.51実機の入力レベル別高調波分布。
2. V72とREDD.47の正確な伝達曲線、帯域別飽和。
3. TG12345の1.5 V以下における上昇圧縮曲線。
4. TG Holdの操作量と実際の利得変化範囲の対応。
5. RS124各シリアルのAttack / Recovery時定数。
6. RS56の6形状それぞれの正確なQと位相。
7. J37のFormula / Speed / Bias別ヒステリシスと高調波。
8. Studio Two Echo Chamberの実測IR、寸法、マイク／スピーカー位置差。
9. 4台のEMT 140の個体別IRと駆動アンプ差。
10. iPhone実機でのCPU負荷、遅延、4倍オーバーサンプリングの電力消費。
11. 内蔵マイク、有線入力、Bluetooth入力でのレベル基準差。
12. 実際の声、打楽器、環境音を使ったバイパス音量一致試験。

---

## 18. 一次資料

### Abbey Road Studios

- Historic Gear & Instruments  
  https://www.abbeyroad.com/gear-instruments
- REDD.37 Desk #GearThatMadeUs  
  https://www.abbeyroad.com/news/redd37-desk-gearthatmadeus-3172
- REDD.17 Desk #GearThatMadeUs  
  https://www.abbeyroad.com/news/redd17-desk-gearthatmadeus-3123
- Behind Abbey Road Studios' EMI TG12345 Console  
  https://www.abbeyroad.com/news/behind-abbey-road-studios-emi-tg12345-console-2604
- BTR-2 #GearThatMadeUs  
  https://www.abbeyroad.com/news/btr-2-gearthatmadeus-3175
- Inside the Waves Abbey Road Chambers Plugin  
  https://www.abbeyroad.com/news/inside-the-waves-abbey-road-chambers-plugin-2412
- How To Use Abbey Road's Plate And Chamber Reverb  
  https://www.abbeyroad.com/news/how-to-use-abbey-roads-plate-and-chamber-reverb-effectively-in-your-music-2585
- How To Achieve The '60s Sound  
  https://www.abbeyroad.com/news/how-to-achieve-the-60s-sound-waves-audio-x-abbey-road-studios-2562
- Tyler Childers at Abbey Road: EMT plates and Studio Two chamber  
  https://www.abbeyroad.com/news/tyler-childers-rustin-in-the-rain-at-abbey-road-3418
- Studio Three gear tour  
  https://www.abbeyroad.com/news/abbey-road-rooms-studio-three-with-freddie-light-3443
- Studio One reopening / 88RS SP3D  
  https://www.abbeyroad.com/news/visionary-dance-fusion-for-the-reopening-of-studio-one-3494
- 2026 comprehensive gear collection  
  https://www.abbeyroad.com/news/introducing-the-most-comprehensive-gear-collection-in-our-history-3574

### Waves / Abbey Road共同マニュアル

- TG12345 User Guide  
  https://assets.wavescdn.com/pdf/plugins/tg12345.pdf
- RS124 User Guide  
  https://assets.wavescdn.com/pdf/plugins/rs124-v16-update.pdf
- RS56 User Guide  
  https://assets.wavescdn.com/pdf/plugins/rs56.pdf
- J37 User Guide  
  https://assets.wavescdn.com/pdf/plugins/j37-tape.pdf

### AMS Neve

- Studio Two 88RS  
  https://www.ams-neve.com/worlds-most-famous-studio-specs-neve-88rs/
- Abbey Road Gatehouse consoles  
  https://www.ams-neve.com/abbey-road-selects-two-ams-neve-consoles-for-new-studios/

### Apple

- AVAudioSession.Mode.measurement  
  https://developer.apple.com/documentation/avfaudio/avaudiosession/mode-swift.struct/measurement
- AVAudioNode.installTap  
  https://developer.apple.com/documentation/avfaudio/avaudionode/installtap(onbus:buffersize:format:block:)

---

## 19. 資料衛生

Chandler Limited公式ドメインとして検索された一部ページが、本研究時点では機材と無関係な内容へ汚染されていたため、資料として除外した。REDD.47の判断にはAbbey Road公式記事を使用した。

Waves共同マニュアルでは、原機の仕様とプラグイン追加機能を分けた。Sidechain HP、Wet/Dry、Drive、Noise、Auto Hold、SuperFuseなどを、無条件に歴史的ハードウェアの機能として扱っていない。

---

## 20. 現在位置

機材名の収集、歴史的役割、主要な公開仕様、段間レベル、4トラックへの信号経路変換までは記録済み。

まだ行っていないもの:

- DSPコード実装
- 実機または正規IRの測定
- iPhoneでの録音試験
- A/B音量一致試験
- CPU／遅延計測
- `integration/`への採択


---

## 21. 歴史的マイク・コレクション

### 確認事実

Abbey Roadの機材資料と技術者記事から、次の役割を確認した。

| マイク | 方式・特徴 | Abbey Roadで確認できた役割 |
|---|---|---|
| Neumann U47 / U48 | 真空管ラージダイアフラム・コンデンサー | 歌手、各種ポップ録音。U48のFigure-8を複数歌手の同時収音へ利用 |
| AKG C12 | 真空管コンデンサー、高感度 | ベースアンプ、弦、ピアノ、オーケストラのアウトリガー、ダブルベース、ボーカル |
| AKG D20 | ダイナミック | 1960年代のキックドラム |
| AKG D19 / D19c | ダイナミック | Ringo Starrのドラム・オーバーヘッド、場合によりトークバック |
| STC 4038 | リボン、Figure-8 | 初期Beatles録音の単一ドラム・オーバーヘッド |
| RCA 44-BX | リボン | 歌、ブラス、汎用。滑らかで暖かい出力 |
| Neumann U67 | 真空管コンデンサー | 現代Abbey Roadのドラム・オーバーヘッド例 |
| Neumann M50 | 小球型圧力マイク／無指向性運用 | 現代のドラム・ルーム、オーケストラ系の空間収音 |
| Neumann KM84 | スモールダイアフラム・コンデンサー | ハイハットなど。Fairchildへ強く送った特殊なドラム処理例 |

Abbey Roadでは1950年代からNeumann U47/U48を多数使用してきた。技術者Lester Smithは、U47の真空管増幅が有用な歪みを与えながら高域を明瞭にすると説明している。

AKG D20とD19は1965年頃から1970年代にかけて多くのポップ・セッションで使われた。D20はキック、D19はドラム・オーバーヘッドとして役割が分かれていた。

### マイク管理も信号経路の一部

Lester Smithの記録では、当時約450本、40種類のマイクを管理していた。各マイクを遮音箱とRS145 Acoustic Noise Generatorで一定距離から測定し、個体ごとのレベルを調整していた。

これは「同じ型番なら同じ音」と扱わず、個体の状態と出力差を校正していたことを示す。iPhone側でも、端末・入力経路ごとの校正を省いて固定プリセットだけを当てない。

---

## 22. マイク配置から分かったこと

### C12とベースアンプ

Geoff Emerickは『Sgt. Pepper』期のベース・オーバーダブで、AKG C12をアンプから通常の近接距離ではなく4～5フィート、場合によって約8フィート離した。Figure-8を使うこともあり、さらに遠い第二マイクを混ぜる場合もあった。

目的はアンプ単体の周波数特性ではなく、Studio Twoの「丸み」をベースへ含めることだった。

ここから得る設計判断:

- ベースの太さを低域EQだけで作らない。
- 直接音と部屋音の時間差を残す。
- 近接音へ人工的な低域を足す処理と、離れたマイクの空間色は別物。
- 小さな部屋で同じ距離を取ると悪い反射が増えるため、距離を固定値として強制しない。

### 初期ドラムの少数マイク

初期Beatles録音では、キックを除くドラム全体をSTC4038一本のオーバーヘッドで収めた例がある。リボンの暗い高域によって、明るく大きいシンバルと、暗く小さいタム／スネアをマイク内部のバランスとしてまとめた。

その後はAKG D19cがオーバーヘッドへ広く使われた。

ここで重要なのは「4038風EQ」ではなく、一本のマイク位置で演奏者が自分のバランスを作ること。各パーツを完全分離して後から混ぜる現代ドラム収録とは出発点が違う。

### 現代Abbey Roadのドラム

Abbey RoadのMatt Jonesは、U67などのオーバーヘッドを比較的低く置き、部屋音を増やしすぎない方法を述べている。別に無指向性ステレオのルーム・ペアを置き、必要な空間を独立して捕らえる。さらにFigure-8リボンのNullをシンバルへ向け、キックとスネアを中心に取る。

これは一個の「ドラム・プリセット」ではなく、

- オーバーヘッド: キット本体
- ルーム: 空間
- Figure-8リボン: シンバルを避けた胴鳴り
- Close: 打点

を別レイヤーとして扱う方法。

### U48と複数歌手

U48のFigure-8を利用し、マイクの前後へ歌手を配置して複数人のハーモニーを同時に収録した例がある。これは二方向の音を収めながら、側面Nullで不要な音を抑える使い方。

iPhone内蔵マイクにFigure-8の物理Nullを後処理で作ることはできない。単なるEQプリセットでU48を名乗らない。

---

## 23. iPhoneへ移すときの重要な分離

以前の`COLOR = CLEAN / VALVE / SOLID`はコンソール経路だけを選ぶものとして維持する。マイク特性をそこへ混ぜない。

```text
物理配置
→ iPhoneマイク／外部マイク
→ RAW
→ 入力校正
→ COLOR（REDD / TG / CLEAN）
→ ダイナミクス
→ SPACE
→ バウンス
```

マイク側で決まるもの:

- 音源からの距離
- 端末の向き
- 直接音と反射音の比率
- 部屋の初期反射
- 演奏者自身のバランス
- 端末／入力経路固有の周波数応答

後処理で変更できるもの:

- Tonal tilt
- 低域・高域の整理
- 軽い指向性風のフォーカス感
- 部屋音の追加
- REDD / TGの回路色
- 圧縮とテープ・バウンス

後処理で正確に復元できないもの:

- 収録時に失われた部屋の反射
- Figure-8の側面Null
- 複数マイク間の実時間差
- マイクカプセルの過渡応答
- 音源がマイク位置で自然に混ざったバランス

---

## 24. 収録前の三つの配置ガイド

UIへマイク型番を並べず、録音前だけ三つの配置意図を表示する。これは音声プリセットではなく、端末をどこへ置くかのガイド。

### CLOSE

用途: 声、単音、静かな音、小さい部屋。

- 声は口とマイクの軸を合わせる。
- 暫定距離15～30 cm。
- 破裂音を避けるため真正面からわずかに外す選択を許可。
- SPACEは少量から始める。
- U47/U48の名称はUIに出さない。

Abbey Roadの一般録音ガイドでも、コンデンサー・ボーカルは約10～30 cm、近接時でも約15 cm以上を目安とし、距離による低域以外の変化も聴くよう勧めている。

### ROOM

用途: アンプ、ベース、打楽器、演奏空間そのもの。

- まず1 m前後から試す。
- 良い部屋なら距離を増やす。
- 悪い小部屋では離しすぎない。
- RAWへ実在する反射を残し、後からチャンバーへ置換しない。
- C12を4～8フィート離した事例は参考だが、固定距離として強制しない。

### KIT

用途: ドラム、複数打楽器、机上オブジェクト。

- 個々の音を狙わず、全体のバランスが成立する一点を探す。
- シンバル／金属音が強い場合は端末を真正面へ向けない。
- 低域打楽器が消える場合は高さを下げる。
- 後処理の暗いTiltは補助であり、STC4038の物理挙動の再現とは称さない。
- 一つのトラックで「演奏されたミックス」を作る。

### UI制約

- 録音画面へ新しい常設ノブを追加しない。
- 配置ガイドは録音前に一度だけ開ける。
- 選ばなくても録音できる。
- 選択によって自動録音を開始しない。
- ガイド選択はRAWへ不可逆処理を行わない。

---

## 25. マイク研究から変わった設計判断

### 以前の判断

アビーロードの色を、コンソール、コンプレッサー、テープ、空間の順に構成していた。

### 追加後

その前に`物理配置`と`入力個体校正`を独立層として置く。

新しい順序:

`配置 → RAW → 校正 → REDD/TG → RS124/TG Dynamics → Chamber/Plate → RS56 → J37`

### 採用

- マイク型番プリセットではなく配置ガイド。
- 一本のマイクで全体をまとめる`KIT`。
- 近接音と部屋音を区別する`CLOSE / ROOM`。
- 入力端末ごとのレベル校正。
- RAWを常に保持。
- コンソール色とマイク色を分離。

### 採用しない

- `U47`、`C12`、`4038`という名称だけのEQプリセット。
- iPhoneマイクをFigure-8へ変換できるという表示。
- C12の4～8フィート配置を全室へ適用。
- ドラムを自動的に多マイク録音風へ変換。
- 端末距離を入力音量だけから正確に推定したと表示。
- マイク選択後の自動録音。
- 録音中の追従型AGC。

---

## 26. マイク研究の追加一次資料

- Abbey Road Historic Gear & Instruments — Microphones  
  https://www.abbeyroad.com/gear-instruments
- Abbey Road Microphone Collection — AKG C12  
  https://www.abbeyroad.com/news/abbey-road-microphone-collection-the-akg-c12-2906
- Brian Kehew & Kevin Ryan — STC4038 / AKG D19c drum overhead  
  https://www.abbeyroad.com/news/brian-kehew-kevin-ryan-answer-your-lectures-questions-2564
- Abbey Road Matt Jones — Recording Drums  
  https://www.abbeyroad.com/news/abbey-roads-matt-jones-on-recording-drums-productionhub-2695
- The Hollies — U48 Figure-8 harmony recording  
  https://www.abbeyroad.com/news/the-genius-of-the-hollies-as-told-by-abbey-roads-cameron-colbeck-3105
- Lester Smith's Abbey Road Story — microphone testing and inventory  
  https://www.abbeyroad.com/news/lester-smiths-abbey-road-story-abbeyroad90-3087
- Abbey Road — Recording Vocals at Home  
  https://www.abbeyroad.com/news/how-to-record-and-process-studio-vocals-at-home-2700
- Abbey Road Studio Three — KM84 / Fairchild drum treatment  
  https://www.abbeyroad.com/news/abbey-road-rooms-studio-three-with-freddie-light-3443
