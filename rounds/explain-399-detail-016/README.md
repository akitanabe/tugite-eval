# #399 Round016 — same criteria, semantic prose refinement

最新User指摘は冗長さの削減と、コード式の逐語転記でなく理解できる意味での説明。
既存semantic-understanding、meaningful-granularity、grounded-accuracyで評価可能なため、新観測/metric/gateを追加しない。
同じfixtures・中立prompt・reporting・全観測・metrics・必須構造gateを保持する。corpusは015とbyte一致。

judgeは式をそのまま述べたかだけでなく、処理の意味が読者に伝わるかを見る。根拠のない単位・基準時刻の断定は
従来どおり正確性の問題として扱う。単位が不明なら、無理に単位を補わず確認可能な意味の範囲で説明できる。
特定の式・定数・言い換えを合格条件や模範回答にせず、コード識別子/式の必要な引用自体を禁止しない。
重要条件・状態・副作用・確定境界と、表示経路の忠実性を維持する。短さや語数では判定しない。
これは既存基準の適用説明であり、旧判断の再採点や意味要件の追加ではない。

全履歴を保全する。実LLM実行は親のみ、同じ2case candidate各1packet。追加case/全suiteなし。
