# コード中心の説明: prospective準備

新candidate SHA未提供。これは実行用packetを生成する前の意味固定であり、trial起動・採点は行っていない。
[要求変更と適用基準](../../cases/explain-398-code-centered/README.md)、[固定corpus](../../cases/explain-398-code-centered/corpus.json)、
[機械可読登録](preregistration.json)を参照。

意味固定commitは `294297430cb4ce0a965bbe23b5cde23f21998054`、引数解説の範囲補足commitは
`715fff40a05fa4ee772031528d42eea0df48d197`。
最終corpus SHA-256は `52c45cba589780225cf41add220893285c6c54619a8d9670fe79d679dc06aed1`。
候補出力を見ず、最新ユーザー発言を根拠に固定した。
旧candidate `2e7ae9237103cc9a6c6d9afbb748c11ad2ea51e7` の14件は旧基準でPASSだが期待差あり、という
親の報告を記録した。旧応答/採点を本taskで検証したとの主張はしない。旧round/results/rubricは変更しない。旧14件を新基準適合の根拠にしない。
受領した`34afef723211ae48a8447917bc18bf835b40e69f`は親が明示した非final版なので、fetch・freeze・試行に使わない。

新しい目的は、実装していないHumanがコードから処理の接続を読み順に追えること。
意味ある処理の実コード抜粋と短い補足を使い、入力値→判断/変更→次へ渡す値/呼出先をつなぐ。
孤立した断片列挙・位置名一覧・長い散文だけ・全呼出しdumpを代替としない。
出典と省略を明示し、合成コードを実在と偽らない。値の解説は内部処理理解に必要な範囲だけ。
引数一覧/型/デフォルト値の網羅やfence数・行数・説明量で加点しない。
追加の粒度優先順位も固定した。明白な引数/単純代入の逐語説明より、コードをまたぐ接続、重要な分岐・状態変化・順序へ
説明量を集中し、一行ずつ日本語へ翻訳しない。原文末尾の未完「コ」は補完しない。

## candidate SHA到着後

比較baselineは旧candidate `2e7ae923…` を提案する。直前の出力形式からの改善を比較でき、
旧#398達成基準を維持したまま新candidateに新形式の義務を適用できるため。
新形式はbaselineの遡及的仕様違反とは扱わない。

次の`<NEW_CANDIDATE_SHA>`だけを親から受領した完全SHAに置換する。枝名や仮文字列では動かない。
既存`prepare_398.py`への最小拡張（corpus/baseline選択）で、追加frameworkは使わない。
旧引数の既定値は保持する。

```bash
python3 evals/prepare_398.py both <NEW_CANDIDATE_SHA> .local/explain-398-code-centered \
  --corpus cases/explain-398-code-centered/corpus.json \
  --baseline-sha 2e7ae9237103cc9a6c6d9afbb748c11ad2ea51e7 --focus-trials 3
```

新candidate sourceは適用根拠と配布identityだけ確認する。期待観測をsourceや出力に合わせて変えない。
共通source引用がなくなった場合は、期待値を変えず新sourceのprovenanceとの対応を点検し、理由を残す。
生成先にinputs/index/snapshot/quality-protocolができるのでhashを照合し、新delivery commitへ保全する。
旧004のpacketを新005の入力として再利用しない。fixtureとpromptのbytesは同じでも版とrubricのidentityは異なる。

最初は新final candidateのsession-flow 1件だけを起動し、親が実際のコード中心出力を確認する。
その後、必要なcandidate回帰4cases、他の重点case、重要差の両版反復へ順次展開する。
22packetの事前生成は実行義務ではない。従来の初回10件一括展開を既定としない。
単回は記述的な独立品質評価に留め、方向付き比較は既存compareの両版3回要件を守る。

親は新しいdelivery SHA/input path/hashで [既存stage→固定Skill→collect --quality手順](../explain-398-004/HANDOFF.md)を使う。
実taskはfresh eval環境、gpt-6.1-sol / medium。control/rubric/旧出力を評価対象へ読ませない。
親が完了を観測してquality-importし、別contextのjudgeが新roundの適用rubricと共通品質を評価する。
quality-post-templateのprotocol hashも新生成物へ合わせる。完全内部証跡や実効モデル不明は制約として保持する。
version更新とPRは保留。

## 準備QA

fixture/prompt/working changes/既存期待観測/旧metricの意味の保持を機械比較した。
新観測は7casesのcandidateだけに適用し、重点3casesの新共通品質は記述的比較と明記した。
独立読み取り専用reviewで、コード接続中心・未提供依存の限界・固定文言oracle禁止・旧結果保持を点検した。
reviewで見つかったzipによる旧観測欠落の見逃しは、旧id/expectation列の完全比較で修正した。

- 新prospective corpus検査3件成功、既存準備・fixture検査6件成功。
- 新corpusと指定baselineを使うCLI smokeでfreeze/prepare/export/snapshot成功（LLM実行なし）。
- git diff --check成功。旧004/旧cases/results/Tugitecoreは保持。

未確認: 新candidateの固定SHA、配布source引用とidentity、両版packet、実出力品質。
