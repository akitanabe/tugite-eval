# Round023 — 履歴上の混合11入力、通常対象は8ケース

読者指定の実験はUser指示で廃止済み。追加3件は保留/残件ではなく、今後の通常評価へ含めない。
通常評価は[基本8ケース](../../cases/explain-399/README.md)、[現行設定](../../cases/explain-399/current.json)、[8入力一覧](../../cases/explain-399/inputs.json)。
このroundのindex全件を列挙して起動しない。

## 保持する履歴

当時はseparated/mixed、infrastructure/unknown-connection、shipping正常/境界/欠落依存/意図未共有の基本8件と、
normal/unknown-connection/infrastructureへ読者指定一文を加えた3件を準備した。
そのcorpus・packet・index・quality-protocol・snapshot/sealは変更しない。preregistrationとprovenanceは当時の計画の履歴で、現在の実行指示ではない。
原文の案内はGit履歴にも残る。[廃止記録](RETIREMENT.json)で旧実験を区別する。

## 維持する基本8ケース

候補5cc3e4cefe0d8c9a8b746c86f74cde30a9b732f7、gpt-6.1-sol / medium、fixture・元依頼・override・観測基準は不変。
現行8入力一覧は同じ8packet path/hashを参照し、新しいtrialや再評価をこの整理のために要求しない。
全体説明→主要コード経路→意味上の処理単位の詳細という順序、構造・意味・正確性・重要条件/副作用/境界と不明の扱いを保つ。
関数/class全件一覧・操作の逐語訳・根拠ない目的/保証で代替しない。固定の語数や分割数を新たに導入しない。

## 実行記録

親から基本8直接taskの完了報告を受領。DIRECT_TASKS/EXPECTED_CONDITIONSと旧独立確認待機記録は保持する。
準備workerへ未供給の実応答や実効条件は検証済みと偽らない。直接taskをsealed harness実行として遡及偽装しない。
通常対象はこの8件で完結する。廃止した3件を「全件完了のために必要」とする以前の案内は撤回する。
