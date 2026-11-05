# #399 current evaluation — 基本8ケース

通常評価の正本は[current.json](current.json)、[current-corpus.json](current-corpus.json)、[8件の入力一覧](inputs.json)。
対象候補・モデル要求・fixture・元依頼・override・観測基準は既存基本8ケースから変更していない。
既に実行した8件をこの整理のために再実行する必要はない。

| Case | 内容 |
|---|---|
| explain-399-separated | 分離したSession機能の意味と実経路 |
| explain-399-mixed | 同一Controller内の処理と意味単位の区別 |
| explain-399-infrastructure | 配線・認証・例外・状態確定の基盤 |
| explain-399-unknown-connection | 未提供adapterと未確認接続 |
| explain-this-normal | 配送料の主要処理 |
| explain-this-boundary | テストなしの境界説明 |
| explain-this-failure | 欠落した外部依存 |
| explain-this-ambiguous | 未共有のHuman意図と実装事実の区別 |

全体説明→コード実行経路→意味上の処理単位ごとの詳細という順序を評価する。
コードとの対応、主要条件・副作用・確定/失敗境界、不明を保持する。機械的な関数/class全件一覧、操作の逐語訳、
根拠のない意図/保証で代替しない。構造・意味・順序/単位の3必須観測、その他の既存品質基準は不変。
モデル要求gpt-6.1-sol / medium、通常は各1fresh task。未観測の実効設定はunknownのままにする。

## 通常の入力受渡し

inputs.jsonのpathsはrepository root基準。既存8packetとhashをそのまま参照し、親が必要な試行だけを起動する。
ファイル参照元round023は歴史上11packetを含むarchiveなので、directory全件を列挙せず、この8件一覧だけを使う。
[cloud手順](../../evals/cloud-tasks.md)のstage→固定Skill→collect --qualityを使い、本文と運用証跡を分ける。
親による直接実行はsealed harness実行と区別して記録し、実応答から独立判定する。

将来、候補を更新して新たにfreezeするときも現行corpusを明示する（SHAはcurrent.jsonと整合させる）:

```bash
python3 evals/prepare_398.py candidate 5cc3e4cefe0d8c9a8b746c86f74cde30a9b732f7 .local/NEW_ROUND --corpus cases/explain-399/current-corpus.json
```

prepare_398.pyは既存transport helperの歴史的名称。defaultの旧corpusは使わない。
retired実験を通常対象へ自動復元しない。[履歴区分](history/README.md)は現在の実行指示ではない。

元のcorpus.jsonは初期2caseの凍結済み事前登録資料として不変で残す。現在の実行入口はcurrent.jsonが指すcurrent-corpus.json。

## 関連チェック

```bash
python3 tests/explain-399-current-test.py
python3 tests/explain-399-test.py
python3 tests/explain-399-meaning-test.py
python3 tests/explain-399-structure-test.py
```

現行選択の8件固定、既存packet/hash/モデル条件の保持、archiveのseal/index-protocol hash、初期fixtureと既存意味/構造gateを検査する。
この整理は実LLM試行や過去結果の再採点ではない。
