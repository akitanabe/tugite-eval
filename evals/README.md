# Tugite behavior evaluation

[Tugite Issue #397](https://github.com/akitanabe/tugite/issues/397) の振る舞い評価を、独立した `akitanabe/tugite-eval` repository で管理する。
評価対象は配布済み `plugins/codex` 全体。source の静的 lint、契約検査と LLM の振る舞い評価は別の証拠である。
初回cloud pilotは親から実行成功が報告されたが、pre receiptと完全transcriptがなくreference-onlyである。
比較用の完備した試行は0件で、Skillの優劣は判定不能である。
[正常ケース新round](../rounds/cloud-normal-002/README.md) と [親receipt/import](parent-receipts.md) を用意している。
親がfresh cloud taskを起動する [cloud adapter](cloud-tasks.md) ではnested CLIを必要としない。
以下の `run` とcanaryの説明は任意のnested CLI adapterに適用する。

## 評価単位と事前固定

| Track | Entry skills | Applicable versions |
|---|---|---|
| 共通比較 | impl-lead / test-report / test-verify / visualize-that | v7.3.7 / v7.4.0 / v7.5.0 |
| 新規仕様達成 | explain-this / review-propose / impl-plan / impl-review | v7.5.0 |

固定 SHA は `runner.py` の `VERSIONS` にある。新規 Skill の存在しない旧版セルは作らない。
入口以外の Skill、参照、assets、custom agents は各固定版の配布物を丸ごと保持する。
32 ケース（8 Skill × 正常・境界・失敗・曖昧）、64 版別セル。通常の初期試行は各セル3回。
`corpus.json` の fixture、prompt、期待観測、適用版、仕様引用と共通 metric の判定境界を実行前に固定する。
配送料の独立した `requirements.md` が fixture の要求根拠であり、被評価応答から正解を作らない。
ケースの意味判断は独立 evaluator が行い、特定の文言・HTML・担当・分割数を唯一解にしない。

`freeze` は存在しない round directory にだけ書く。配布物を Git SHA から取得し、仕様引用の存在と内容 hash、
解決済み fixture、runner 自身を seal に記録する。round 作成後は期待値を変えない。
修正が必要なら理由付きの別 round を作り、旧 round を保存する。seal は通常の hash による同一性検査であり、
ホスト管理者に対する署名・改竄防止機構ではない。

版差の適用例:

- test-report: v7.3.7 は topology と観測限界。v7.4.0 / v7.5.0 は根拠付きの静的診断と全観測範囲の詳細も評価する。
- test-verify: v7.3.7 の snapshot / commit lifecycle と、v7.4.0 / v7.5.0 の no-change route・commit authority を分ける。
- impl-lead: v7.3.7 / v7.4.0 の実行前 Unit Design と、v7.5.0 の impl-plan 依存・委譲 readiness を分ける。

版別適合は applicable observations、共通品質は固定した common metrics で判定する。
意図的な責務変更を common metric の失敗へ読み替えない。

## セットアップと最小実行

Python 3.12+、Git、Bashが必要。Pythonの追加依存はない。`run` を選ぶ場合のみCodex CLIも必要。
`freeze` は `https://github.com/akitanabe/tugite.git` から指定3 SHAを一時的な別Git repositoryへ浅く取得する。
このeval repositoryのobject databaseにTugiteのcommitがあることを前提にせず、core履歴を取り込まない。
GitHubへの読み取り接続が必要。既存のローカルGit sourceを使う場合は `freeze ... --source-repo /path/to/tugite` を明示する。
一時source repositoryは配布物展開後に削除され、sourceの指定と固定SHAは `spec.json` に残る。
テストも最初に同じ固定SHAだけを一時sourceへ取得し、各roundにはその別sourceを明示する。
credential 作成、login、権限拡大や有料契約はセットアップに含めない。

```bash
python3 tests/eval-runner-test.py
python3 evals/runner.py freeze .local/eval-rounds/sol-medium-001
python3 evals/runner.py prepare .local/eval-rounds/sol-medium-001 test-report-normal v7.3.7
python3 evals/runner.py run .local/eval-rounds/sol-medium-001 \
  .local/eval-rounds/sol-medium-001/attempts/test-report-normal--v7.3.7--1
python3 evals/runner.py report .local/eval-rounds/sol-medium-001
```

まずこの1ケースの入力固定→実行→証拠保存→独立裁定→レポートを確認し、その後にケースを展開する。
`run` は隔離が確認できなければ `execution.json` に `blocked / infrastructure-only` を保存し、LLM を起動しない。
CLI の終了コード0は証拠保存の成功を示す。評価成功は `execution.json` の状態と独立裁定を読む。
`--synthetic` はテストダブル用で、出力が実行成功形式でも LLM 証拠に昇格できない。

`prepare` は各試行に新しい Git repository を作る。参照 remote は作らない。
元 fixture の commit、レビュー対象の working diff、無関係な dirty、設定、Skill discovery を区別して保存する。
custom agents は固定版 installer で新規導入する。配布定義は不変、試行側の model / effort overlay は別 hash で記録する。
親子の要求 baseline は `gpt-6.1-sol / medium`。元の配布 agent の設定も記録する。
モデル更新は `freeze --model ... --effort ...` で別 round を作る。Tugite SHA の更新とは独立して管理する。

## Runner が検証する境界

Codex の named permission profile を `sandbox` と `exec` に同じ設定で渡す。
対象外 checkout と credential の tool read、対象外 write、配布物・agent設定・discovery変更、
実際の local Git push、到達可能な TCP socket を canary で確認する。許可した fixture write も確認し、
probe 自体の起動失敗を「隔離成功」と数えない。canary は秘密を含まない専用ファイルだけを用いる。

model の指示は隔離証拠ではない。shell の filesystem / network 制御を検査しても、ホスト管理者や
別経路の server-side tool を制御した証明にはならない。user config を除外し apps / web search を無効化するが、
runtime が提供する全 tool の列挙・設定効果は未検証のため、初回稼働時にログで確認する。
実行 adapter の positive path は synthetic の機構テストだけで確認済みであり、Codex 本体での成功は未検証。
未知の CLI、設定を受理しない CLI、canary failure では停止する。
reviewer 不在ケースは multi_agent を無効化する設定を記録する。実際の非提供はログでも確認する。
renderer 不在ケースは browser・image・shell 群を無効化して features list で確認する。この runtime は unified_exec が true に正規化されるため、全除去を確認できず fail-closed で停止する。
残りの失敗ケースは不存在 runner、未提供 source、実行前提不足など、fixture と明示 authority で構成する。

現 cloud で観測した具体的ブロッカー:

1. Codex CLI 0.163.0 の nested `sandbox` が `app-server socket directory must be a user-owned directory with mode 0700` で起動できない。
2. 既存認証を使う最小の実接続 probe が `wss://chatgpt.com/backend-api/codex/responses` への proxy CONNECT 403 で拒否された。
   destination-policy denial を迂回せず停止した。恒久設定変更や新 credential は行っていない。
3. standalone bubblewrap probe も uid map の read-only error。独立した sandbox 起動可能環境での再検証が必要。

これらはSkillのfailureやregressionを示さない。nested CLI adapterの稼働前提であり、fresh cloud task方式の前提ではない。
Cloud / dot 間の自動実行 API は確認できていない。dot への手動委任はこの CLI と round を受け渡す方式とし、
権限・sandbox・認証・ネットワークの前提を受け側で再検証する。

## 証拠と独立判定

`attempt.json` は試行 ID、固定 repo SHA、親の要求、利用可能な agent 定義と元設定、overlay hash、runtime、
初期 snapshot を保持する。`execution.json` は実行状態、実効設定、ロード観測、コストと制約を保持する。
新規 session は `codex exec --ephemeral`。resume/fork は使わない。
`events.jsonl` / `stderr.txt`、実行後 diff / status / file hash、新規・ignored を含む成果物本文を保存し seal する。
初期 fixture・HEAD・diff・agent設定・discovery を実行直前に再検証し、報告時にも証拠・裁定 seal を再検証する。
10 MB を超えたログは切詰めと明記し、完成した証拠と扱わない。

親子の実効 model / effort、実際の子選択、ロード済み配布物は**未観測なら null**。decoder は子の requested / resolved-at-creation、provider response、全文 read の出典を分けて記録する。
要求値、agent 定義、thread.started、model の自己申告で埋めない。
staged inventory とロード証拠を混同しない。実際の cat/read の出力・tool transcript などを evaluator が確認し、
依存ロードや実効設定が判定に重要で未観測なら indeterminate と理由を残す。
対応する runtime event が公開されない場合や依存が暗黙注入される場合は不明を保持し、この基盤の hash だけからロード完了とは主張しない。
usage は runtime 出力があれば保存、金額 cost は不明可。

ログに bearer/token の代表パターンを redact するが、完全な DLP を保証しない。
fixture に秘密を使わず credential/environment を dump しない。共有前に成果物を点検する。
credential や user home のコピーを round や bundle へ含めない。

```bash
python3 evals/runner.py judge-template ROUND ATTEMPT /tmp/judgment.json
# 別 evaluator が rubric と sealed evidence を読み、各項目に result/reason/evidence を記入
python3 evals/runner.py adjudicate ROUND ATTEMPT /tmp/judgment.json
python3 evals/runner.py report ROUND
```

judgment の `judge_id` は evaluator identity、`independent=true` は実行担当と独立して判定したことの申告。
機械が独立性や意味判断の正しさを保証するわけではない。可能なら evaluator を version 名から盲検化し、
必要な applicable rubric と証拠だけを渡す。引用や定義から版が分かる限界は残る。
pass/fail は該当項目の意味判断と sealed evidence の参照を必須にする。
infrastructure-only / synthetic 証拠は Skill の pass/fail を成立させない。
裁定は追記不能・上書き不能。裁定の訂正は別 round と理由で保存する。

## 反復・比較と停止

初期3試行。食い違い・判定不能があり具体的調査理由を事前記録できる場合だけ `--trial 4/5 --reason ...` を使う。
最大5試行。安全性失敗、環境拒否、identity drift、同じ証拠で進展しない場合は追加試行を止める。
拒否済み操作を同条件で繰り返さない。3試行未完了は比較の判定不能とし、欠損を Skill failure にしない。
小標本で統計的有意性を主張しない。版別適合の pass/fail 集計と、共通品質の比較裁定は別軸である。

独立 evaluator の比較裁定例（`round_id` は `spec.json` から取得）:

```json
{
  "round_id": "ROUND-ID",
  "judge_id": "independent-evaluator",
  "independent": true,
  "decisions": [{
    "case_id": "test-report-normal",
    "baseline": "v7.3.7",
    "candidate": "v7.5.0",
    "result": "indeterminate",
    "reason": "実行証拠不足。版固有の診断追加は回帰と扱わない。",
    "metric_ids": ["authority-and-scope", "task-usefulness"],
    "evidence": []
  }]
}
```

`compare ROUND FILE` で保存し `report ROUND` で反映する。
改善 / 悪化 / 同等 / 判定不能を `improved / worsened / equivalent / indeterminate` で記録する。
方向付き比較には両版の初期3試行すべての completed LLM evidence と独立裁定が必要。
実効設定不明・モデル差・版差・意図的仕様変更・試行ばらつきの留保を reason に保持し、因果的優劣を結論しない。
新規4 Skill は単独達成評価であり、比較裁定へ入れない。

継続 Skill の v7.5.0 回帰疑いは、再現条件、固定 SHA、事前期待と根拠、反復結果、実行証拠、
意図的変更との区別、観測限界をまとめ、親 QA 後の Issue 記載候補にする。
この基盤は自動投稿しない。評価基盤の変更に被評価 Skill の修正を混ぜない。

## 静的検証

```bash
python3 tests/eval-runner-test.py
git diff --check
```

このrepositoryのPython・JSON・評価文書はここで検証する。Tugite本体の契約・配布生成物はsource repository側のGunte、
Skill文書のlintはsource repository側のtextlintが所有し、本repositoryへ検査基盤を複製しない。
これらの静的検査をLLMの意味遵守の評価に読み替えない。

具体的な再現コマンド、設定の最小変更案、実装不足と観測限界の分類は [runtime-diagnostics.md](runtime-diagnostics.md) を参照。

## #398 explain-this comparison

新しい固定SHA比較は [事前固定ケース](../cases/explain-398/EXPECTATIONS.md) と `prepare_398.py` を使う。
`runner.py freeze --version-map MAP.json` は明示したlabel→完全SHAを新roundに固定する。
既定の#397版集合・既存round/resultsは保持する。schema3 cloud inputは選択した版だけのfixed_versionsを含み、
input hashと実fetch SHA、配布物inventoryをstageで照合する。候補未確定のplaceholderは実行できない。
