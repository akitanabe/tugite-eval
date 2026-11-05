# 11 prepared inputs vs8 executed tasks

| 項目 | 8直接task | 追加3packet |
|---|---|---|
| 対象 | separated、mixed、infrastructure、unknown-connection、shipping正常/境界/欠落依存/意図未共有 | normal、unknown-connection、infrastructureの読者指定版 |
| fixture/override | 元の基本8case | 対応する基本caseと同じ |
| 依頼の差 | 元の依頼 | 改行＋「15歳くらいの人に伝わるように説明してください。」のみ追加 |
| 候補/モデル要求/基準 | 5cc3e4、sol/medium、現行基準 | 同じ |
| 反復 | 各1回 | 各1回。基本caseの追加反復ではなく、prompt条件を一つ変えた比較入力 |
| 現在の報告 | 親から8件完了の報告 | 今回バッチ外として未実行/保留 |

したがって、8件で全基本機能・境界・欠落依存・意図未共有シナリオを一度ずつ実行したとは言える。
しかし、今回棚卸しした全11prepared入力を実行したとは言えない。
「用意済み入力すべて」を文字どおり完了するなら、残る3読者指定packetを各1fresh taskで実行する必要がある。
旧候補反復、baseline再比較、他Skillの追加は必要ない。追加の反復条件を導入していない。

COVERAGE_DELTA.jsonで各対応pairの差がcase ID/promptだけで、fixture/観測/metrics/source/model要求は同じと検証した。
EXPECTED_CONDITIONS.jsonで基本8件の元依頼・override適用後file bytesが17c18c2cの元caseと合うことを独立に静的照合した。
これは実際の直接taskのread/モデル/本文を検証したことではない。

親は8件完了を報告したが、完了本文・実行条件・artifact所在はこのworkerへ未供給。
同threadのread APIも公開toolにない。INDEPENDENT_REVIEW.jsonの品質判断はnullで保持し、本文を推測してPASS/FAILにしない。
実応答本文（またはこのworkerから読める保存先）と、実行条件/観測限界が必要。受領後、固定fixtureと現行rubricで
形式・意味単位・意味の達成・重複・事実/条件/作用/限界を独立に評価する。
旧結果やprepared input-sealを新しい実行証拠へ遡及転用しない。
