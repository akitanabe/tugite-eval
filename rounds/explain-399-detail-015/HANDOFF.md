# Round015 — detail selection, exactly two candidate packets

Candidate `cce79cc73f96d616ffaf1044216fb5d746432e2d`, tree `3d0e727bb08a4e229e72ae434923366c9babee34`。
[入力path/hash](INPUTS.md)、[基準変更](README.md)、[provenance](PROVENANCE.json)。
構造gate・全観測・metrics・fixture・中立prompt・reportingは014から変更なし。
独立judgeは構造と内容/粒度を別々に評価し、周辺詳細の省略だけを不正確と扱わない。
校正は013/calibration.jsonを参照できるがexchange sliceであり完全回答例ではない。被評価taskには渡さない。
実LLM実行は親だけ、candidate各1回。

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




準備QA: corpus/resolved-corpusが014とbyte一致。新候補SHA/treeと既存source引用、snapshotのremote復元、2packet固定attempt照合、2stage smoke、構造gate3回帰checks、公開範囲scan/diff check成功。
runner/transportコード変更なし。実LLM実行・出力採点なし。
