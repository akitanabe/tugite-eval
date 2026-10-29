# 実装先頭の短い説明: 2 sample handoff

事前freeze後、final candidate `ed8857da509f84235cdba3d2032440dd041d27a1`を接続済み。
通知されたtree `4c4ab23f0a18171ea5098c96180bb000109d3996`も一致。
[実行用2件のpath/hash](INPUTS.md)、[index](index.json)、[source identity](PROVENANCE.json)を使用する。新しい[形式要件](../../cases/explain-398-implementation-first/README.md)と
[corpus](../../cases/explain-398-implementation-first/corpus.json)を事前固定し、旧004/005は保持する。
[登録](preregistration.json)に固定candidate SHAを記録した。古い候補SHAや拒否された方針で代替しない。

実在する実装識別子を先に、処理と接続を短く説明する。長い抜粋や逐語講義は必須ではない。
重要な条件/状態/作用/順序/失敗境界を保持し、実装要素を長い一行chainに詰めない。
コード抜粋は必要時の補助として許す。固定行数・template・fence数で判定しない。

最終SHA受領後、既存adapterだけで正確に2packetを生成する。

```bash
python3 evals/prepare_398.py candidate <FINAL_CANDIDATE_SHA> .local/explain-398-implementation-samples \
  --corpus cases/explain-398-implementation-first/corpus.json \
  --case explain-398-session-flow --case explain-398-infrastructure
```

placeholder/枝名では実行しない。candidate sourceは引用・配布identity確認に限る。
inputs/index/snapshot/quality-protocolを新delivery commitへ保全し、2件のpath/hashを親へ返す。
旧roundの入力や結果は新適合の根拠にしない。

親は新delivery SHAのfresh eval taskへ各packetを1つずつ渡し、固定Skill→fixture作業→collect --qualityを使う。
要求設定はgpt-6.1-sol / medium。control/rubric/旧出力を被評価taskへ読ませない。
評価準備taskは実taskを起動・採点しない。内部証跡や実効model不明は制約として保持する。

**親が2件の実際の応答をHumanへ提示して停止。全件展開・追加case・反復・version更新・PRは禁止。**

事前固定corpus SHA-256: `d6abc2ef60985f61c5f37e4c3c7c10842334f766ac6fec6120b7cf4d8d965d15`。

## 生成済み2packetの実task用prompt

`<DELIVERY_SHA>`は本inputsを含む最終remote main完全SHA、`<INPUT_PATH>`/`<INPUT_SHA256>`はINPUTS.mdから選ぶ。
1taskに1packet、fresh eval環境、requested gpt-6.1-sol / medium。control/rubricや旧出力は対象taskへ渡さない。

```text
Repo=https://github.com/akitanabe/tugite-eval.git、cwd=/workspace/tugite-eval、固定code/data SHA=<DELIVERY_SHA>。
なければ通常clone。既存ならtop-level/originを確認。逐次成功確認してgit fetch --no-tags <URL> <DELIVERY_SHA>、git cat-file -e <DELIVERY_SHA>^{commit}、git status --porcelain（空）、git checkout --detach <DELIVERY_SHA>、git rev-parse HEAD（一致）。失敗/dirty/別repoなら保持して停止。force/reset/clean禁止。
python3 evals/cloud_task.py stage <INPUT_PATH> <INPUT_SHA256> /workspace/quality-stage
固定SHAの通常fetchを許可。/workspace/quality-stage/prompt.txtを読み、指定された固定Skillを最初に読み、指定fixtureで作業する。現行Skill/corpus/control/snapshot/rubric/他版/旧出力は読まない。採点/nested CLI/push/依存導入/fixtureからの外部通信は禁止。
完全応答を/workspace/quality-response.txtへ保存し、repo cwdで:
python3 evals/cloud_task.py collect /workspace/quality-stage <INPUT_SHA256> /workspace/quality-response.txt /workspace/quality-result --quality
応答本文、成果物所在、result-seal hash、読んだ固定参照、制約を返す。内部証跡/実効model未観測は不明のまま。拒否時は操作/対象/理由/完了部分/denied-pending-uncertainを正確に返して停止し、迂回しない。
```

親は2件の実際の応答をHumanへ提示し、進め方の判断を待つ。これ以降の展開/反復/version/PRは行わない。

準備QA: 新corpus検査4件成功。fixture/promptと技術的期待を旧005から保持し、旧抜粋必須条件を除去。
事前freezeからcorpus byte不変、candidate SHA/tree/Skill引用と配布identity、2packetのhashとcandidate/trial1、
rubric非混入、snapshot restoreと実candidateでの2stage smokeを確認。旧004/005/resultsは変更なし。
公開scanとdiff check成功。これらは準備機構の証拠であり、Skillの実出力品質や内部遵守の保証ではない。
