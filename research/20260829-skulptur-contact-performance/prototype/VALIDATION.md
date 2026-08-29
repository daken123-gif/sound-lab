# Validation record

実行日: 2026-08-29 UTC

## 実行済み

`node --test`

- PASS: 非アクティブ時は入力とビット単位で一致
- PASS: 4次／8次ともインパルス入力で非有限値を発生しない
- PASS: 対象帯域のミュートが出力エネルギーを変える
- PASS: 4次と8次の出力に測定可能な差がある
- PASS: リリース後はクリックを作らずDryへ収束
- PASS: マルチタッチで別帯域を独立制御
- PASS: 同帯域では最後に触れた指を優先
- PASS: Elastic復帰
- PASS: Throwの継続、端点反射、摩擦停止
- PASS: Flow動作中も手動タッチを優先
- PASS: RECを明示するまでジェスチャーを記録しない
- PASS: 帯域カーブの記録とループ境界補間
- PASS: 触れた帯域だけを差し替え、他帯域を保持
- PASS: 記録状態の保存・復元
- PASS: 手動タッチ > 記録演奏 > Throw > Flow の優先順位
- PASS: 記録演奏によるDSP経路の自動有効化
- PASS: 4本のループを単一の演奏対象へ合成
- PASS: トラック単位のゲインとミュート
- PASS: 独立ドラムがスペクトル処理を迂回
- PASS: ループを変形してもドラム成分を保持
- PASS: Feedbackによる帯域テールの延長
- PASS: 最大Feedbackでも非有限値と過大発散を生じない
- PASS: Feedback解除後に処理状態を休止できる
- PASS: ループとドラム合流後の過大出力を0.98以内へ制限
- PASS: 中央を無加工として、下側をCut・上側をFeedbackへ変換
- PASS: 操作位置を0〜1へ制限
- PASS: 複数指と同帯域の最終タッチ優先
- PASS: Feedbackの優先順位を指 > 記録 > 固定値に設定
- PASS: 一つのREC操作からCutとFeedbackを同時記録
- PASS: 試奏面にSTART、REC、Flow、Clearを配置
- PASS: 4ループ＋独立ドラムの5入力接続
- PASS: 音響開始はSTART操作に限定し、マイクは自動起動しない
- PASS: DSPが返した帯域状態を試奏面へ表示
- PASS: 表示上の制御元が指 > 記録 > Throw > Flowの優先順位と一致
- PASS: DSPのGain／Feedback値を同じ操作面位置へ戻せる
- PASS: ホスト接続時に4ループ＋独立ドラムの5入力を固定
- PASS: 本体から明示されたトランスポート、REC、指操作だけを送信
- PASS: ジェスチャー状態の要求と応答をIDで対応付け
- PASS: 終了時に入力・出力接続を解除し、以後の操作を遮断
- PASS: 試奏面も`SkulpturHostController`経由で動作
- PASS: LOOP 1〜4の明示操作からだけ音声ファイルを読み込む
- PASS: マイク取得を追加せず、音声ファイルを4秒へ切断・無音補完
- PASS: 読込音声を最大ステレオへ制限し、切断点をフェード
- PASS: 現在のトランスポート位置へ同期して1トラックだけクロスフェード差し替え
- PASS: ContactGestureFrameの必須field、範囲、track所有権、pressure由来を検査
- PASS: contact起点、単調時刻、release/cancel終端のphase因果を検査
- PASS: Pointer Eventをcontact/press/slide/release/cancelへ変換
- PASS: fallback pressure 0.5をhardware測定値として扱わない
- PASS: capture喪失と画面向き変更をcancelへ変換し、所有権を解放
- PASS: 画面非表示をcancelへ変換し、所有権を解放
- PASS: 同じ接触frameからSkulpturの10帯域とCut↔Feedback位置を導出
- PASS: 画面外pointercancelを最後の有効接触点から終了
- PASS: 画面外pointerupをcancelへ回復し、pointer所有権を解放
- PASS: Contact Performance Takeを相対時刻の単一frame列として記録
- PASS: 空Take、時刻後退、未終了gesture、duration不一致を拒否
- PASS: Take再生列で制御値を保持し、gesture IDと時刻を再インスタンス化
- PASS: 再生pointer IDを実pointerから分離
- PASS: 実時間playerが期限到来frameだけを順序通り発行
- PASS: 再生停止時に全active接触へcancelを発行
- PASS: playerの二重開始と時刻後退を拒否
- PASS: 一つのTAKEボタンから録音・再生・安全停止へ到達
- PASS: 画面非表示時にTAKE再演を停止し、復帰時の残りframe一括発行を防止
- PASS: iOSによるAudioContext休止を既存STARTボタンのRESUME操作へ接続
- PASS: 同じTAKE再生frame object列を表示playerと音響schedulerへ供給
- PASS: AudioContext時計上の予約時刻を順序通りqueueから発行
- PASS: 同時刻commandの記録順序を保持
- PASS: schedule ID単位で未発行commandを中断
- PASS: 未開始move、二重begin、未終了pointer、時刻後退を拒否
- PASS: Hostから予約batchと明示cancelをAudioWorkletへ送信
- PASS: 音響予約が拒否された場合に表示playerの開始状態を巻き戻す
- 合計: 84 pass / 0 fail

