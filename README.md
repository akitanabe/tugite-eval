# Tugite Eval

#399の通常評価は[基本8ケース](cases/explain-399/README.md)と[現行設定](cases/explain-399/current.json)を使用します。過去roundを全件列挙して対象を増やさないでください。

[Tugite](https://github.com/akitanabe/tugite) の固定版 Skill を評価するコーパスと証拠・独立判定の基盤です。
32ケース・64版別セルを持ち、継続4 Skillの3版比較と、v7.5.0追加4 Skillの達成評価を分けます。

```bash
python3 tests/cloud-task-test.py
python3 tests/cloud-receipt-test.py
python3 evals/runner.py freeze .local/eval-rounds/sol-medium-001
```

Python 3.12+ / Git / Bashが必要です。固定版は別のTugite repositoryからSHAを指定して取得するため、
初回にGitHubの読み取り接続を使います。詳細は [評価手順](evals/README.md) を参照してください。

版間比較用の完備したLLM試行は0件で、Skillの優劣・デグレは判定不能です。
初回pilotは [親報告の参考観測](pilots/cloud-pilot-001/REFERENCE.md) として分離しています。
[正常ケース16セルの新round](rounds/cloud-normal-002/README.md) と [親receipt/import](evals/parent-receipts.md) を用意しています。
標準の品質評価は [品質protocolと短い起動prompt](rounds/cloud-normal-002/QUALITY_HANDOFF.md) を使います。
完全transcriptや実効モデルunknownは品質評価を止めません。内部遵守は別の未検証事項です。
1試行ごとに親が新規cloud taskを起動する [cloud adapter](evals/cloud-tasks.md) と
[固定pilot入力](pilots/cloud-pilot-001/input.json) を用意しています。nested Codex CLIは任意の別adapterです。
[旧CLIの診断記録](evals/runtime-diagnostics.md) はその実測履歴です。

出典と移植前の対応SHAは [PROVENANCE.md](PROVENANCE.md)、利用条件は [MIT License](LICENSE) を参照してください。
生成round、実行ログ、credential、Tugite本体のGit履歴はこのrepositoryに保存しません。

#403 の追加評価は [walkthrough / explain-code の10ケース](cases/walkthrough-403/README.md)。旧名称 `code-explain`・参照例復元前の固定SHAをGit経由で独立eval環境へ取得し、10ケース・30応答の実評価と独立判定を完了しました。現在の改名後候補は実モデル未再評価です。出力上の不合格は0件で、内部Skill利用・権限操作の確認には未確定事項が残ります。評価対象SHA・詳細結果・限界はリンク先を参照してください。これは単独達成評価であり、#399 の通常対象は変更しません。

#405 の追加評価は [plan-align の7ケース](cases/plan-align-405/README.md)。固定候補の入力と評価基準を準備済みで、独立tugite-eval-containerでの実モデル評価は未実施です。
