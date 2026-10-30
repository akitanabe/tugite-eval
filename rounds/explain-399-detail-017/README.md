# #399 Round017 — unchanged fixed pair

016/015/014の中立prompt・fixture・全観測・metrics・reporting・必須構造gateを保持する。
corpus.jsonとresolved-corpus.jsonは016とbyte一致。既存source引用は新候補にも存在するため変更不要。
候補SHA/treeとpacket identityのみ更新する。旧出力に合わせた基準変更はしない。

親報告では016は構造/事実PASS、semantic style FAIL。旧結果/判断を保全し、この準備では実出力を読まず再採点しない。
既存[詳細選択基準](../explain-399-detail-014/README.md)と[意味表現の適用説明](../explain-399-detail-016/README.md)を引き続き用いる。

candidate各1packet、同じ2caseだけ。親がfresh taskを起動する。準備側は静的restore/stage確認のみで、LLM実行・採点を行わない。
