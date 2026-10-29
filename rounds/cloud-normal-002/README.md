# Normal-case cloud round 002 (parent only)

標準の実行・独立品質比較は [QUALITY_HANDOFF.md](QUALITY_HANDOFF.md) を参照する。
以下の二段階receipt手順は任意のstrict監査経路として保持する。
fixture/rubric/input identityは両経路で同じ。

既存corpusの正常ケースを変更せず抽出した8ケース・16版別セル。継続4 Skillは3版、追加4 Skillはv7.5.0のみ。
[index.json](index.json) がcase、版、固定source SHA、input SHA、attempt identity、必要能力の一覧。
各セルtrial 1をprepared状態で保存した。3初期試行方針は維持し、trial 2/3は親がpilot2確認後に別attemptとして準備する。
このroundでの実LLM試行は未実行。機構テストの出力をここへ投入していない。

- Round ID: `e7da77d4-bb42-4965-a8a0-6945b5c62f61`
- Pilot2: `test-report-normal / v7.3.7 / trial 1`
- Input: `rounds/cloud-normal-002/inputs/test-report-normal--v7.3.7--1/input.json`
- Input SHA-256: `a47763ea50c0a7dad7ce6d80314287a06b2ea08b47ef5d5b73abd0798de81183`
- Attempt: `81625202-efb8-4336-a65d-99784d72d70a`
- Requested baseline: `gpt-6.1-sol / medium`; resolved/effectiveは実測がなければunknown。
- 変更理由・元corpus hash: [change.json](change.json)

[setup prompt](SETUP_PROMPT.txt) の `<EVAL_CODE_SHA>` に親が最終handoffの完全Git SHAを入れる。
setup後の生出力と能力の証拠を親が独立取得し、[親receipt手順](../../evals/parent-receipts.md) で子の書込範囲外へ保存する。
readyにならなければblocked。readyなreceiptのSHAと実行前before/prompt hashを [run prompt](RUN_PROMPT.txt) へ入れ、同一taskの次turnに渡す。
別case/版/試行には新規taskを使う。通常fetch/cwd/HEAD確認はsetup promptに含まれ、古いmount snapshotでもfetchから始める。

親が記録する最低情報:

- 実際のtask ID、setup/run turn ID、parent observer ID、eval code SHA、input/attempt/round identity。
- 実行前stage receipt原文、その取得出典と証拠hash、before/prompt/adapter/runner hash、必要能力の実測。
- 実行前に親が保存したpre receipt SHAと、その後run許可に渡した同じ値。
- result sealと全artifact hash、親runtime証拠のpath/hash、完了/input/provenance/完全transcriptの各観測。
- requested / resolved / effective / unknownの区別、子agent/ロード/cost等の出典またはnull。
- 別contextの独立judge ID、全適用rubric/共通metricごとの判定・理由・sealed evidence参照。

親のcapabilities/post記入templateはこのdirectoryにある。観測不足のままtrueや実効値を補完しない。
これらのtemplateやcontrol/snapshotは評価agentへ渡さない。

```bash
python3 evals/cloud_receipt.py restore rounds/cloud-normal-002/snapshot .local/cloud-normal-002
# 例: pilot2の受領後。PARENT_PRE/POST/RUNTIMEは親の実物証拠を保存した場所
python3 evals/cloud_receipt.py import .local/cloud-normal-002 \
  .local/cloud-normal-002/attempts/test-report-normal--v7.3.7--1 \
  rounds/cloud-normal-002/inputs/test-report-normal--v7.3.7--1/input.json \
  RESULT PARENT_PRE POST_JSON PARENT_RUNTIME_DIRECTORY
```

続いて既存runnerのjudge-template → 別context独立judge → adjudicate → reportを使用する。
部分transcriptはevidence-incompleteとなり、比較の完了試行に数えない。
pre receiptのない初回pilotは別のreferenceとして保持し、このroundへ移さない。
論理的なinput/control分離はtool隔離ではなく、実際のretrieval・権限・通信の限界を親が記録する。
