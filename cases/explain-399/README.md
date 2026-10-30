# #399: semantic flow and actual execution

正本は [Issue399](https://github.com/akitanabe/tugite/issues/399) 全文（2026-10-30確認、コメント0件）。
#398を置換した再設計であり、旧roundの結果や一時的な出力方針から評価目的を継承しない。

## 要求と旧基準の置換

- 機能の目的・全体像・主要な意味処理を示す。旧「導入不要」「短い寄与行だけ」は適用しない。
- 実際の入口・呼出し関係・順序を追えるコード実行フローを示す。意味上の流れとコード経路を取り違えない。
- 主要処理の意味・条件・分岐・状態変化・副作用をコードへ対応づけ、重要な順序・tx/失敗境界を残す。
- Dispatcher等の基盤は、必要な経路の連続性を保つために残す。汎用内部機構の講義は不要だが、名前で一律削除しない。
- 意味上の処理単位と実装上の責務を区別する。inline処理を架空のServiceへ置換せず、混在を自動的に設計問題としない。
- 全体像→経路と処理の説明を評価する。経路と説明の一体化は許す。固定の見出し・語数・行数・identifier-first-only・Reference文面一致は要求しない。

旧#398のbrevity/identifier-first-only/omit-framework、固定の短い役割行、戻り値を一律省略する方針は新基準の根拠ではない。
必要な意味・条件・効果・接続に応じて情報を選ぶ。実コードから確認できない意図や接続は引き続き捏造しない。
コード品質判定、refactoring提案、理想的な責務分割、追加の説明agentは求めない。深い内部調査は維持し、調査量を出力量に直結させない。

## 再利用と2ケース

| Case | Fixture | 評価する差 |
|---|---|---|
| explain-399-separated | 既存の合成Session fixtureをbyte保持 | ControllerからOperationへ委譲される交換処理と、認証/状態取得の分離した経路を忠実に示す。 |
| explain-399-mixed | 同じSessionの最小variant | exchangeの要求取得・検証・状態操作・Cookie発行を同じController関数に置く。意味では区切れても実経路を分割しない。 |

mixedではSessionOperation.exchangeを削除し、Controller.exchangeへ処理を直接置いた。他のstore/auth/Dispatcherと意味上の挙動は保持する。
両方とも学習用memory transactionが明示されている。混在だからtx不在/設計不良とは推論しない。
実DB lock/並列性は提供しない。WebView搬送とbinding Cookie設定も未提供なので、確認できない橋渡しを創作しない。

case promptは同一の中立な機能説明依頼。期待する経路やReference Outputをpromptに埋め込まない。
fixture READMEは学習用前提であり、模範回答ではない。Issueの注文API例を複写せず、同じ構造的要件を別の合成機能で見る。

輸送は既存の固定SHA→stage→固定Skill→collect --quality、fresh task、独立品質観測を再利用できる。
`task-response-only`は操作一覧を説明本文へ混ぜない機構上の指定で、全体像や必要な経路/条件を削る指定ではない。
prepare_398.pyは歴史的な名前のtransport helperとしてのみ再利用する。新corpusを必ず明示し、旧corpus/旧候補を使わない。

## 事前固定と実行待機

candidate sourceのbasisは意図的に未解決。新#399 SHAが来てから新定義内の根拠引用を確認し、provenanceだけを補う。
旧#398 source引用を適用根拠として流用しない。期待観測を候補出力へ合わせない。
新2ケース各1回のみ。親が実LLM taskを起動する。本準備ではpacket/snapshotもLLM評価も作らない。
旧入力・rubric・結果は保持し、旧失敗を新基準で合格へ読み替えない。公開は合成codeと要件要約のみ。
