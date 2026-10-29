# コード要素中心の説明: 少数sampleの準備

final candidate `56ac61bb4cc83236ecf3a233131aa8def75ab0f6`を事前freeze後に接続済み。trial起動・採点は親が行う。
通知されたtree `d90a8ea982dc94c0ccb1bd7515363f876a030cd3`との一致も確認した。
[実行用3packetのpath/hash](INPUTS.md)と[index](index.json)、[source identity](PROVENANCE.json)を使用する。
[要求変更と適用基準](../../cases/explain-398-code-centered/README.md)、[固定corpus](../../cases/explain-398-code-centered/corpus.json)、
[登録](preregistration.json)を参照する。

corpus SHA-256: `afd9416583a6a1c0fe771917dc95ba8e6cf7c0b27e011dc3aa59a5a0f5ea250d`。
先行freezeは29429743…、範囲補足715fff40…、粒度補足eefb7278…。今回、最新の骨格指示を追加の仕様明確化として固定する。
旧candidate2e7ae923の14件PASSは親の歴史的報告であり、新適合の根拠にしない。旧応答を読んだり遡及採点したりしない。
旧round/results/rubricを保持。34afef723…は非finalのため未使用。

## 最新の骨格と評価基準

実在する関数/class/構造体等を流れの骨格にし、実コード抜粋で呼出し・処理順・データ受渡しをつなぎ、内部処理を短く補足する。
コードを概念工程へ過剰再編しない。位置名/全関数/import一覧や全コードdumpを代替としない。
説明は見れば分かる引数・型・単純代入の翻訳へ割かず、重要な接続・分岐・状態・副作用・順序へ集中する。
共通基盤が挙動に効く場合、または基盤自体が対象の場合は必要なコードを残す。

最新ユーザー指示を元Issueの「主要単位は意味処理」より優先した。
旧`398-process-and-effects`はbaseline限定にし、新candidateでは`398-code-structure-and-effects`に置き換え、
Controller.exchange→SessionOperation.exchange→MemoryStoreの実構造を軸にtx/拒否/副作用/失敗境界を維持する。
7casesの`code-centered-explanation`も実コード要素中心へ明確化した。元Issueと新指示の矛盾を同時に課さない。
抜粋の固定集合・行数・fence数・引数解説量をoracleにしない。未提供接続/依存を合成しない。
原文末尾の未完「コ」は補完しない。

## 親が候補SHAを受領した後

代表的なcandidate2〜3casesだけを準備する。session-flowとinfrastructureを基本とし、必要ならunknown-connectionを加える。
次のコマンドの`<FINAL_CANDIDATE_SHA>`を親からの完全SHAへ置換する。仮文字列/枝名は実行できない。
3件目不要なら最後の`--case`を外す。旧corpusと旧helper既定値は保持し、明示case選択だけを追加した。

```bash
python3 evals/prepare_398.py candidate <FINAL_CANDIDATE_SHA> .local/explain-398-code-samples \
  --corpus cases/explain-398-code-centered/corpus.json \
  --case explain-398-session-flow --case explain-398-infrastructure --case explain-398-unknown-connection
```

candidate sourceは適用引用・配布identityの確認に限る。期待をsource/outputに合わせて変えない。
生成先のinputs/index/snapshot/quality-protocolを新delivery commitへ保全し、input path/hashを親へ返す。
旧004 packetは新005へ流用しない。最初にsession-flow1件を親が起動し、その後も合計2〜3件の範囲で扱う。
親は新しいdelivery SHAとinput path/hashで [stage→固定Skill→collect --quality](../explain-398-004/HANDOFF.md) の機構部分を再利用する。
旧handoffの10件/22件展開や比較計画は適用しない。

fresh eval環境、requested gpt-6.1-sol / medium。control/rubric/旧出力を被評価taskへ読ませない。
親が完了を観測し、必要な独立judgeによる新基準の品質観測を付け、実際の応答をHumanへ提示して判断を待つ。
旧14件PASSで新適合を代替しない。内部証跡/実効モデル不明は制約として保持する。

**ここで停止。全件展開・回帰の自動追加・追加反復・version7.5.2更新・PR作成は禁止。Humanの判断を待つ。**

## 準備QA

fixture/prompt/working changes/旧metricと旧結果を保持。矛盾する骨格条件だけ適用版を明示して置換した。
新corpus検査は旧観測列を丸ごと比較し、意図した置換以外の欠落を検出する。
新case選択で少数だけ生成でき、未知/適用外caseや未確定SHAでは書込み前に停止する。
独立読み取り専用reviewを行い、LLM trial/output採点はしない。
配布identity/source引用と3packetは照合済み。未確認は実出力品質。

## 生成済みpacketでの実task bootstrap

`<DELIVERY_SHA>`はこのinputsを含む最終remote main完全SHA、`<INPUT_PATH>`/`<INPUT_SHA256>`はINPUTS.mdから選ぶ。
1taskに1packet、requested gpt-6.1-sol / medium、fresh eval環境。control/rubric/旧出力を評価対象へ渡さない。

```text
Repo=https://github.com/akitanabe/tugite-eval.git、cwd=/workspace/tugite-eval、固定code/data SHA=<DELIVERY_SHA>。
なければ通常clone。既存ならtop-level/originを確認。逐次成功確認してfetch --no-tags <URL> <DELIVERY_SHA>、cat-file -e <DELIVERY_SHA>^{commit}、status --porcelain（空）、checkout --detach <DELIVERY_SHA>、rev-parse HEAD（一致）。失敗/dirty/別repoなら保持し停止。force/reset/clean禁止。
python3 evals/cloud_task.py stage <INPUT_PATH> <INPUT_SHA256> /workspace/quality-stage
固定SHAの通常fetchを許可。/workspace/quality-stage/prompt.txtを読み、指定固定Skillを最初に読み、指定fixtureで説明する。現行Skill/corpus/control/snapshot/rubric/他版/旧出力は読まない。採点/nested CLI/push/依存導入/fixtureからの外部通信は禁止。
完全応答を/workspace/quality-response.txtへ保存し、repo cwdで:
python3 evals/cloud_task.py collect /workspace/quality-stage <INPUT_SHA256> /workspace/quality-response.txt /workspace/quality-result --quality
応答本文、成果物所在、result-seal hash、読んだ固定参照、制約を返す。内部証跡/実効model未観測は不明のまま。失敗時は操作/対象/理由/完了部分/denied-pending-uncertainを返す。
```

親は3caseの実際の応答をHumanへ提示し、判断を待つ。これ以降の展開/反復/version/PRは禁止。

検証結果: 新corpus検査3件・準備/fixture検査7件成功、独立レビューでも同検査成功。
実final candidateでsnapshot restoreと3packet stage smokeが成功。全packetはcandidate/trial1で評価基準非混入、
session-flow rubricには旧骨格条件がなく新構造観測が適用されることを確認。公開scan/diff check成功。
これらは準備機構の確認であり、被評価Skillの実応答や内部遵守を評価した証拠ではない。
