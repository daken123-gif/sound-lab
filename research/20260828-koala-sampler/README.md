# Koala Sampler research

- research-id: `20260828-koala-sampler`
- status: `active`
- 更新日時: 2026-08-28 UTC
- 研究対象: elf audio / Mazbox Limited「Koala Sampler」
- 現在の問い: Koala Samplerの速い録音・演奏・再サンプリングを研究し、4トラックのField LooperをKoalaより難しくせず設計するにはどうするか

## 現在のユーザー要件

以下は外部製品の事実ではなく、現在の製品方針を決めるユーザーの発話である。

- Field Looperは4トラックとする。
- 「Koalaより難しいものを作るのは愚の策」であり、Koalaを操作複雑度の上限として扱う。
- アプリ起動やマイク接続を録音開始へ変えず、録音は人間の明示操作から始める。
- iPhoneへ特化し、無理にDAWへ寄せない。
- 4トラックを合成した音を波形として直接触れる方向は維持する。
- ドラム部は既存ルーパーへ混ぜず、別の研究・楽器として扱う。

## 一次資料

- [Koala Sampler公式マニュアル](https://manual.koalasampler.com/)
- [General Overview](https://manual.koalasampler.com/mobile/2-general-overview/)
- [Sample](https://manual.koalasampler.com/mobile/4-sample/)
- [Sequence](https://manual.koalasampler.com/mobile/5-sequence/)
- [Perform](https://manual.koalasampler.com/mobile/6-perform/)
- [Effects](https://manual.koalasampler.com/mobile/9-effects/)
- [AUv3 Functionality](https://manual.koalasampler.com/mobile/11-AUv3-functionality/)
- [Samurai公式ページ](https://koalasampler.com/samurai/)
- [Mixer公式ページ](https://www.koalasampler.com/mixer/)
- [Koala Sampler公式リリースノート](https://cdn.koalasampler.com/builds/release-notes.html)
- [iOS App Store掲載ページ](https://apps.apple.com/us/app/koala-sampler-beat-maker/id1449584007)

## 一次資料から観測できた事実

### 録音とサンプル

- Sample画面にはA〜Dの4バンク、合計64パッドがある。
- 空パッドを押している間にマイク入力を録音し、離すと録音を終える。
- 入力元にはマイク、音声ファイル、動画、オーディオインターフェース、AUv3 Effect時の外部入力、Koala内部の再サンプリングがある。
- 入力モニターは明示的なMonitor操作で有効にする。マイク監視時はフィードバック回避のためヘッドホン利用が警告される。
- Koala内部のパッド、シーケンス、Perform FXを演奏しながら、その結果を空パッドへ再録音できる。
- パッドを空パッドへドラッグするとコピーできる。使用中パッドへ重ねると、ミックス、交換、後ろへの連結を選べる。
- ミックスまたは連結時には、両サンプルへ設定したパラメータが音へ焼き込まれる。
- サンプル編集には再生範囲、ズーム、One Shot、Reverse、Loop、Ping Pong、Crossfade、Attack、Release、Tone、6 Choke Groupなどがある。
- Auto-Chopにはトランジェント、等分、Lazyの方法がある。Samurai追加機能である。
- Stem Splitは最大4ステムを抽出し、追加データを端末へ導入してStandaloneで使用する。

### シーケンス

- 32シーケンス枠があり、一つのシーケンスは最大64小節である。
- 録音済みシーケンスへRecordするとオーバーダブになる。
- シーケンスをドラッグしてコピー、ミックス、末尾への追加ができる。
- 切替タイミングは即時、1拍、1小節、シーケンス終端から選べる。
- SamuraiではKeyboard、Scale、Note Repeat、Piano Roll、Velocity、発音確率などの編集が加わる。

### Perform FX

- Perform画面には16種類のライブFXがある。
- FXは触れている間だけ有効になり、HOLDで指を離した後も保持できる。
- 複数の指で複数FXを同時に使え、16種類すべてを同時に有効化できる。
- 横画面では16FXを同時表示し、電話の縦画面では2ページへ分ける。
- StutterとCutterはテンポ同期し、Pitch、Filter、VibroFlangeは中央から上下で処理方向が変わる。
- FXの信号順は左上から右下である。

### MixerとAUv3

- Mixer追加機能は4バスとMainを持ち、各チャンネルに5個のFXスロットがある。
- iOSでは外部AUv3の音源・エフェクトをKoala内部でホストできる。
- Koala自体もiOSホストへAUv3 Instrument、AUv3 Effect、Multi-Busとして読み込める。
- Instrumentとして読み込んだ場合はKoalaへの外部入力を録音できない。外部音をKoalaへ録る用途ではEffectとしての読み込みが推奨される。
- KoalaからAUv3ホストへTransportを送れないため、ホスト側の再生を開始する必要がある。
- 公式マニュアルはMulti-Busの対応ホストとしてAUMを挙げている。
- AUv3モードではStem SplitとKoala内Solo/Muteに制限がある。

### 2026年8月時点の更新

公式リリースノートでは、2026-08-20の2.0.3に次が記録されている。

- 全体Undo/Redo
- 新しいArpeggiator
- ChopperのNEXTトリガー
- Loop / Trackの書き出し制御
- Piano Rollノート色とパッド色の一致

Samuraiのタイムストレッチ数について、現行のApp Store記述はCyclicを含む5モードを挙げる一方、公式マニュアルのSample節は4モードを記述している。一次資料間の更新差として保留し、どちらかへ断定しない。

## ユーザー評価・訂正

- Field Looperは3ループ案から4トラックへ変更された。
- 私がKoala研究を足し算として扱い、FREE/LINK、テイク履歴、PRINT先、4つの複合シーン、ローリングバッファなどを追加した案に対し、ユーザーは「Koalaより難しいもの作るのは愚の策」と訂正した。
- この訂正により、Koalaの機能を多数移植する方針ではなく、Koala以下の操作手数で4トラックを扱う方針が現在の基準になった。

## 推論・設計判断

### Koalaの中心は機能数ではなく短い循環

Koalaの主要な循環は次である。

```text
録る
  -> その場でパッドになる
  -> 切る／叩く／並べる
  -> FX込みで再サンプリングする
  -> 新しい素材として再び使う
```

録音結果がファイル管理画面へ退避せず、演奏面のパッドへ直接現れることが速さの中心である。64パッド、32シーケンス、Piano Roll、Mixerを移植することは、この中心を採用することと同義ではない。

### Field Looperの複雑度上限

初期版の演奏面へ露出させる候補は次に限定する。

- 4つの大きなトラック
- 各トラックの録音、ループ再生、オーバーダブ、Mute
- 全体Undo
- INPUT GAIN / OUTPUT GAIN
- 4トラックの合成波形
- 合成波形への瞬間的な直接操作
- 少数のマスターFX

詳細な同期モード、テイクブラウザ、ルーティング、FXチェーン編集、Piano Roll、プラグインホストは初期の演奏面へ出さない。

### 一操作一結果

Koalaから採るべきUI規則:

- 録音操作は録音だけを始める。
- 指を離す、または同じ対象を再度押すと録音結果がすぐ演奏可能になる。
- FXは触れている間だけ効き、離すと原音へ戻る。
- HOLDやUndoが必要でも、録音・再生の入口を増やさない。
- 色だけに頼らず、録音中、再生中、オーバーダブ中、Muteを文字でも示す。
- マスター面を触っている指があっても、別の指によるTrack / Mute / FX操作を拒否しない。

## Field Looperへ採用する点

確定した設計条件:

- 4トラック。
- Koalaを超える操作複雑度を初期版へ持ち込まない。
- 録音開始には人間の明示操作を必要とする。
- iPhoneに特化した一画面の演奏を中心にする。
- INPUT / OUTPUTを演奏画面で確認・調整できる。
- 4トラック合成後の波形を直接触る。
- マルチタッチを、波形を保持しながら別の演奏操作を行うために使う。

現在の実装候補。ユーザーによる実機承認は未取得:

- 空トラックを押して録音し、再度押してループを閉じる。
- 再生中トラックへの明示操作でオーバーダブする。
- 合成波形のX位置で断片を捕捉し、上方向ほど短く反復し、指を離すと通常再生へ戻る。
- マスターFXを `FILTER / ECHO / REVERSE / SPACE` 程度へ絞り、押している間だけ有効にする。

## 採用しない点

- 64パッドをField Looperへ移植すること。
- 32シーケンスとPiano Rollを初期版へ入れること。
- Samurai、Mixer、Stem Split、内部AUv3ホストを初期版の必須機能にすること。
- Koalaの16 Perform FXをそのまま並べること。
- DAWのようなMixer、Bus、FXチェーン編集を演奏画面へ出すこと。
- アプリ起動、マイク許可、入力接続、画面復帰を録音開始にすること。
- 操作結果を説明なしの長押しや多段メニューへ隠すこと。
- ドラム機能を4トラックの既存ルーパーへ混ぜること。

## 失効した判断

1. **3ループ**  
   現在は4トラックへ変更された。

2. **FREE / LINKの二同期モード**  
   Koalaより操作判断を増やすため、初期案から撤回。

3. **表示されるテイク履歴と録音先指定**  
   テイク管理、PRINT先、自己フィードバック除外などを演奏者へ判断させる案は撤回。

4. **4つの複合マスターシーン**  
   LOOP / CUT / DUB / SPACEごとに軸の意味と内部チェーンを設計する案は、Koalaより難しくなるため初期版から撤回。

5. **ローリングバッファを理解して触る設計**  
   内部実装として使う可能性は残るが、演奏者へ概念やモードを要求しない。

6. **Koalaの機能を足してField Looperを強化する方針**  
   機能移植ではなく、録音から演奏までの手数を減らす設計原則だけを採る。

## 触る実装パス

この研究PRでは製品コードを変更しない。

統合時の候補:

- `field-processor/index.html`
- 将来分割する場合のtrack state / waveform / master FX modules

## 依存する研究

- `20260828-iphone-mic-preamp`: iPhone入力、INPUT / OUTPUT、録音前段。
- `20260828-kaoss-master-fx`: 合成波形とマスターFX。ただし同研究内の3ループ記述は現在の4トラック要件と矛盾し、後続統合時に更新が必要。
- Loopy Pro研究: 手動録音、Monitor、Echo Cancellation、縦横UI。
- Teenage Engineering研究: 4トラックという制約。
- AUM研究: 外部入力、内部音声、AUv3接続。
- Digitakt / IDM drums研究: ドラム部をルーパーと分離する。

依存研究の未検証内容を、この研究で検証済みとして扱わない。

## 未検証事項

- Koala実機をこの研究内で操作していない。一次資料からの観測のみ。
- iPhone 13 mini横画面で、4トラック、合成波形、INPUT / OUTPUT、少数FXが一画面に収まるか。
- 4トラックの録音開始・終了・オーバーダブを一つのTrack操作へまとめても誤操作しないか。
- 2〜4本目の録音をどのように同期させれば、設定を増やさず、人間の明示操作も保持できるか。
- 合成波形へ触れる操作が、説明なしに位置選択と反復量として理解できるか。
- マスターFXを4個まで減らす判断が、必要な演奏表現を損なわないか。
- 波形操作中に別指でMute / FXを押すマルチタッチがiPhone Safariで安定するか。
- 実機で声を録音し、4トラックへ重ね、波形を触るまでKoala以下の判断数で到達できるか。

## 次の検証順序

1. 製品コードを触らず、iPhone 13 mini横画面の一画面ワイヤーフレームでタッチ面積を確認する。
2. 4トラックの状態遷移を、説明なしのタップだけで誤操作なく行えるか机上試験する。
3. 同期設定を追加せず2〜4本目を録音する一つの挙動だけを選ぶ。
4. 合成波形の捕捉と復帰だけを試作する。
5. マスターFXは一つから開始し、Koalaより難しくならないことを各追加前に確認する。
6. iPhone実機で「起動、声を録る、4本重ねる、波形を触る」を通しで検証する。
