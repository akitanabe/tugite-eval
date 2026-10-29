# Pilot handoff (parent only)

新規 `tugite-eval-container` taskを親が作成し、要求モデルを `gpt-6.1-sol`、effortを `medium` とする。
再開・forkは使わない。親はpush後に返された完全Git SHAへeval checkoutを固定する。
この文書とcontrol.jsonは被評価taskの入力に含めず、下記promptだけを渡す。

- Case: `test-report-normal`, version `v7.3.7`, trial `1`
- Fixed Tugite source: `886e919a16ff6d318ed824ab53e8335362261c95`
- Input: `pilots/cloud-pilot-001/input.json`
- Input SHA-256: `0b1dad5135deeaef23222f25cfe05b0e200c451dde13d529768861401efa2aab`
- Attempt ID: `6adb2451-e816-4dbc-b1a6-d6f0d1644d5a`
- Round ID: `5c45690f-6565-4b3a-baa9-511d3e3fee88`
- 親専用適用rubric/元round identity: `control.json`
- このroundはfresh cloud transport用の新round。旧nested CLI roundの実行済み扱いにはしない。

## 被評価taskへ渡すprompt

以下はeval repositoryを親が指定revisionに固定済みで、taskのcwdがそのrepositoryの場合の完全prompt。
bootstrapは固定Skillを読む前に現行Tugite Skillを読み込まない。

```text
この新規taskで、指定済み固定入力の1試行だけを実行してください。最初に
python3 evals/cloud_task.py stage pilots/cloud-pilot-001/input.json 0b1dad5135deeaef23222f25cfe05b0e200c451dde13d529768861401efa2aab /workspace/pilot-stage
を実行してください。input/control/corpusや他版結果を手動で読まず、続いて /workspace/pilot-stage/prompt.txt を読み、その指示に従って固定版Skillを読み、/workspace/pilot-stage/workspace で作業してください。現行版Skillへの切替、nested Codex CLI、採点、外部通信・push・依存導入は行わないでください。stageに必要な固定SHA取得は許可されています。taskの完全な応答を /workspace/pilot-response.txt に保存してから
python3 evals/cloud_task.py collect /workspace/pilot-stage 0b1dad5135deeaef23222f25cfe05b0e200c451dde13d529768861401efa2aab /workspace/pilot-response.txt /workspace/pilot-result
を実行してください。最終返却は応答本文、result directory、result-seal.jsonのSHA-256、input SHA、実際に読んだ固定Skill/参照、使用コマンド、観測できた制約を含めてください。不明なモデル実効値・費用・子agent設定を推測しないでください。失敗や拒否時は同じ操作を繰り返さず、正確な対象・操作・理由・完了済み部分・結果状態を返してください。
```

## 親の回収・判定

[cloud adapter運用](../../evals/cloud-tasks.md) の手順でtask ID / raw transcriptと出力を対応させ、hashを確認する。
返却は `response.txt`, `collection.json`, `after.json`, `artifacts/`, `result-seal.json` と、stageの `before.json`。
タスク側からこのdev workspaceへのパスが見えるとは仮定しない。必要なbytesは親runtimeの正規回収機能で取得する。
回収機能がなければ正確な不足を記録し、部分出力を完了証拠にしない。
controlのrubricを別判定contextで採点し、各判定にraw transcript / response / diffの証拠を紐づける。
request/resolved/effective/unknown、実際のロード、子agentの観測と不明を分ける。
現adapterの出力は未検証の輸送証拠であり、既存runnerのLLM集計には自動投入しない。
単一pilotからregressionやモデル優劣の結論を作らない。
