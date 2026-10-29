# Parent receipts and existing reports

親がsetupと実行を別turnにし、評価作業開始前にbaselineを保存する。collectorの成功、子の自己申告、
要求モデル値だけでtrusted completedを成立させない。receiptは親の証拠付き申告であり、runtime署名ではない。
このプロトコルは親が指定した出典区分の真偽や「全transcript」の完全性をAPIで認証しない。
親は実際に取得したruntime出力と独立取得bytesに基づいて記入し、取得できない項目はnullのままにする。

## 1. Setup → 親保存 → run

親はsetup-only promptでcheckout URL、完全eval code SHA、cwdを指定し、逐次fail-stopでcheckoutとstageを行わせる。
stage後は評価Skill/promptを読まず停止する。親は実際のtask ID、setup turn ID、stage stdout receiptとその取得証拠、
必要能力の実測を子の書込範囲外に保存する。source区分は次の意味を持つ。

- `parent-runtime`: 親がruntimeから実際に得たtool/event出力。子の要約・自己申告をこの区分へ置き換えない。
- `parent-artifact-inspection`: 親が評価開始前に実物bytesを独立取得・照合したsetup証拠。
- `child-self-report` / unknown: 観測不足。receiptはblockedになり、runを許可しない。

```bash
python3 evals/cloud_receipt.py receive-stage INPUT parent-stage.json setup-evidence.txt capabilities.json PARENT_PRE \
  --task-id ACTUAL_TASK_ID --setup-turn-id ACTUAL_SETUP_TURN_ID --parent-id PARENT_OBSERVER_ID \
  --eval-code-sha EXACT_EVAL_CODE_SHA --observation-source parent-runtime
```

入力はv2で、input SHA、attempt/round ID、adapter/runner code hash、before/prompt hashを照合する。
`capabilities.json` は capability名ごとの `{"available": true|false|null, "evidence": "観測箇所"}`。
必須能力がfalse/null/観測なしならblocked。`receipt.json` がreadyの場合だけ、そのSHAを記録してrun promptを送る。
必須能力はfixture読取、shell、Git。実装/修復/HTML保存にはfixture書込、test-verifyにはPython実行も必要。
child agentsやrendererは利用可能性を別途記録する。Skillが条件付きで必要とする能力が実際に利用できなければ、
その時点でblockedとし、架空の子agentや描画証拠で代替しない。visualize-thatで仕様が許すrender-unverifiedはそのまま区別する。

親のrun promptにはtask ID、setup turn ID、eval code SHA、input SHA、before SHA、prompt SHA、親receipt SHAを含める。
子は各identityを確認してから固定prompt/Skillを読み、fixtureで実行し、親保持before hashを渡してcollectする。
要求モデルは `gpt-6.1-sol / medium`。setup/runの実効値が取れない場合は不明とする。
再開は同一新規task内のsetup→runのためにだけ使用し、別case/versionには新しいtaskを使う。

## 2. 親のpost receipt

親がresult bytesとtask ID / run turn ID / 応答を対応付け、`result-seal.json` の全hashとartifact inventoryを確認する。
`post.json` は [template](../rounds/cloud-normal-002/post-template.json) を用い、観測ごとにparent-held runtimeファイルへの参照を付ける。
`runtime_files` は別directoryに保存したruntime証拠の相対path→SHA-256。hash対象以外のファイルもある場合はimportを拒否する。

- `agent_turn_completed`: 実際のagent応答を持つ完了turnを親runtimeで観測したか。
- `input_identity_verified`: 指定task/turn、code、input、固定prompt、配布物が実行に対応するか。
- `artifact_provenance_verified`: 回収したresponse/artifactsがそのtaskの出力であることを親が確認したか。
- `transcript_complete`: setupからrun/collectまで、tool使用と子agentを含む生のruntime証拠を完全取得したか。

true/falseの観測は実在する親runtime証拠への参照を必須にする。不明はnull。
最終messageを取得しただけではtranscript_completeをtrueにしない。
`telemetry` のresolved/effective、loaded distribution、spawned children、usage/costは、実際のruntime出典がなければnull。
要求値、ファイルに置いたmodel overlay、agentの自己申告は実効値の出典にならない。
`synthetic` は実際の試行か機構test doubleかを親が明示する。機構テストは実LLM試行に数えない。
必要能力の不足は `capability_blockers` に正確な理由を残す。

## 3. Import → 独立裁定 → report

consumerのcheckoutが異なる場合も、Git保存したsnapshotからroundを復元できる。
snapshotはspec/rubricとprepared入力metadataを保存し、元producerのworkspaceやGit履歴を含まない。
配布物は復元時に別の一時source repositoryへ固定SHAでfetchする。frozen runnerと一致するeval code revisionで実行する。

```bash
python3 evals/cloud_receipt.py restore rounds/cloud-normal-002/snapshot .local/cloud-normal-002
python3 evals/cloud_receipt.py import ROUND ATTEMPT INPUT RESULT PARENT_PRE POST_JSON PARENT_RUNTIME_DIRECTORY
python3 evals/runner.py judge-template ROUND ATTEMPT judgment.json
# 別contextの独立judgeが適用rubricとsealed evidenceを読み、理由と証拠を記入
python3 evals/runner.py adjudicate ROUND ATTEMPT judgment.json
python3 evals/runner.py report ROUND
```

importは期待inputをfrozen spec/attemptと照合する。親pre/postはchild result directory外から渡す。
postは親pre receipt hash、task/input/code、異なるsetup/run turn ID、result seal、runtime証拠hashに一致する必要がある。
result内before/promptは親が実行前に保持したhashと一致する必要がある。独立judgeのIDに実行task IDは使えない。
独立性はID/宣言だけで完全には証明できず、親が実際に別contextを使う責任を持つ。

`state=completed` はreadyなpre receipt、parent-runtimeによる完了/input/provenanceの観測、完全transcript、
設定/配布物の非改変、blockerなし、synthetic=falseが全て揃った場合だけ成立する。
完了応答と出所を観測したがtranscript不足なら `evidence_kind=llm, state=evidence-incomplete`。
この場合も直接観測できた項目の独立裁定を保持できるが、reportの完了試行・比較母集団には数えない。
子の自己申告だけなら `cloud-reference`、必要能力不足なら `blocked`。
実効モデル等の不足はnullを保持し、judgeが当該判定をindeterminateにする。
3初期試行・独立裁定・比較証拠が揃うまで版別/版間結論はindeterminateのまま。

importは既存executionを上書きしない。裁定も既存runnerの上書き禁止を維持する。
修正・新たな入力・仕様変更は旧roundを保持して新roundにする。

## 初回pilotの扱い

`cloud-pilot-001` はpre receiptのない旧protocolの参考観測として別保存し、v2 importerでは受け入れない。
親から報告された応答/静的観測の評価は [reference note](../pilots/cloud-pilot-001/REFERENCE.md) に出典と限界を記録する。
このdev taskでは初回pilotの実物bytesを取得していないので、hash再検証や独立採点を行ったとは主張しない。
