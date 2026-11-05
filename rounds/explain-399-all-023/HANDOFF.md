# Round023 — all11 prepared #399 scenarios

Fixed Tugite candidate `5cc3e4cefe0d8c9a8b746c86f74cde30a9b732f7`, tree `9bf27e5d683c5d9fd161f029a28849a69fd3ef89`。
[11input path/hash](INPUTS.md)、[対象集合/現行基準](README.md)、[開始前の実行状態](STATUS.json)。
親からcanonical8件の直接fresh task起動報告を受領（DIRECT_TASKS.json）。この8件を重複起動しない。
以下のsealed bootstrapは将来必要なときの準備資料で、実際の直接taskがこのpacketを使用した証拠ではない。
11個のprepared入力中、読者指定3件は今回の8件バッチ外として保留。明示gpt-6.1-sol / medium、モデル代替なし。
nested Codex CLIの既知初期化問題と同じ経路を再試行しない。

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







## 親の回収と実説明品質の独立判定

各taskのcase/trial/task ID、input/eval/source SHA、requested/resolved/effective modelと出典、完了状態、response path/hashとresult sealを保存する。
完全内部証跡/実効model不明はunknownで保持し、出力品質判断を止めない。実行失敗をSkill内容FAILやPASSに置換しない。
独立judgeへcontrol/rubricとsealed response/fixtureを渡す。被評価taskへrubric/校正/過去応答を渡さない。
構造・意味・正確性を独立に読み、形式だけ合っていても実説明が操作の逐語訳/全関数一覧なら意味達成としない。

現行観測:
- 全体説明→参照用の主要コード実行経路→意味上の処理単位ごとの詳細説明という順序。
- 意味単位とコード根拠の対応。関数/class境界や図のnodeごとに機械分割しない。自然に一致する境界や短いfixtureは許す。
- 実際の接続/帰属/順序/復帰後の継続、重要条件・副作用・確定/失敗境界を保持。
- 未提供依存や接続は既知の役割と不明部分を分け、架空の業務意図/保証/内部経路を創作しない。
- 周辺detailや本文の手順再列挙で本筋を埋めず、短さ/語句/heading一致だけで採点しない。

総合quality PASSにはdisplayed-execution-structure、grounded-processing-meaning、ordered-semantic-detailがすべてPASSである必要がある。
意味が伝わる図の注釈だけでもよいという旧受入句は今回の詳細順序要件を上書きしない。旧semantic校正のsliceを完全回答として使わない。
15歳指定3件は元の一文以外に追加指示/新基準を入れず、同じ基準で出力を読む。

結果をSTATUSのcase対応に紐付けた別artifactで記録し、現在の8件バッチの完了/失敗/未実行と、別枠保留の読者指定3件を分ける。実応答の所在、各quality判断と証拠、制約を集計する。
候補内容の問題、基準/入力の不整合、環境/運用失敗を分類する。失敗を隠す取り直しをせず、復旧が必要なら元attempt/理由/安全性確認を残す。
旧結果を書き換えず、今回候補で未実行のcaseを過去PASSで埋めない。version/PR/merge/release操作なし。

直接taskの条件照合では、実際に読んだ固定Skill/fixture/override、元依頼、モデル指定、実行・変更・通信の観測を親の証拠から確認する。
prepared packet/input-sealを直接taskが使ったかのように遡及して付けない。parent-direct evidenceとして品質を判定し、sealed transportの未確認部分を明記する。
