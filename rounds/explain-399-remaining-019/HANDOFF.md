# Round019 — remaining six candidate trials

Candidate `4ffee85221ea0ff175be6a3b86a3de1bde9f47bb`, tree `4955bfb2d7bb786096612bb0d7793051f32b7f43`。
[6入力path/hash](INPUTS.md)、[scope/適用根拠](README.md)、[preregistration](preregistration.json)。
018 separated/mixedは親報告で実行済みとして除外。残り6case各1fresh task、要求gpt-6.1-sol / medium。
モデルを代替しない。自律fresh-task作成APIは未提供なので親が起動する。nested CLIへ切り替えない。

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





## 親の回収・判定

各taskのID、requested/resolved/effective設定と出典、input hash、固定eval/source SHA、result seal hash、完了状態を保持する。
既存collect --qualityとquality-importを再利用できる。完全内部証跡や実効modelが不明でも出力品質判断を止めず、不明を明記する。
独立judgeはcontrol/rubricとsealed response/fixtureを読み、構造と意味・正確性・粒度・権限を別々に観測する。
観測はpass/fail/indeterminateと理由/証拠。総合output_quality PASSにはrequired displayed-execution-structure PASSが必須。
単一関数には適切な簡潔構造を許し、欠落依存は既知の部分経路＋明示gapを評価する。未知の内部の列挙は要求しない。
013の構造calibrationは判断境界の参考sliceであり、Session以外の正解templateではない。

候補内容の問題、評価入力/基準の不整合、実行環境/運用上の失敗を分類する。
失敗試行を隠した取り直しはしない。実行失敗は元attemptを保持し、安全な復旧の根拠と関連IDを記録してから別attemptを扱う。
自動反復は事前登録していない。欠損/運用失敗は候補の内容FAILと混同せず、6件の未完了を全PASSとしない。
旧398の形式制約で落とさず、018や旧判断を書き換えない。version/PR/merge/release操作なし。
