# Round007: candidate2 sample handoff

親指定candidate `f69dcced4b64ee932b84b05ec8d31ddac2637762`、tree `d5d0b3e7966841752f3a67570dac4e11e25e785a`。
[2件のpath/hash](INPUTS.md)、[index](index.json)、[provenance](PROVENANCE.json)を使用する。
各case candidate trial1のみ。実LLM試行・採点は未実施。

意味の中心基準は9ad9047…、中立promptはcd597e79…で固定した。
source全体改訂に伴う引用だけを5e95ded…で対応し、その後corpusはbyte不変。
暫定6bのpacketは作っていない。旧004/005/006の入力・基準・結果は保持し、新適合の根拠にしない。

[要件](../../cases/explain-398-concise-flow/README.md) / [harness監査](../../cases/explain-398-concise-flow/AUDIT.md) /
[judge用事実参照](../../cases/explain-398-concise-flow/REFERENCE.md)。
中心は処理フローと、その中で各関数/classが何をするか。識別子先頭は維持し、内部講義や網羅的役割catalogを目標にしない。
重要な接続と正確さを保持し、固定の語数/行数/templateや受理例文を要求しない。

**Skillだけでなくprompt・response reporting・rubricも旧006から変更。Skill単独の改善効果は主張できない。**
新promptはフローと役割を尋ねる中立な依頼で、解答templateや受理済みfixture回答を含めない。
`response_reporting=task-response-only`により操作一覧の出力義務を外し、collector/親が機構証拠を別に保持する。

## 親がfresh taskへ送るprompt

`<EVAL_SHA>`はこのinputsを含む最終remote main完全SHA、`<INPUT_PATH>`/`<INPUT_SHA256>`はINPUTS.mdから選ぶ。
1taskに1packet、fresh eval環境、requested gpt-6.1-sol / medium。

```text
新規の1試行です。要求設定gpt-6.1-sol / medium。
Repo=https://github.com/akitanabe/tugite-eval.git、cwd=/workspace/tugite-eval、固定code/data SHA=<EVAL_SHA>。
checkoutがなければ通常clone。既存ならtop-levelとorigin URLがこのrepoと一致することを確認。
次を一つずつ成功確認して進める:
git fetch --no-tags https://github.com/akitanabe/tugite-eval.git <EVAL_SHA>
git cat-file -e <EVAL_SHA>^{commit}
git status --porcelain=v1 --untracked-files=all
statusが空ならgit checkout --detach <EVAL_SHA>、git rev-parse HEADが指定SHAと一致することを確認。
失敗/dirty/別repoなら保持して停止。force/reset/cleanは使わない。
repo cwdで:
python3 evals/cloud_task.py stage <INPUT_PATH> <INPUT_SHA256> /workspace/quality-stage
固定SHAの通常fetchを許可。/workspace/quality-stage/prompt.txtを読み、指定固定Skillを最初に読み、指定fixtureで依頼に応答する。
現行Skill/corpus/control/snapshot/rubric/REFERENCE/他版/旧応答は読まない。採点/nested CLI/push/依存導入/fixtureからの外部通信をしない。
/workspace/quality-response.txtには依頼への説明本文だけを保存する。操作したファイル/commandsや環境報告を追記しない。理解を左右する未確認箇所は本文の該当箇所で短く示す。実行上の拒否/失敗は説明本文と別に正確に報告する。
repo cwdで:
python3 evals/cloud_task.py collect /workspace/quality-stage <INPUT_SHA256> /workspace/quality-response.txt /workspace/quality-result --quality
最終返却は説明本文、result directory、result-seal.jsonのSHA-256。内部証跡/実効modelが未観測なら不明のまま。
拒否時は操作/対象/理由/完了部分/denied-pending-uncertainを正確に返して停止し、迂回しない。
```

Humanへ提示するのはresponse.txtの説明本文。seal/path等の輸送情報や環境報告は別に保持する。
control/rubric/REFERENCE/旧出力は被評価taskへ渡さない。完全内部証跡・実効model不明は制約のまま扱う。

**親が2case各1回の実際の本文をHumanへ提示し、判断待ちで停止。追加case・反復・全件展開・version更新・PRは禁止。**

## 回収と必要な独立品質観測

親がtask完了と回収物/input hashを対応付け、quality-post-template.jsonの値を実観測で埋める。
quality-importを使う場合はsnapshotを新directoryへrestoreし、そのroundと各attemptへimportする。
別contextのjudgeには新rubricとREFERENCEを渡す。細部の全項目転記を求めず、記述した事実の誤りや重要な欠落は保持する。
単回sampleを反復比較や因果的優劣の証拠にしない。追加実行を自動起動しない。

```bash
python3 evals/cloud_receipt.py restore rounds/explain-398-concise-flow-007/snapshot .local/concise-live
```

以降:

```bash
python3 evals/cloud_receipt.py quality-import .local/concise-live \
  .local/concise-live/attempts/CASE--candidate--1 \
  rounds/explain-398-concise-flow-007/inputs/CASE--candidate--1/input.json \
  RESULT QUALITY_POST_JSON PARENT_COMPLETION_DIRECTORY rounds/explain-398-concise-flow-007/quality-protocol.json
```

準備QA: 新静的3件成功。既存mode/import機構54件の成功に加え、実candidateでsnapshot restore、
固定case/packet mode照合と2stage smokeを確認。stageの操作一覧要求は除外済み。
corpus byte不変、2cases candidate/trial1、fixture保持、rubric非混入、公開scan/diff check、旧履歴無変更を確認。
これらは準備機構の検証であり、Skillの実出力品質や内部遵守の評価ではない。
