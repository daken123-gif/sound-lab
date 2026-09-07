# プロジェクト共通の音源取得・解析方針

更新: 2026-09-07 UTC

## 適用範囲と今回の決定

ユーザーの「band campもプロジェクト全体の解析に取り入れましょう」に基づき、Bandcampを全アーティスト研究で利用する正式な音源経路へ追加する。Autechreだけに限定しない。各研究は、このファイルを `main` から取得し、自分の研究ブランチにある古いコピーだけで方針を決めない。

Shazamによる作品・版の同定とApple Music公式プレビューの既存観測は保持する。Bandcamp追加はSpotifyへの変更でも、既存研究結果の上書きでもない。全曲を取得できた研究から全曲検証へ進む。

## 入力経路

| 経路 | 役割 | 取得時に確定するもの |
| --- | --- | --- |
| Shazam → Apple Music公式preview | 作品・版の同定と局所観測 | 曲ID、収録版、storefront、実取得音声hash、区間尺 |
| 公式アーティスト／レーベルのBandcamp | 全曲の公開試聴音声、または利用可能な購入音源による検証 | 公式性の根拠、album/track ID、版、codec、実測尺、hash |
| 公式YouTube／Topic | 公式配信表現による追加照合 | video/channel ID、権利表示、配信codec、音声実体、hash、実測尺 |
| ユーザー提供・権利者公開の音源 | 取得可能な別表現での照合 | 提供元、版、入力品質、hash、実測尺 |

Bandcampの公開試聴MP3と購入用FLAC/WAVを分ける。公開試聴が全曲か、限定区間かは、取得・全体デコードとページ尺の照合で対象ごとに検証する。一曲の成功を全カタログの取得保証にしない。ダウンロードに認証・購入・アクセス制限が必要な場合はその境界を記録する。

## 共通の実行工程

1. 公式の配信元と曲・収録版を同定する。曲名一致や尺一致だけで同一masterとは判定しない。
2. 公開playerが提供する音声または利用可能な正規ファイルを取得する。ログイン制限、購入制限、DRM、サービス側のアクセス制限は回避しない。
3. 元bytesのSHA-256、取得日、stable page URL、曲ID、codec、sample rate、channels、byte数を固定する。期限付きの配信URLや認証情報は公開Gitへ保存しない。配信hostとURL hashを残し、再取得はstable pageから行う。
4. 音声全体をエラー検出付きでデコードし、実測尺とページ尺を照合する。ページ閲覧・URL発見・音声取得・全体decode・音楽解析を別状態として扱う。
5. 既存previewの位置を全曲内で照合する。offset、照合方法、候補ピークの曖昧さ、codec差、速度差、gain差を記録する。一致しない版を無理につなげない。
6. 全曲を連続した明示窓へ分け、窓の開始・終了と特徴を記録する。既存の共通校正済み特徴を使い、最後の短い窓もその尺を表示する。全体BPM一個で長期変化を潰さない。
7. 元previewの観測を残し、全曲で維持された結果、局所偏り、反証を追記する。分離stemは二次証拠として扱う。

`analyze_previews.py` は出力scopeを「unknown-position 30-second excerpt」と固定しているため、全曲をそのまま渡して全曲解析済みとはしない。全曲用処理では区間とscopeを明示し、このラベルを継承しない。特徴定義を変えた場合は従来値との直接比較を停止し、同じ入力を旧・新両方式で測ってから差を解釈する。

## 実行と保存

Bandcampの再現用取得器:

```bash
python research/music-analysis/acquire_bandcamp.py \
  https://autechre.bandcamp.com/album/anti \
  --artist Autechre --track Flutter
```

出力は `.source-work/` の音声とmanifest。Gitへ残すのは、この方針、取得器、必要なmanifestと解析値、検証記録。音声本体、PCM、動画、cookies、期限付き配信URL、依存packageは保存しない。source manifestは音源の再取得保証ではなく、取得した実体を識別する記録である。

全曲用の `analyze_source_windows.py AUDIO --manifest MANIFEST --output RESULTS` は、manifestのhashと尺を照合してから既存特徴を30秒窓で測る。各窓の絶対offsetと実尺、全体の被覆を出力する。元previewとの照合や音楽的解釈は別工程。動作証拠とYouTubeの取得診断は [source-validation-20260907.md](source-validation-20260907.md) に記録する。

共通方針の更新は全研究が参照できる入口を整えるものであり、全研究の再解析が終了したことや、全会話が既に新方針を読んだことを意味しない。既存の定期タスク設定の変更は別工程として扱う。
