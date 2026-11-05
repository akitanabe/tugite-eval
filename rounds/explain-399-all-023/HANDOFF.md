# Round023 — 履歴上の混合集合

通常評価の入口は[現行の基本8ケース](../../cases/explain-399/README.md)、[設定](../../cases/explain-399/current.json)、[8入力一覧](../../cases/explain-399/inputs.json)。
このroundの全indexをそのまま通常起動しない。旧追加3件はUser指示で廃止済み、保留/残件ではない。

基本8packetは変更せず、現行8入力一覧が同じpath/hashを参照する。候補5cc3e4ce、gpt-6.1-sol / medium、fixture・依頼・override・構造/意味/順序の基準は不変。
既存の8直接taskをこの整理のために重複起動しない。将来の試行は現行案内のstage→固定Skill→collect --quality、独立品質判定を使用する。

023の元corpus/packet/index/quality-protocol/snapshotとhashは履歴として不変。DIRECT_TASKS/EXPECTED_CONDITIONS等の実行記録も保持する。
直接taskとsealed harnessの差、未取得の実応答/実効モデルは引き続き区別する。旧入力sealを未実施の実行証拠にしない。
廃止済み3件を未実行通常caseとして集計せず、全件完了のために追加起動を要求しない。RETIREMENT.json参照。