`node scripts/render-demo.mjs`

- `renders/skulptur-4th-demo.wav` を生成
- `renders/skulptur-8th-demo.wav` を生成
- 48kHz / stereo / 16-bit PCM / 各8秒

ローカルHTTP配信

- PASS: `demo/`
- PASS: `demo/style.css`
- PASS: `demo/app.js`
- PASS: `src/contact-gesture.js`
- PASS: `src/contact-gesture.schema.json`
- PASS: `src/pointer-contact-adapter.js`
- PASS: `src/skulptur-contact-bridge.js`
- PASS: `src/contact-performance-take.js`
- PASS: `src/contact-performance-take.schema.json`
- PASS: `src/scheduled-touch-queue.js`
- PASS: `src/skulptur-filter-bank.worklet.js`
- 11資産ともHTTP 200

## 時間設計の一次根拠

- Web Audio API 1.1: `AudioContext.currentTime`はrunning中にrender threadで単調増加し、すべての予約時刻の座標系になる。<https://webaudio.github.io/web-audio-api/>
- HTML Standard: 非表示documentではrendering opportunityが大幅に間引かれ得るため、`requestAnimationFrame`を音響時計にしない。<https://html.spec.whatwg.org/multipage/webappapis.html>
- WebKit Bug 231105 / 263627: iOSのbackground遷移と復帰でAudioContext停止・再開が一貫しない事例がある。<https://bugs.webkit.org/show_bug.cgi?id=231105> / <https://bugs.webkit.org/show_bug.cgi?id=263627>

## 未検証

- iPhone 13 mini実機のCPU負荷
- Safari/WebKit上のAudioWorklet動作
- Mobile Safari上のPointer Event順序、capture、pressure、contactArea
- Mobile Safariが実際にAudioContextを休止・再開するタイミング
- iPhone実機上で描画と音響が同じ接触frameを追跡すること
- AudioWorklet予約がMobile Safari実機でrender quantum範囲のずれに収まること
- Contact Performance Takeの複数Take一覧、命名、永続保存UI
- Safari上で端末内の各音声形式を`decodeAudioData`できる範囲
- iPhoneマイクまたは実録音素材による音質評価
- iPhone実機上での4トラック同時再生負荷
- FeedbackのiPhone実機音量安全性、内部オーバーサンプリング、製品全体画面への統合
- クラウドブラウザからローカルURLへの接続がクライアント側で遮断されたため、ブラウザ上の自動操作確認

この記録はローカルNode実行の結果だけを示し、iPhone実機での動作完了を意味しません。
