# Round022 — same Skill, audience sentence only

Candidate `3b51aea9116417018ad23366cb4e109e1233adac`, tree `fa269b9d06cd43a8cce871c1f187748a1873a78d`。
[3input path/hash](INPUTS.md)、[唯一の依頼差分](README.md)、[比較用雛形](comparison-plan.json)。
親が同じnormal / unknown-connection / infrastructure各1fresh taskをgpt-6.1-sol / mediumで起動する。
Skill・fixture・評価基準は021と同じ。task promptへ指定の一文だけを追加した実験。

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






## 同じ判定と表現変化の観測

親がtask ID、input/source/eval SHA、requested/resolved/effective設定と出典、response/result sealを保持する。
独立judgeは021と同一rubricで構造・事実・意味・粒度を評価する。両必須観測のPASSを総合quality PASSの条件として維持する。
新しい年齢別合格基準、語句禁止、比喩指定、コード禁止、短文化制約などを加えない。
judge-only calibrationは021と同じ。被評価taskにはrubric/calibration/旧応答を渡さない。

021と022の同じ3caseの実応答を別の比較artifactへpath/hash付きで対応づけ、どの表現や説明がどう変わったかを記録する。
旧判断を書き換えない。旧応答が未取得なら比較を未完了とし、synthetic応答で埋めない。
出力差を安定した年齢指定の因果効果やモデル優越として断定しない。単回の同一条件実験として観測限界を残す。
失敗を隠した再試行や全6件への展開はしない。Tugite本体/version/PR操作なし。

準備QA: corpus/resolved-corpusの差は各prompt末尾の指定一文だけ。3packetを021と比較し、差がprompt/round_id/attempt_idのみであることを検証（DELTA.json）。
Skill配布物・agent設定・fixture・モデル要求・reporting等は同一。各rubricとcalibrationはbyte一致。
remote restore、3packet照合・stage、意味/構造gate計6回帰checks、公開scan/diff check成功。実LLM実行・比較採点なし。
