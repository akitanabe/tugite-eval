# Round011: meaning/purpose clarification — candidate2 packets

[監査と変更理由](AUDIT.md)、[corpus](corpus.json)、[登録](preregistration.json)を参照。
prompt・fixture・reportingは007〜010と同じ。最新の明示要件により期待の中心を、処理単位の意味・機能上の目的へ明確化した。
戻り値/受渡し/fields/statusは、流れの理解に不可欠な場合だけ補足する。各節点の既定項目にしない。
コードに根拠を持つ機能上の寄与と、共有されていない歴史的設計意図を区別し、捏造しない。

候補`3fc608131926491866503c154e176b67e60a3890`、tree`7bd1415cd0cee0ea9a6ecbdecba854b85bb51a77`を接続済み。
[2件のpath/hash](INPUTS.md)、[index](index.json)、[provenance](PROVENANCE.json)を使用する。source引用は候補にも存在し、事前固定corpusはbyte不変。
候補受領後の既存adapter手順:

```bash
python3 evals/prepare_398.py candidate <NEXT_CANDIDATE_SHA> .local/explain-398-round011 \
  --corpus rounds/explain-398-role-meaning-011/corpus.json \
  --case explain-398-session-flow --case explain-398-infrastructure
```

実LLM評価は親が起動する。caseは2件各1回だけ。全attemptと全出力を保持し、都合のよいsampleだけを選ばない。
役割・意味を基準に親が品質を判断し、必要なら次候補の同じ2caseへ進む。全suite/追加case/version/PRは行わない。
旧結果を新基準への適合根拠にせず、要件明確化を含む比較をSkill単独の因果効果としない。

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


Human向けには説明本文だけを提示し、輸送/実行証拠は別に保持する。task-response-only reportingを維持。

criteriaは010から明示要件で変更したため、旧結果の新基準への合格読み替えやSkill単独の因果主張はしない。

準備QA: 新3静的検査成功。事前commit f6fe8bb…からcorpus byte不変、元の中立prompt/fixture/reporting一致、
2packet candidate/trial1と評価基準非混入を確認。実候補でsnapshot restore、固定case対応、2stage smoke、
公開scan/diff check成功。これらは準備機構の確認であり、LLMの実応答評価ではない。
