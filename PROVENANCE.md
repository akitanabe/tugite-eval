# Source provenance

この評価基盤は `akitanabe/tugite` 内のローカル開発ブランチから移植した。Tugite本体の履歴は継承せず、評価用のファイルだけを新repositoryへ追加する。

- Source repository: https://github.com/akitanabe/tugite
- Source branch: `eval/397-versioned-behavior`
- Source HEAD: `f0e438b6c5f1590ca42e7610107bfbaa05f97a89`
- Source tree: `79a1186cf8efb3ec98f1fa8342253c583fd7a61d`
- Source development base: `c44261f1f70da40c75123a91153a8aa6c6d4be1e`
- Destination initial main: `1a5c754d96c00aaae414653bfe8a9fa24d7455d1`（LICENSEのみ）

元のMIT License / Copyright (c) 2026 akitanabe は既存の [LICENSE](LICENSE) と同一であり、変更せず保持する。

| Source / destination path | Source SHA-256 | Migration |
|---|---|---|
| `evals/runner.py` | `558c816a8b2b364f2b833d5cc0f37941266a2ad51549024062e8b2dc00c38914` | 固定版取得を別repositoryの浅いfetchへ変更。Cloud adapter再設計は含まない。 |
| `evals/corpus.json` | `07a4edfabdae5cfbd2f2352623d19e9940c7d23e944b7f1e4e4f9ab188845def` | byte単位で同一。 |
| `evals/README.md` | `16180784701e6302d3ec220f08044309466b9968e9fd38bda1996b4a122ca44c` | 独立repositoryの取得・検証手順へ更新。 |
| `evals/runtime-diagnostics.md` | `bb0ff8e4732c2400aa1dd4733bfd09e492a402a9a4732e82b3cd0e5782618e0f` | byte単位で同一。元環境の観測記録。 |
| `tests/eval-runner-test.py` | `a01fe788aa8580535f87384fc82640bea3eb9ac1b473cde63f190e93648d09c7` | 既存16ケースを保持し、別sourceのsetupと独立objectDB検証を追加。 |

評価対象のfixed SHAは `evals/runner.py` の `VERSIONS` と各roundの `spec.json` に記録する。
生成artifact、raw logs、credential、元repositoryの `.git` / config は移植対象に含まれない。
旧環境の評価結果は実LLM完了0件で、ここでも性能やデグレの結論は追加していない。
