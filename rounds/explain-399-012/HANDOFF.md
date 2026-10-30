# #399 candidate2 packet handoff

Candidate `4f57597a4eb758cd963c2de194a63ddaca224ff0`、tree `540abdd27a1d1e29993aa17e560caf1ca5696262`。
[2件のpath/hash](INPUTS.md)、[index](index.json)、[provenance](PROVENANCE.json)。実LLM試行・採点は未実施。
[新基準と再利用監査](../../cases/explain-399/README.md)、[事前corpus](../../cases/explain-399/corpus.json)。
新source引用だけを補った[resolved corpus](resolved-corpus.json)で固定した。事前のprompt/fixture/期待/metricは保持。

#399は#398基準を置換する。全体の意味フロー、実際の入口から連続するコード実行フロー、意味/条件/作用を評価する。
分離/混在双方で忠実な責務境界を保持し、inline処理を架空serviceへ置き換えない。基盤を機械除去せず、汎用機構の講義へ広げない。
旧brevity/identifier-first-only/導入禁止/omit-frameworkやReference文面一致を採点に使わない。
輸送のtask-response-onlyは操作一覧を本文へ混ぜないためで、全体像や必要な条件/経路を削る指示ではない。

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


Human向け本文と輸送証拠を分ける。新sourceの固定Skillを読み、#399による説明を返す。
case promptは機能説明の中立依頼のみで、解答例・Reference Output・rubricを含めない。
親が2fresh taskを各1回起動し、必要な独立judgeに#399基準と実codeを渡して品質を判断する。
全結果を保持。全suite/旧candidate再利用/追加の説明agent/version/PRを自動追加しない。
旧入力・基準・結果を保持し、旧失敗を合格へ読み替えず、新旧基準差をSkillだけの因果効果やmodel優越としない。

## 再利用と置換

再利用: SHA transport、stage/collect --quality、配布物/agent定義全体、分離Session fixture。
追加: Controller内に交換処理が混在する最小fixture。
置換: #398の出力選択/粒度方針をすべて#399の目的・原則・出力要件・受入条件に置換。
新候補はmainから別dev taskで構築された親指定SHA。旧398candidateは使わない。

準備QA: 新3検査（fixture分離/混在の成功・拒否・commit失敗・再利用拒否・認証・Cookie失敗境界を含む）成功。
事前登録60786573…からprompt/fixture/期待/metricは不変、source basisだけを解決したことを照合。
2packet candidate/trial1、frozen case対応、snapshot restore、2stage smoke、評価基準非混入、公開scan/diff check成功。
旧round/resultsは変更なし。これは準備検証であり、実LLMの品質評価ではない。
