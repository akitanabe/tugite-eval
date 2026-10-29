# Public synthetic nonnormal corpus: preparation only

公開済み `evals/corpus.json` の境界/失敗/曖昧24ケースを変更せず抽出した。
48版別セルのうち43を既存runner/adapterでtrial 1としてexportし、5セルをnot-supportedでblockedにした。
新しいfixture・prompt・期待値・機能を追加せず、評価結果に合わせた修正もしていない。
実評価の起動、私的ログや会話のexportは行っていない。host準備telemetryはpublic metadataから省いた。

- Round: `70b5ac7c-b596-4452-ad8a-8fedb5d262f3`
- Eval code: `19f0126119a59c93ea5acf2eac31bbf603f99cab`
- Requested: `gpt-6.1-sol / medium`
- [Path/hash/case/version/status一覧](INPUTS.md)、[機械可読index](index.json)、[適用不可理由](BLOCKED.md)
- [元public定義とSHA](provenance.json)、[同じ品質基準をこのroundへ適用するprotocol](quality-protocol.json)

renderer/reviewerが不在だというプロンプトはtool制御ではない。既存fresh cloud adapterがその不在を実際に強制できない5セルは、
`visualize-that-failure` の3版、`review-propose-failure`、`impl-review-failure`。
制約を無視してexportしたり、実行前からSkill失敗扱いにしたりしない。これらにinput/control/attemptは作っていない。
他の失敗ケースは公開fixtureにあるmissing runner、未提供source、未決仕様等を保持したもの。
実際の環境で必要な実行権限がなければ、既存品質protocolどおりblockedとして扱う。

## 実行時の取得（親が起動する場合）

新規taskで通常clone/fetchし、URL/origin/cwd/cleanと各操作の成功を確認する。
codeを19f0126に固定したまま、単一inputだけをこのdata commitから取得できる。
`<DATA_SHA>` は最終handoffの完全SHA、`<INPUT_PATH>` / `<INPUT_SHA256>` はindexから対応する値を使う。

```bash
git fetch --no-tags https://github.com/akitanabe/tugite-eval.git <DATA_SHA>
git cat-file -e 19f0126119a59c93ea5acf2eac31bbf603f99cab^{commit}
git checkout --detach 19f0126119a59c93ea5acf2eac31bbf603f99cab
git rev-parse HEAD
# 上記成功・HEAD一致を確認してから入力を取得する。
git show <DATA_SHA>:<INPUT_PATH> > /workspace/trial-input.json
python3 evals/cloud_task.py stage /workspace/trial-input.json <INPUT_SHA256> /workspace/quality-stage
```

続いてstaged promptに従い固定Skill/fixtureを使い、同じinput SHAで `collect --quality` する。
corpus/control/snapshotや他版結果は評価agentへ渡さない。HTML内のexample.invalid文字列を実通信しない。
code SHAとinput data SHAを親の記録で区別する。親はこの新roundのquality-protocol.jsonをquality-importへ渡す。
この追加のcheckoutを親receiverに用いる場合、既存code bytesは19f0126と同一である。

## Receiver復元

```bash
python3 evals/cloud_receipt.py restore rounds/cloud-nonnormal-003/snapshot .local/quality-nonnormal
```

その後、既存quality-importにROUND/ATTEMPT/INPUT/RESULT/親完了記録を渡す。
固定inputと実出力の対応・独立品質判断は保持し、完全transcriptや実効モデルunknownを品質比較の前提にしない。
内部権限・隠れた操作等の不可観測項目はindeterminate、品質PASSとは別扱い。
既存正常round、source corpus、旧protocol、公開resultsはこの追加で変更しない。
