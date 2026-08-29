# BattleFX研究 Phase 4 — AUv3自動化可能性ゲート

- research-id: `20260828-battlefx`
- status: `active`
- 更新日: 2026-08-28
- 研究対象: BattleFX iOS版を外部ホストまたはField Looperから演奏制御できるか
- 実機観測: 未実施
- 実装状態: 未実装

## 1. 今回取得できたこと

### 1.1 Apple App Storeで読めた範囲

App StoreのBattleFXページから次を読めた。

- iPhone / iPad対象
- 無料
- サイズ23.8 MB
- iOS / iPadOS 12.0以降
- Shatter DelayとHeadspace Reverbを任意のtrackで使えるという製品説明
- mix controls、Solo、Muteを含むという製品説明
- delay/reverb bufferの自動choke
- tempo sync / free
- delayとreverbの独立制御
- beat前後へのnudge
- Euclidean pattern knob
- MaximizeとEQ

出典:

- https://apps.apple.com/us/app/battlefx/id6764648922
- https://www.unfilteredaudio.com/products/battlefx

### 1.2 読めなかったもの

現在取得したApp Store本文には、BattleFXの`Version History`または`What's New`節が返らなかった。

Appleの旧iTunes lookup endpointも、この取得経路では安全なURLとして開けず、別経路からversion metadataを補完できなかった。

したがって今回の研究では次を断定しない。

- 現在version番号
- build番号
- release noteの有無
- 初版以後のparameter追加・削除
- preset formatのversion
- parameter addressの安定性

「version履歴が存在しない」とは判定しない。今回の取得面から本文を得られなかっただけである。

## 2. AUv3であることとautomationできることを分ける

AUv3としてホストへ読み込めることは、製品GUIの全controlがhost parameterとして公開されることを証明しない。

必要な状態を分ける。

| 状態 | 何が確認できるか |
| --- | --- |
| LOADABLE | hostがeffectをinstantiateして音声を通せる |
| GUI_CONTROLLABLE | plugin独自画面からcontrolを触れる |
| PARAMETER_EXPOSED | hostがparameter treeからcontrolを列挙できる |
| HOST_AUTOMATABLE | host automationで値を記録・再生できる |
| MIDI_MAPPABLE | MIDI CC等から値を変更できる |
| GESTURE_SAFE | 複数controlの同時gestureが破綻しない |
| STATE_RESTORABLE | 保存後に同じ値と内部状態が戻る |

App Store掲載と製品説明からLOADABLE以後を一括で推定しない。

## 3. 公開parameter一覧の取得結果

BattleFX固有の次の情報は、今回の公開Web資料から取得できなかった。

- AUParameterAddress
- parameter identifier
- display nameの全一覧
- min / max / default
- unit
- flags
- ramp可否
- read-onlyかwrite可能か
- host automation対応
- MIDI learn対応
- parameter group階層
- choke patternの離散値
- sync時とfree時でaddressが変わるか
- preset変更時にparameter treeが変わるか

Apple Developer Documentationには`AUAudioUnit.parameterTree`の入口が存在するが、取得器ではJavaScript必須ページの本文を読めなかった。

- locator: https://developer.apple.com/documentation/audiotoolbox/auaudiounit/parametertree

このlocatorの存在を、BattleFXが特定parameterを公開している証拠へ使わない。

## 4. なぜField Looperにとって重大か

Phase 3の演奏語は、次の製品controlへ外部から届く可能性を前提にしていた。

| 演奏語 | 必要になるBattleFX側control候補 |
| --- | --- |
| EXCITE | delay/reverb inputまたはwet send |
| STARVE | input gateまたはsend gain |
| BREAK_ECHO | delay choke enable/rate/pattern |
| BREAK_ROOM | reverb choke enable/rate/pattern |
| LEAN | delay/reverb nudge |
| KILL | feedback、decay、bufferまたはwet gain |
| CATCH | host側wet-only bus録音 |
| SLOW/CRUSH候補 | delay/reverb S.RATE |

