# Output quality handoff (parent)

品質比較の標準経路は `output-quality-v1`。ユーザーの「完全な証跡は不要。クオリティが維持されていればよい」という判断を適用する。
[quality-protocol.json](quality-protocol.json) を実行前に固定し、既存16セルのfixture/rubricを変更せず使う。
旧strict setup/pre-receipt/run経路は任意の監査用途として保持する。
初回pilotは参考のまま。この品質protocolで再分類・比較母集団への移入はしない。

- 全inputのpath/hash/case/version: [QUALITY_INPUTS.md](QUALITY_INPUTS.md)
- 機械可読な一覧: [index.json](index.json)
- Protocol SHA-256: `1f63eb00f44e527aaea2393c43d4daa739001b5daff6b89bb52cef38895e1513`
- 起点: test-report-normal / v7.3.7 / trial 1
- Requested: gpt-6.1-sol / medium

## 親がそのまま送るprompt

`<CODE_SHA>` だけを最終handoffの完全SHAに置換し、新規eval taskへ送る。他caseにはindexのinput path/hashを入れ替える。

```text
新規の1試行を実行してください。要求設定はgpt-6.1-sol / mediumです。
Repo=https://github.com/akitanabe/tugite-eval.git、cwd=/workspace/tugite-eval、固定code SHA=<CODE_SHA>。
checkoutがなければ通常cloneし、既存checkoutではtop-levelとorigin URLを確認してください。
次を一つずつ成功確認して進めてください: git fetch --no-tags https://github.com/akitanabe/tugite-eval.git <CODE_SHA> → git cat-file -e <CODE_SHA>^{commit} → git status --porcelain=v1 --untracked-files=all（空を確認）→ git checkout --detach <CODE_SHA> → git rev-parse HEAD（指定SHA一致）。失敗・dirty・別repoなら保持して停止し、force/reset/cleanは使いません。
cwd=/workspace/tugite-evalで次を実行してください。
python3 evals/cloud_task.py stage rounds/cloud-normal-002/inputs/test-report-normal--v7.3.7--1/input.json a47763ea50c0a7dad7ce6d80314287a06b2ea08b47ef5d5b73abd0798de81183 /workspace/quality-stage
固定SHAの通常fetchは許可されています。続いて/workspace/quality-stage/prompt.txtを読み、指定された固定版Skillを最初に読んで、/workspace/quality-stage/workspaceで作業してください。現行Skill・corpus/control/snapshot・他版や過去結果は読みません。採点・nested CLI・外部通信・push・依存導入は行いません。実行に必要な権限や能力がなければblockedとして正確な理由を返し、架空の証拠で代替しません。
完全な応答を/workspace/quality-response.txtへ保存し、元のrepo cwdで次を実行してください。
python3 evals/cloud_task.py collect /workspace/quality-stage a47763ea50c0a7dad7ce6d80314287a06b2ea08b47ef5d5b73abd0798de81183 /workspace/quality-response.txt /workspace/quality-result --quality
最終返却は応答本文、成果物の所在、result-seal.jsonのSHA-256、実際に読んだ固定Skill/参照、観測できた制約です。完全な操作transcriptは不要です。実効モデル・内部遵守・費用などは不明なら推測しません。失敗時は対象・操作・理由・完了済み部分・結果状態を返してください。
```

## 親の回収と独立品質評価

親はtask完了を実際に観測し、回収した応答・全artifactをinput/Skill/requested model/trialへ対応付ける。
[quality-post-template.json](quality-post-template.json) の識別子・hash・観測値を実際の値で埋める。
`completion_evidence` は親が保持したtask完了通知/最終応答などのfileへの参照。完全tool transcriptは不要。
`observation_source=parent-task-completion` は親が実際に見た完了通知に使い、子だけの自己申告へ付けない。
親の完了通知にturn IDがなければnullでよい。実効モデルunknownもそのままでよい。
必要な実行権限の拒否が観測された場合はcapability_blockersへ記録し、blockedにする。

```bash
python3 evals/cloud_receipt.py restore rounds/cloud-normal-002/snapshot .local/quality-normal
python3 evals/cloud_receipt.py quality-import ROUND ATTEMPT INPUT RESULT QUALITY_POST_JSON PARENT_COMPLETION_DIRECTORY \
  rounds/cloud-normal-002/quality-protocol.json
python3 evals/runner.py judge-template ROUND ATTEMPT judgment.json
# 別contextのjudgeが適用rubric/共通metricと実出力を評価する
python3 evals/runner.py adjudicate ROUND ATTEMPT judgment.json
python3 evals/runner.py report ROUND
```

独立judgeは出力品質の総合判断をjudgmentの追加field `output_quality={result,reason,evidence}` に記録できる。
既存observations/common_metricsの意味は変更しない。artifactで観測できる部分を判定し、内部権限・隠れた操作など
観測できない項目はindeterminateにする。品質PASSは内部遵守保証ではない。
既存reportにはjudgment全体が保存される。内部観測不足によるspec_conformanceのindeterminateと、出力品質判断を区別する。
出力品質の比較は既存compareの共通metricから観測可能な軸を選び、別contextの独立判断を保存する。
完全transcript・pre receipt・実効モデルunknownは、品質試行のcompletedや比較参加を妨げない。

まず正常16セルを各1試行で通し、継続4 Skillの版間判断は原則各版3試行で行う。
追加trial 4/5は不一致のときだけ事前理由を記録する。新規4 Skillはv7.5.0の独立仕様達成として扱う。
全正常ケース後に境界/失敗/曖昧へ進む。単一試行からモデル優劣や仕様起因の回帰を結論しない。
