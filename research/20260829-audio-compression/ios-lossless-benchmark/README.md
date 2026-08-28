# iPhone実機 ALAC／FLACベンチマーク

PC上で測ったALAC／FLACの容量、復号CPU負荷、途中シークの差を、Appleの`AVAudioFile`経路で再測定するためのXCTestです。アプリの形式を決定するテストではなく、未取得だったiPhone実機証拠を得るためのものです。

## 入力ファイル

次の3ファイルをiOSアプリのテストターゲットへ追加し、`Copy Bundle Resources`に含めます。

- `lossless-access-benchmark/source.wav`：48 kHz、24-bit、ステレオPCM、120秒
- `lossless-access-benchmark/source.m4a`：同じPCMから作ったALAC
- `lossless-access-benchmark/source.flac`：同じPCMから作ったFLAC

テストコード`LosslessDecodeBenchmarks.swift`も同じテストターゲットへ追加します。

## 実行条件

1. Simulatorではなく対象iPhoneを選ぶ。
2. Release構成でテストする。
3. 低電力モードを切り、充電ケーブルを接続する。
4. 端末温度が落ち着いてから全テストを3回実行する。
5. 最初の1回はファイルキャッシュを温める試行として別記する。
6. XcodeのTest Reportから経過時間、CPU、メモリをCSVへ転記する。
7. 実行前後の端末機種、iOS、空き容量、`ProcessInfo.thermalState`も記録する。

## 判定単位

- `testSingle*`：120秒ファイルの全復号。各形式5反復。
- `testFourTrack*`：同じ形式を4ファイルとして並列全復号。各形式3反復。
- `testSeekedSamplesMatchPCM`：5、30、60、90、115秒地点から1秒を読み、PCM／ALAC／FLACのSHA-256を照合。

CPU時間、経過時間、メモリ、シーク一致を別々に記録します。容量が小さいことだけで採用せず、4トラック処理中のCPUと発熱を重視します。

## この環境での検証限界

現在の作業環境にはSwift、Xcode、iOS SDK、接続済みiPhoneがありません。そのため、コードは作成・内容確認までで、コンパイルと実機実行は未実施です。