これらがhost parameterとして公開されていなければ、BattleFX AUv3をそのまま内部エンジンとして包んでもPhase 3の演奏は成立しない。

GUIを人間が直接触れるだけならBattleFX単体は演奏できる。しかしField Looper側のtrack選択、EXCITE latch、CATCH、KILLと同期させるには、外から安定して値を送れる必要がある。

## 5. 最小監査対象

全controlを最初から調べる必要はない。Phase 3の成立を左右する順で調べる。

### Gate A: routing

1. Delay Gain / Mix / Solo / Mute
2. Reverb Gain / Mix / Solo / Mute
3. Master直通の有無
4. Delay-to-Reverb Send
5. bypass

合格条件:

- dryを重複させずwet-only returnを作れる
- plugin bypassとtail killを混同しない
- host側でgainまたはmuteを安全に動かせる

### Gate B: interruption clock

1. Delay Choke enable
2. Delay Choke rate
3. Delay Euclidean pattern
4. Delay Nudge
5. Reverb Choke enable
6. Reverb Choke rate
7. Reverb Euclidean pattern
8. Reverb Nudge

合格条件:

- delayとreverbを別addressとして列挙できる
- hostから一方だけを動かせる
- sync/free切替後も意図したcontrolへ届く
- automation再生が周期の勝手なresetを起こさない

### Gate C: material / instability clock

1. Delay Time
2. Feedback
3. Glitch
4. Stereo
5. Delay S.RATE
6. Reverb Predelay
7. Decay
8. Reverb S.RATE
9. IN TILT
10. OUT TILT

合格条件:

- 値変更がhostから可能
- gesture開始/終了をhostへ通知できる
- S.RATE操作で急な発振または大音量が出た場合にKILLできる

### Gate D: restoration

1. host project save
2. app終了
3. audio route変更
4. app再起動
5. project reload

合格条件:

- parameter値が戻る
- preset名だけでなく実値を確認できる
- active choke phaseが戻るかresetするかを区別できる
- 古いtail bufferが復元されるかを区別できる

## 6. 実機監査の手順

### 6.1 host

最初はAUM等、AUv3 parameter一覧とautomation/MIDI mappingを表示できるhostを使う。

特定hostで見えないことをBattleFXの非公開判定へ直結させない。最低二hostで比較する。

候補:

- AUM
- Logic Pro for iPad
- Loopy Pro
- GarageBand

この列挙は対応確認済み一覧ではない。監査候補である。

### 6.2 test signal

次の四素材を固定する。

- 単一sample impulse
- 1 kHz sine
- 短いvoice consonant
- 長いvoice vowel

用途:

- impulse: routing、delay onset、choke位置
- sine: pitch/S.RATE、gain discontinuity
- consonant: short tail、ruff、buzz
- vowel: reverb memory、STARVE、KILL

### 6.3 parameter dump

hostが表示する全parameterについて次を記録する。

```text
address
identifier
displayName
groupPath
min
max
default
unit
flags
currentValue
writable
automationObserved
midiMapObserved
```

表示名だけで同一性を判定しない。同名parameterがdelay/reverb両方にある可能性があるため、groupPathとaddressを一緒に持つ。

### 6.4 gesture test

各parameterで次を行う。

1. 値をゆっくり変更
2. 最小から最大へ一回変更
3. automationを記録
4. 再生
5. 別parameterと同時変更
6. preset変更
7. project reload

記録するもの:

- 値が追従したか
- 音が変わったか
- host表示値が戻ったか
- click / dropout
- latency変化
- parameter tree変化
- address変化
- gestureの取りこぼし

## 7. 三つの分岐

### A. 必要parameterが公開される

BattleFX AUv3を実機参照エンジンとして使える。

ただしField Looperへ製品を埋め込めることとは別である。研究段階では、AUM等でPhase 3の演奏文法を試すところまで。

