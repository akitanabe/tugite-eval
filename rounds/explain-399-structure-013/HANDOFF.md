# Round013 — corrected structural criterion, candidate2 inputs

[修正理由と判定](README.md)、[preregistration](preregistration.json)、[corpus](corpus.json)。
Candidate `3e9a42e29be0f0f81efad0ea1ef86d6c18615cba`、tree `ffe0aaa31b9a0364fdb90ee16f025ab58bab3298`。
[2件のpath/hash](INPUTS.md)、[index](index.json)、[provenance](PROVENANCE.json)。実LLM評価は未実施。012のfixture/中立prompt/reportingを保持したまま、
表示されたフロー自体が追跡可能である正の構造観測を追加した。事実忠実性とは別に判定する。

source引用を最終SHAで解決後、既存helperでseparated/mixedを各1packetだけ生成する。
新候補outputを見て基準を合わせない。旧012を含め全履歴/元judgmentを保存する。
親報告の012 PASS撤回は本登録へ追記した歴史状態であり、新しい実行結果ではない。

独立judgeにはcalibration.jsonを事前校正用として渡せる。順序・接続が別topicに散在するfragmentsは事実Passでも構造Fail、
structured separated/mixedは構造Passとなる境界を確認する。これはexchange sliceの合成校正で全caseの唯一解ではない。
被評価taskにはcorpus/rubric/calibration/Reference/旧結果を渡さず、元の中立promptだけを維持する。

新rubricはrequired_quality_observationsで構造観測を必須にする。
judgeのoutput_quality.result=passは、displayed-execution-structure=passのときだけ記録できる。
accuracy Passや他metricで構造Failを相殺しない。構造評価の意味判断は独立judgeがcodeと表示を読む責務である。
実LLM task起動は親だけ。2case各1回、追加case/説明専用agent/全suite/version/PRは追加しない。

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
現行Skill/corpus/control/snapshot/rubric/calibration/REFERENCE/他版/旧応答は読まない。採点/nested CLI/push/依存導入/fixtureからの外部通信をしない。
/workspace/quality-response.txtには依頼への説明本文だけを保存する。操作ファイル/commandsや環境報告を追記しない。理解を左右する未確認箇所は本文の該当箇所で短く示す。実行上の拒否/失敗は本文と別に正確に報告する。
repo cwdで:
python3 evals/cloud_task.py collect /workspace/quality-stage <INPUT_SHA256> /workspace/quality-response.txt /workspace/quality-result --quality
最終返却は説明本文、result directory、result-seal.jsonのSHA-256。内部証跡/実効modelが未観測なら不明のまま。
拒否時は操作/対象/理由/完了部分/denied-pending-uncertainを正確に返して停止し、迂回しない。
```



calibration/本rubric/Referenceはjudgeだけの資料で、被評価taskへ渡さない。本文は元の中立依頼への応答だけ。
親が2fresh task各1回を起動し、独立judgeは事実忠実性と表示構造を別に評価する。
構造Fail/不明を総合PASSに相殺しない。校正例はexchange sliceだけで、全caseの唯一解ではない。

準備QA: 新構造/gate検査3件、runner17件、receipt24件成功。
prereg9355075…からcase基準は不変（source引用だけ解決）、012の中立prompt/fixture/reporting/事実基準を保持。
2packet candidate/trial1とgate情報のjudge側限定、snapshot restore、固定case照合、2stage smoke、公開scan/diff check成功。
校正例は実応答ではなくjudge用synthetic slice。自然文を自動採点した証拠ではない。構造の意味判定はjudgeが担う。
