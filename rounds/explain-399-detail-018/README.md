# #399 Round018 — fixed pair for minimal finishing candidate

017の中立prompt・fixture・全観測・metrics・reporting・必須構造gateを変更しない。
corpus.jsonとresolved-corpus.jsonは017とbyte一致。既存source引用は新候補にも存在するため変更不要。
候補SHA/treeと必要なpacket identityのみ更新する。

親報告ではUserは017を肯定し、図と本文の重複を軽く整理する仕上げを承認した。
これは準備のprovenanceであり、新しい判定基準や合格判定ではない。旧結果/判断を保全し、ここで再採点しない。
既存[詳細選択基準](../explain-399-detail-014/README.md)と[意味表現の適用説明](../explain-399-detail-016/README.md)を維持する。

同じ2case candidate各1packetだけを固定。親がfresh taskを起動する。
準備側は静的restore/stage確認のみで、LLM実行・採点・version/PR操作を行わない。