### B. 一部だけ公開される

公開範囲だけで演奏を再構成する。

例:

- Choke Rateは公開、Euclidean Patternは非公開
- Delay Nudgeは公開、Reverb Nudgeは非公開
- Solo/MuteはGUI専用

この場合、非公開controlを似た別parameterへ勝手に置換しない。Phase 3のどの行為が成立し、どれが成立しないかを分離する。

### C. 重要parameterが公開されない

BattleFXは音響参照機として使い、Field Looper側は独自の最小DSPで構造を検証する。

これはBattleFXの複製を意味しない。

最低限:

- wet-only input/output
- short delay
- character reverb
- delay/reverb独立choke clocks
- nudge
- S.RATE結合仮説
- emergency KILL

製品固有の未公開algorithm、preset、reverb modeをコピーしない。

## 8. parameter addressをPerformance Takeへ保存しない

仮にBattleFXのaddressを取得できても、Performance Takeの意味eventを製品固有addressへ直接結び付けない。

悪い例:

```json
{
  "address": 18437,
  "value": 0.72
}
```

研究候補:

```json
{
  "event": "BREAK_ECHO",
  "density": 0.72,
  "adapter": {
    "product": "BattleFX",
    "observedVersion": null,
    "parameterAddress": null
  }
}
```

意味eventを正本にし、製品versionごとのparameter mappingをadapterへ隔離する。

理由:

- version updateでaddressまたは範囲が変わる可能性を未検証
- hostごとに表示名が変わる可能性を未検証
- 独自DSPへ移ったときも演奏記録を残せる
- BattleFXの採否がPerformance Take全体を壊さない

## 9. version不明時の扱い

監査結果には必ず観測対象versionを付ける。

取得できない場合:

```json
{
  "appStoreId": "6764648922",
  "observedVersion": null,
  "observedBuild": null,
  "versionEvidence": "UNOBTAINED"
}
```

version不明のparameter dumpを「BattleFX全versionの仕様」として保存しない。

同じ端末で後日再監査するときは、前回結果を上書きせず新しいrun IDへ保存する。

## 10. 公開資料から変わった判断

参照前:

- AUv3 parameter一覧をWebから取得できれば、実機前にPhase 3の外部制御可能性をかなり絞れると見ていた。

参照後:

- 製品固有のparameter treeは公開Webから取得できなかった。
- App Store本文からversion historyも取得できなかった。
- よって、Phase 3の`BREAK_ECHO / BREAK_ROOM / LEAN`をBattleFX AUv3で実現可能とはまだ言えない。
- 次の強い証拠は、iPhone上のhost parameter列挙とautomation再生である。

変わらなかった判断:

- delay/reverb chokeは製品説明上、独立制御される。
- BattleFXをmasterまたは主演奏面へ置かない。
- 一基のshared wet bus候補を維持する。
- 実装開始はまだ`no`。

## 11. 参照境界

### 読めた実体

- Apple App Store BattleFX本文
- Unfiltered Audio BattleFX製品本文
- 現行Git BattleFX README
- 現行Git Phase 3
- Draft PR #23 metadata

### locatorだけ確認

- Apple `AUAudioUnit.parameterTree` documentation

### 取得不能

- BattleFX固有AUv3 parameter tree
- BattleFX iOS版release notes
- BattleFX iOS版version/build
- preset一覧とsnapshot
- iOS binary内部metadata
- 実機host automation挙動

## 12. Phase 4の現在判断

- 公開資料調査だけではAUv3外部制御の成立を確認できない。
- 重要parameterの存在をGUI名から推測しない。
- 実機監査はrouting -> interruption -> material/instability -> restorationの順に行う。
- parameter addressはPerformance Take正本へ直接保存しない。
- 監査結果はversion付きrunとして追加し、旧runを上書きしない。
- BattleFXは引き続き共有wet-only tail busの研究候補。
- Field Looperへ統合済みではない。
- 実装開始はまだ`no`。

