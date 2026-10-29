# 短い実装先頭の処理フロー

同じ合成fixtureのsession-flowとinfrastructureだけを対象とする。処理の流れと、その中で各関数/classが何をしているかを主眼に、実装識別子を先に短く処理をつなぎ、
コードに沿う正確さと重要な接続を保って、Humanが流れを追いやすい説明を評価する。
コード内部の説明を主目的にせず、単に逐語説明を短くした回答や、網羅的な関数役割catalogにも置き換えない。
旧006からの要件変更は[監査](AUDIT.md)に記録した。旧応答を模範解答へ変換したり、受理済み例文を暗記させたりしない。

全体像の独立した導入章、逐語的内部講義、網羅的なguard/例外/制約一覧、全ファイル/commands一覧は達成条件にしない。
実装名だけの孤立一覧や意味工程先頭の説明でも代替しない。短い各項目に必要な接続・状態・順序の補足を含めればよい。
抜粋は必要時の補助。固定の語数・行数・template・fence数・唯一の並びや文言は要求しない。

正確さを弱めない。交換の検証、code消費/session登録とtx確定、Cookie発行の前後、認証userとcartの接続は重要。
基盤対象では配線・振分け・認証の介在・handler受渡し・確定/復元の境界が重要。
細部を全て語る必要はないが、語った内容に重要な誤りがあったり、断定の範囲が実装を越えたりした場合はaccuracyの問題として残す。
[事実参照](REFERENCE.md)はjudgeが誤説明を点検する資料であり、回答へ全項目を転記させるchecklistではない。

fixture bytes・対象case・working changesは旧006と同じ。promptはフローと各関数/classの役割を尋ねる中立な依頼へ変更し、回答形式のtemplateや受理例文は含めない。
`response_reporting=task-response-only`はharnessの操作一覧要求だけを外し、code調査や証拠回収を制限しない。
新基準で旧結果を遡及採点しない。公開するのは合成fixtureと要件/監査要約だけで、非公開会話全文やログを追加しない。

事前固定時点では最終candidate SHAは未提供だった。親から新SHAを受領するまで候補packet・snapshotを固定しなかった。
実行は親によるcandidate2件各1回だけ。実際の応答をHumanへ提示し、判断を待って停止する。
全件展開・追加case・反復・version更新・PRは行わない。Tugite本体を変更しない。

prompt・response reporting・rubricも旧006と異なるため、このsampleからSkill変更単独の効果を切り分けて主張しない。
中立promptへの改訂は親の明示指示に基づき、candidate SHA通知後・source/outputを読む前に行った。意味の中心基準は先行commitで固定済み。

独立開発reviewを優先する親の指示により、暫定6b3f4ac…のcandidate packet固定は停止中。
実施済みはsource identity/引用確認だけ。新candidate packet・snapshot・LLM評価は未作成。レビュー後final SHAを待つ。

待機履歴の後、親がf69dcced…の固定と2packet作成を明示したため、新007へ接続した。
corpusのprompt/期待/fixture/metricは変更していない。実際の固定identityは007のPROVENANCE.jsonに記録する。
