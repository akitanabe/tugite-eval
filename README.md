# Tugite Eval

[Tugite](https://github.com/akitanabe/tugite) の固定版 Skill を評価するコーパスと証拠・独立判定の基盤です。
32ケース・64版別セルを持ち、継続4 Skillの3版比較と、v7.5.0追加4 Skillの達成評価を分けます。

```bash
python3 tests/eval-runner-test.py
python3 evals/runner.py freeze .local/eval-rounds/sol-medium-001
```

Python 3.12+ / Git / Bashが必要です。固定版は別のTugite repositoryからSHAを指定して取得するため、
初回にGitHubの読み取り接続を使います。詳細は [評価手順](evals/README.md) を参照してください。

現時点の実LLM評価結果は0件で、Skillの優劣・デグレは判定不能です。
現行のnested Codex CLI adapterと環境上の制約は [診断記録](evals/runtime-diagnostics.md) にあります。
Cloud task方式へのadapter再設計は別作業であり、この移植では変更していません。

出典と移植前の対応SHAは [PROVENANCE.md](PROVENANCE.md)、利用条件は [MIT License](LICENSE) を参照してください。
生成round、実行ログ、credential、Tugite本体のGit履歴はこのrepositoryに保存しません。
