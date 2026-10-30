# #399 Round015 — fixed detail-selection criteria

Round014の基準を変更せず、候補だけを更新する。fixture・中立prompt・全観測・metrics・reporting・必須構造gateは完全に同じ。
corpus.jsonとresolved-corpus.jsonは014とbyte一致する。既存source引用が新候補にも存在することを確認したため、引用自体の更新も不要。

親報告では014は構造/事実に合格し、詳細削減は部分達成。元の結果/判断は保持し、この準備で再採点しない。
[014の基準根拠](../explain-399-detail-014/README.md)を引き続き適用する。
本文と経路の重複・周辺詳細を避けるが、重要条件/作用・commit/Cookie境界・利用者帰属・実責務の忠実性を保持する。
短さや固定layoutだけを品質の代替にしない。

candidate各1packetの2件のみ。実LLM実行は親がfresh taskで行い、この準備では静的restore/stage確認だけを行う。
追加caseや全suiteは起動しない。全履歴を保全する。
