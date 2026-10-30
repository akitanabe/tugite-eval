# #399 output detail selection preregistration

Round013の表示実行フローはUserが受け入れ、続いて詳細の取捨選択の改善を求めた。
親が提案した、図と本文の重複・周辺詳細を減らすoutput-only改善への続行許可を根拠に、候補SHA到着前に登録する。
旧roundの評価を変更せず、新しい実出力も読んでいない。

## 既存基準の評価と最小変更

Round013は既に全call・全guard・全例外の網羅や一般機構の講義を要求していない。
このため観測の追加/削除や合格gateの変更は不要。既存`meaningful-granularity` metricだけに、
表示経路の各手順を本文で繰り返す必要はなく、補足は意味・重要条件/作用/境界など理解を増す情報へ使う、と明記する。
周辺field、serial欠番、主経路に関係しないrouteエラー等は出力必須でなく、省略だけで不正確と扱わない。
ただし、実際に述べる事実の正確性は引き続き評価する。

code再利用の拒否、commit後のCookie発行という確定境界、認証した利用者のcartへの帰属、
分離/混在実装の実在責務は保持する。これらの重要性を周辺詳細削減で相殺しない。
観測文中の内部処理への言及は実経路の帰属を評価するためのもので、各内部値や手順の独立した解説を
全て出力するchecklistではない。重要な条件/副作用は経路に統合して説明してよく、別段落での重複を求めない。

## 固定するもの

2つのfixture、中立の被評価prompt、reporting、全4観測とその適用根拠、
`required_quality_observations=[displayed-execution-structure]`をRound013から変更しない。
表示経路自体の主要順序・必要な入れ子/帰属・復帰後の応答までの連続性を要求するgateは維持する。
固定語数/行数、特定layout、#398のidentifier-only規則は追加しない。
親は構造と内容/粒度を独立に判断し、短さのみを改善と判定しない。

Round013の校正例と構造gate回帰testは引き続き有効だが、校正sliceは完全な回答例ではない。
被評価promptには本rubricや校正例を追加しない。

## 待機

新候補SHAは未接続。packet/snapshotのfreezeやLLM実行はしていない。
候補受領後、同じ2case candidate各1packetのみ作り、親がfresh taskを起動する。
全履歴・Round013の判断は保持し、追加caseや全suiteへ展開しない。
