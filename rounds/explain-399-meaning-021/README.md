# #399 Round021 — unchanged semantic criteria

同じ3件normal / unknown-connection / infrastructureを各1回、新候補で確認する準備。
corpus.jsonとjudge-only calibration.jsonは020とbyte一致。fixture、依頼、既存観測、metrics、reporting、
構造とgrounded-processing-meaningの両必須gateをそのまま保持する。
旧応答に合わせた基準緩和、新しい語句禁止、固定模範文、追加case/反復を導入しない。

親報告では020は構造・事実全件PASS。意味はnormal PASS/改善、unknown-connection FAIL、
infrastructure PASSだが改善小。この報告は履歴のprovenanceで、準備workerが実応答を読んだり再採点したものではない。
020・019の元入力/応答/判定を保持する。同じ基準で新候補と020の実応答を比較し、旧判定は書き換えない。

新候補SHA待ち。実行可能packetやsnapshotを作らず、3ケースの意味とjudge資料だけを固定する。
候補受領後はsource引用・候補identity・必要なpacket identityだけを更新する。
本文/diagramが機能上の役割・達成内容を伝えるか、不明な役割や保証を創作していないかを独立に判定する。
[020の判定根拠](../explain-399-meaning-020/README.md)を引き続き適用し、語句や操作名の使用そのものを禁止しない。

モデル要求gpt-6.1-sol / medium、各1fresh taskを親が起動する。全6件の再実行は行わない。
Tugite本体・version・PR操作なし。実LLM評価はこの準備で起動しない。
