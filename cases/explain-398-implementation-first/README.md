# #398 実装識別子を先にする説明

このroundでは、実在する関数・class・構造体等の識別子を先に示し、何をするかを短く補足しながら、実際の処理順と接続を追えることを評価する。
旧005の「まとまった実コード抜粋を主とする」基準からの、新しく確認された期待の変更である。
長い抜粋を添えるだけで達成とはせず、長い抜粋自体を必須ともしない。意味工程を先に作って実装を後置する説明へ戻さない。

合成fixtureでは、例えばSessionOperation.prepareのchallenge生成からSessionOperation.issueのcode発行へ、
Controller.exchangeの呼出しからSessionOperation.exchangeの検証・消費・登録確定へ、
Cookies.sessionの確定後Cookie発行記録へと、実装名と短い処理説明を読み順につなげられる。
この例は固定の行数・template・抜粋集合・唯一の構成を要求しない。複数classを一行の長いchainへ詰めず、短い別行/段落に分ける。

重要な条件・状態変化・副作用・順序・失敗境界は残す。引数・型・単純代入の網羅説明や逐語的な内部講義へ情報を割かない。
コード抜粋は必要時の補助として許す。実装名だけの孤立一覧、全関数/import一覧、全コードdumpも代替としない。
基盤が挙動に効く場合と基盤自体が説明対象の場合の扱いは維持する。

## 事前固定と適用

[corpus.json](corpus.json) は旧004/005から合成webview fixtureと、session-flow/infrastructureのpromptをbyte保持して再利用する。
技術的な期待（コード消費/session登録の確定後Cookie発行、拒否時effects不発、失敗境界、middleware接続など）も維持する。
説明形式は新しいcandidate-only観測`implementation-first-explanation`と共通品質軸`implementation-first-readability`へ置き換える。
旧005の長い実コード抜粋を必須とする観測は持ち込まない。sourceの共通accuracy引用は事実区別の根拠に限り、
新形式の根拠はこの事前固定した要件である。候補SHA到着後のsource確認は適用根拠・配布identityだけとし、出力へ期待を合わせない。

旧004/005の入力・rubric・結果は保持し、新要件達成の根拠にしない。本準備では旧応答/採点を読まない。
公開するのは合成fixtureと要件の要約であり、非公開会話の全文や実行ログを追加しない。
以前拒否された方針や操作は実行せず、今回の確定要件だけを扱う。

## 実行範囲

candidateのsession-flowとinfrastructureを各1回、計2件のみ。最終candidate SHAは親から受領する。
親が実taskを起動し、実際の応答をHumanへ提示して判断を待つ。自動的な全件展開・追加case・反復・version更新・PRは行わない。
Tugite本体は変更しない。本taskは評価入力準備とQAに限り、応答生成・採点を行わない。
