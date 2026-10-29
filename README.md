# Tugite Eval

[Tugite](https://github.com/akitanabe/tugite) の固定版 Skill を評価するコーパスと証拠・独立判定の基盤です。
32ケース・64版別セルを持ち、継続4 Skillの3版比較と、v7.5.0追加4 Skillの達成評価を分けます。

```bash
python3 tests/cloud-task-test.py
python3 tests/cloud-receipt-test.py
python3 evals/runner.py freeze .local/eval-rounds/sol-medium-001
```

Python 3.12+ / Git / Bashが必要です。固定版は別のTugite repositoryからSHAを指定して取得するため、
初回にGitHubの読み取り接続を使います。詳細は [評価手順](evals/README.md) を参照してください。

比較用の完備したLLM試行は0件で、Skillの優劣・デグレは判定不能です。
初回pilotは [親報告の参考観測](pilots/cloud-pilot-001/REFERENCE.md) として分離しています。
[正常ケース16セルの新round](rounds/cloud-normal-002/README.md) と [親receipt/import](evals/parent-receipts.md) を用意しています。
標準の品質評価は [品質protocolと短い起動prompt](rounds/cloud-normal-002/QUALITY_HANDOFF.md) を使います。
完全transcriptや実効モデルunknownは品質評価を止めません。内部遵守は別の未検証事項です。
1試行ごとに親が新規cloud taskを起動する [cloud adapter](evals/cloud-tasks.md) と
[固定pilot入力](pilots/cloud-pilot-001/input.json) を用意しています。nested Codex CLIは任意の別adapterです。
[旧CLIの診断記録](evals/runtime-diagnostics.md) はその実測履歴です。

出典と移植前の対応SHAは [PROVENANCE.md](PROVENANCE.md)、利用条件は [MIT License](LICENSE) を参照してください。
生成round、実行ログ、credential、Tugite本体のGit履歴はこのrepositoryに保存しません。
