# 周期関係グラフ：S01〜S04検証結果

## 目的

SciPy基準線とlibrosa 1.0基準線の周期候補を一つのBPMへ平均せず、由来つきのノードと整数倍関係として保持する。各役割は確定分類ではなく、後続の証拠で支持・棄却する仮説である。

## 結果

| ケース | 保持された主要仮説 | 保存された不一致 | 判定 |
| --- | --- | --- | --- |
| S01 | 0.5秒を`pulse_candidate`、1.0秒を`accent_cycle_candidate` | 0.5秒はSciPy 4位、librosa 1位 | half／double tempoを一意化せず保持 |
| S02 | 0.5秒を`pulse_candidate`、2.0秒を`recurrence_cycle_candidate` | 2.0秒はSciPy 1位、librosa 4位 | pulseと4倍周期のloop候補を分離 |
| S03 | 0.75秒と1.0秒を`layer_period_candidate`、3.0秒を`joint_recurrence_candidate` | 複数周期で解析器順位が不一致 | 左右レイヤーを単一拍へ早期統合しない |
| S04 | 代表値0.525秒を`time_varying_pulse_candidate` | 固定周期が時間変化を要約することを明示 | 代表周期とtempo curveを同一視しない |

順位は0始まりの内部値ではなく、人間向けに1位始まりで表記した。異なる解析器のscoreは尺度が同じではないため、加算・平均・確率化していない。

## 読戻しで見つかった欠陥

最初の生成結果では、librosaの候補列末尾に含まれるscore 0の周期までノードになっていた。これは証拠のない候補を保存するため除外し、全score付き証拠が0より大きいことを回帰テストへ追加した。

## 現時点の限界

- `accent_cycle_candidate`は、pulseより上位の整数倍周期に付く弱い仮説であり、アクセント、loop、フレーズ境界を識別していない。
- `joint_recurrence_candidate`はチャンネル別優勢周期の整数公倍数候補であり、知覚的な拍節を意味しない。
- S01〜S04は制御された合成音源であり、実録音への一般化は未検証である。
- 解析器間のrank disagreementは残すが、どちらが正しいかはこの層では決めない。

機械可読な全結果は`generated/relational-period-graphs.json`に出力する。再現の正本は生成済みJSONではなく、解析器、合成音源生成器、テストである。
