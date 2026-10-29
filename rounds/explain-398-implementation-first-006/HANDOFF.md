# 実装先頭の短い説明: 2 sample handoff

最終candidate SHA待ち。新しい[形式要件](../../cases/explain-398-implementation-first/README.md)と
[corpus](../../cases/explain-398-implementation-first/corpus.json)を事前固定し、旧004/005は保持する。
[登録](preregistration.json)のcandidate_shaは未確定。古い候補SHAや拒否された方針で代替しない。

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
