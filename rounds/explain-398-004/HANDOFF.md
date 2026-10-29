# #398 fresh task handoff

親だけが実trialを起動し、別contextのjudgeへ採点を委ねる。このroundは準備のみで実行結果ではない。
意味のfreeze commitは `11b7dcdecb470050e4b35eb0ec2cce8c4ddeed90`、adapter commitは
`0d2c38290c60abac4d52ee7e091bd4343f4fce11`。全配布物を保持し、candidate出力は未参照。
[根拠と期待観測](../../cases/explain-398/EXPECTATIONS.md)、[source provenance](PROVENANCE.json)、
[全input path/hash](INPUTS.md)、[機械可読index](index.json) を参照する。

baselineは `c44261f1f70da40c75123a91153a8aa6c6d4be1e`（main観測済み、7.5.1）、
candidateは `2e7ae9237103cc9a6c6d9afbb748c11ad2ea51e7`。
候補SHA到着前にcorpus/fixture/期待観測をcommit固定した。
SHA受領後は候補配布Skillの仕様引用と配布物identityだけを確認した。
`PROVENANCE.json` に新要求と候補source引用を追記したが、corpusと期待観測の意味は変更していない。

## 起動順とscope

まず重点3casesを両版各1回、既存回帰4casesをcandidate各1回＝10試行。
機能ケースを最優先に、受入判断に重要な差がある重点ケースは両版trial2/3も起動する。
全重点3casesを3回にしても22試行。比較の方向を主張するケースは両版3回と独立judgeを必要とする。
全22 packetを事前生成しているが、試行や採点はしていない。#397の83件は今回のscopeに含めない。

## 親が送るprompt

`<DELIVERY_SHA>` はこのhandoffとinputsを含む最終remote main完全SHA。
`<INPUT_PATH>` / `<INPUT_SHA256>` はINPUTS.mdから選ぶ。1taskにつき1packet、fresh task、
開発環境ではなくtugite-eval-container、requested model gpt-6.1-sol / mediumを使う。
この親文書・control/rubricは評価対象taskへ読ませない。

```text
新規の1試行を実行してください。要求設定gpt-6.1-sol / medium。
Repo=https://github.com/akitanabe/tugite-eval.git、cwd=/workspace/tugite-eval、固定code/data SHA=<DELIVERY_SHA>。
checkoutがなければ通常clone。既存ならtop-levelとoriginがこのrepoであることを確認。
次を逐次成功確認: git fetch --no-tags https://github.com/akitanabe/tugite-eval.git <DELIVERY_SHA> → git cat-file -e <DELIVERY_SHA>^{commit} → git status --porcelain=v1 --untracked-files=all（空を確認）→ git checkout --detach <DELIVERY_SHA> → git rev-parse HEAD（指定SHA一致）。失敗・dirty・別repoなら保持して停止。force/reset/cleanは使わない。
cwd=/workspace/tugite-evalで:
python3 evals/cloud_task.py stage <INPUT_PATH> <INPUT_SHA256> /workspace/quality-stage
固定SHAの通常fetchを許可。続いて/workspace/quality-stage/prompt.txtを読み、指定の固定版Skillを最初に読んで/workspace/quality-stage/workspaceで作業。
解決する参照と依存も固定配布物内。現行Skill・corpus/control/snapshot/rubric・他版/過去結果は読まない。採点・nested CLI・push・依存導入・評価fixtureからの外部通信をしない。
完全応答を/workspace/quality-response.txtへ保存。元のrepo cwdで:
python3 evals/cloud_task.py collect /workspace/quality-stage <INPUT_SHA256> /workspace/quality-response.txt /workspace/quality-result --quality
最終返却は応答本文、成果物所在、result-seal.jsonのSHA-256、読んだ固定Skill/参照、制約。完全transcriptは不要。実効model/内部操作は未観測なら不明。拒否なら操作・対象・理由・完了済部分・denied/pending/uncertainを正確に返す。
```

stage生成promptは固定配布物内のexplain-thisと参照を指定し、ケースごとの自然な依頼を末尾に置く。
各promptの本文はinput.jsonのprompt欄にある。重点の問いは次のとおり。

- session-flow: prepare→issue→exchange→Cookie認証→cart取得を、機能理解に必要な粒度でコードへ対応づける。
- infrastructure: app.build/Dispatcher/SessionAuth/transaction自体を説明する。
- unknown-connection: 未提供adapterとCookie認証の接続を持つ範囲を、分かる点から説明する。

## 回収・独立judge

[既存quality手順](../cloud-normal-002/QUALITY_HANDOFF.md) と同じoutput-quality-v1。
親がtask完了を観測し、response/artifact sealをinput SHAと対応付ける。
quality-post-template.jsonのnullを実際の値で埋める。完全内部証跡/実効model不明は制約として残し、品質評価を止めない。
判定根拠は出力/成果物であり、内部遵守の保証はしない。

```bash
python3 evals/cloud_receipt.py restore rounds/explain-398-004/snapshot .local/explain-398-live
python3 evals/cloud_receipt.py quality-import .local/explain-398-live \
  .local/explain-398-live/attempts/CASE--VERSION--TRIAL \
  rounds/explain-398-004/inputs/CASE--VERSION--TRIAL/input.json \
  RESULT QUALITY_POST_JSON PARENT_COMPLETION_DIRECTORY rounds/explain-398-004/quality-protocol.json
python3 evals/runner.py judge-template .local/explain-398-live \
  .local/explain-398-live/attempts/CASE--VERSION--TRIAL judgment.json
# 別contextの独立judgeが対応rubric/共通品質と実出力を読み判断する
python3 evals/runner.py adjudicate .local/explain-398-live \
  .local/explain-398-live/attempts/CASE--VERSION--TRIAL judgment.json
python3 evals/runner.py report .local/explain-398-live
# 両版3回を完了・独立採点したケースの比較だけをnative compareへ渡す
python3 evals/runner.py compare .local/explain-398-live comparison.json
```

common metricは重点ケースでtraceability/usefulness/accuracy/conciseness-without-loss。
baseline旧版適合とcandidate #398達成を分け、意図的変更を回帰扱いしない。
単回だけのケースは独立judgeのoutput_qualityとして記述的評価を残し、reportの3回未完了indeterminateを成功/失敗に偽装しない。

## 準備QA

独立した読み取り専用reviewerがケース準備、fixture期待観測、code/adapterを確認した。
親の自己QAでobligation/oracle/validation planeを確認し、fixture事実は静的読解と意味のある小さなPython検証で裏づけた。
fixtureテストの実行は学習用codeの検証であり、被評価Skillのtrialではない。

- 既存eval-runner 17件、cloud-task 28件、cloud-receipt 23件成功。
- 新規6件成功。paired別rubric、snapshot restore、固定SHA stage、quality collect/seal、map不一致/placeholder拒否、既存回帰保持、fixture分岐/副作用/失敗境界を検証。
- 独立reviewerも新規6件を実行し成功。fixtureの正常/拒否/commit失敗/Cookie失敗を独立手計算して一致。
- 実baseline/candidate配布物のsnapshot restoreとstage smoke、22packetのhash/SHA/評価基準非混入を確認。
- git diff --check成功。Tugitecoreと既存rounds/resultsは変更していない。

限界: 実LLMの出力品質は未評価。新mapでquality-importから方向付き比較までを実trialで通した証拠はない。
既存機構テストと新mapのrestore/stage/collectまでは検証済み。実効modelとsource/runtime差は未観測なら不明を維持する。
