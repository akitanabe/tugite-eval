# Round008: fixed-harness candidate pair

Candidate `886b43e8cf7b39ea1d876cdd314213710066e3a2`、tree `837e818713d203ad9a3b60e81ff6585ab93f6a3f`。
[2件のpath/hash](INPUTS.md)、[index](index.json)、[provenance](PROVENANCE.json)を使う。candidate各1回のみ。実LLM試行・採点は未実施。

Round007のprompt・fixture・期待観測・common metrics・response_reportingを固定し、変更はsource根拠引用と版/packet identityだけ。
旧引用がcandidateに無かったため、short-implementation-firstのbasis.quoteだけを実sourceへ対応させ、他の内容の一致を確認した。
最初の旧引用での準備はpacket作成前に停止。LLM試行ではない。旧007以前の入力・結果は保持している。

基準は[Round007の要件](../../cases/explain-398-concise-flow/README.md)と[事実参照](../../cases/explain-398-concise-flow/REFERENCE.md)。
処理フローと各関数/classの役割を短くつなぎ、重要な接続とコードに沿う正確さを保つ。
全内部項目の列挙、回答template、語数/行数制限を追加しない。REFERENCE/rubricを被評価taskへ渡さない。

## Fresh task用prompt

`<EVAL_SHA>`は本inputsを含む最終remote main完全SHA、`<INPUT_PATH>`/`<INPUT_SHA256>`はINPUTS.mdから選ぶ。
各taskは独立fresh eval環境、requested gpt-6.1-sol / medium。1taskに1packet。

```text
新規の1試行です。要求設定gpt-6.1-sol / medium。
Repo=https://github.com/akitanabe/tugite-eval.git、cwd=/workspace/tugite-eval、固定code/data SHA=<EVAL_SHA>。
checkoutがなければ通常clone。既存ならtop-levelとorigin URLがこのrepoと一致することを確認。
次を一つずつ成功確認:
git fetch --no-tags https://github.com/akitanabe/tugite-eval.git <EVAL_SHA>
git cat-file -e <EVAL_SHA>^{commit}
git status --porcelain=v1 --untracked-files=all
statusが空ならgit checkout --detach <EVAL_SHA>、git rev-parse HEADが指定SHAと一致することを確認。
失敗/dirty/別repoなら保持して停止。force/reset/cleanは使わない。
repo cwdで:
python3 evals/cloud_task.py stage <INPUT_PATH> <INPUT_SHA256> /workspace/quality-stage
固定SHAの通常fetchを許可。/workspace/quality-stage/prompt.txtを読み、指定固定Skillを最初に読み、指定fixtureで依頼に応答する。
現行Skill/corpus/control/snapshot/rubric/REFERENCE/他版/旧応答は読まない。採点/nested CLI/push/依存導入/fixtureからの外部通信をしない。
/workspace/quality-response.txtには依頼への説明本文だけを保存する。操作ファイル/commandsや環境報告を追記しない。理解を左右する未確認箇所は本文の該当箇所で短く示す。実行上の拒否/失敗は本文と別に正確に報告する。
repo cwdで:
python3 evals/cloud_task.py collect /workspace/quality-stage <INPUT_SHA256> /workspace/quality-response.txt /workspace/quality-result --quality
最終返却は説明本文、result directory、result-seal.jsonのSHA-256。内部証跡/実効modelが未観測なら不明のまま。
拒否時は操作/対象/理由/完了部分/denied-pending-uncertainを正確に返して停止し、迂回しない。
```

Human向け説明本文と、親が保持する輸送・実行証拠を分ける。全pair/attemptを保持し、都合のよいsampleだけを選ばない。
親は2件の品質を判断し、必要なら次のcandidateで同じ2caseを反復できる。以前の毎pair後のHuman待機条件は更新されている。
**このroundでは2case各1回だけ。全suite・追加case・version更新・PRは行わない。**

Round007とのprompt/fixture/criteriaは固定したが、小標本・未観測の実効model/runtime・応答ばらつきから因果/model優越を主張しない。
Round006以前との比較にはharness変更の留保も維持する。

## 回収

必要なら`quality-post-template.json`を親の実観測で埋め、下記roundへquality-importする。内部観測不明は制約として保持する。

```bash
python3 evals/cloud_receipt.py restore rounds/explain-398-concise-flow-008/snapshot .local/round008-live
python3 evals/cloud_receipt.py quality-import .local/round008-live \
  .local/round008-live/attempts/CASE--candidate--1 \
  rounds/explain-398-concise-flow-008/inputs/CASE--candidate--1/input.json \
  RESULT QUALITY_POST_JSON PARENT_COMPLETION_DIRECTORY rounds/explain-398-concise-flow-008/quality-protocol.json
```

静的QA: 固定harnessコードはd59af57…とbyte一致。007とのprompt/fixture/観測expectation/metric/
response_reporting一致、source-basis引用だけの差分、2packetのhashと固定case対応を検証。
実candidateのsnapshot restoreと2stage smoke、rubric非混入、操作一覧要求の非追加、公開scan/diff check成功。
これらは準備機構の確認であり、実LLM応答の品質評価ではない。
