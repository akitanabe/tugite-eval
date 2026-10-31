# Round020 — grounded processing meaning, exactly three fresh tasks

Candidate `2085c0cfd43d3c65ddeced1e0cca5879b7c3c78a`, tree `8f78e6a3785af53bbaf7443b24a4243ea0a44eea`。
[入力path/hash](INPUTS.md)、[基準変更](README.md)、[比較記録の雛形](comparison-plan.json)。
同じnormal / unknown-connection / infrastructure各1回。親がgpt-6.1-sol / mediumでfresh taskを起動する。
旧019の全6件やbaselineの再実行は追加しない。実効設定不明はunknown。

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





## 独立判定と実応答比較

親がinput/source/eval SHA、task ID、result sealと完了本文、requested/resolved/effective設定を保持する。
judgeにはcontrol/rubricとsealed response/codeを渡す。calibration.jsonは別の合成コードのjudge-only境界例で、LLM応答や唯一解ではない。
被評価taskへrubric/校正例/旧応答を渡さない。独立judgeは意味・構造・正確性を別々に判定し、理由と証拠を記録する。
総合quality PASSにはdisplayed-execution-structureとgrounded-processing-meaningの両方PASSが必要。
事実PASSや経路表示PASSで主要説明の逐語訳を相殺しない。根拠のない目的や保証を足して意味を作らない。
既知範囲で役割が伝わるかを評価し、未知内部の説明を強制しない。図に意味を統合してよく、本文の重複や全末端の役割行は不要。

親の持つ019の同じ3caseの実応答と新応答を並べ、comparison-plan.jsonに対応する別の結果artifactへ
各responseのpath/hash、元判断、新しい意味観測での読解、重要な改善/残存問題を記録する。
旧019判断はそのまま保持し、新しい基準のPASSだったと書き換えない。旧応答が欠ければ比較は未完了とする。
語句一致や禁止語の件数で採点せず、役割・達成内容と根拠を読んで判断する。モデル/Skillの因果的優越は主張しない。
実行失敗・基準不整合・候補内容の問題を区別し、失敗を隠した取り直しはしない。
