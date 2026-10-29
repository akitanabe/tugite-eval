# #398 事前固定の評価根拠

仕様根拠は [Tugite #398](https://github.com/akitanabe/tugite/issues/398) の本文
（2026-10-29確認、コメント0件）と、baseline `c44261f1f70da40c75123a91153a8aa6c6d4be1e` の
`shared/skill/explain-this/SKILL.md` および配布版。GitHub mainも同SHA、VERSIONは7.5.1と確認した。
候補output・候補diffを見る前に、この文書、corpus、fixtureを固定する。候補SHAは未提供。
実在WebView・業務コード・私的データは使わない。合成fixtureの学習用の意味を評価し、実アプリ互換性は主張しない。

| ケース | 独立した問い | 必要な観測・コード根拠 |
|---|---|---|
| session-flow | 機能の意味と実装の対応 | operation.prepareでchallenge状態生成→issueで親条件確認とcode登録。Controller.exchange→SessionOperation.exchange→store.registerで一つの交換処理を実現。exchange一関数内にも状態取得/拒否判断/保守/消費/登録/確定という複数の意味単位がある。 |
| infrastructure | 同じ基盤を主題にすると省略方針を切替できるか | app.buildの配線、Dispatcher.dispatchのroute選択、SessionAuth.callがcartだけに介在しコピーrequest.userを渡す、403変換と想定外例外の伝播、MemoryStore.transactionの確定/復元を中心にする。 |
| unknown-connection | 未提供依存と接続を捏造しないか | provider_adapter未提供。exchange_ticket呼出し→戻り値→Cookie発行、cartのuser引渡しは既知。永続化/tx/検証/再利用防止/失敗作用は不明。ROUTESだけではCookie認証→request.user接続を証明できない。 |

機能ケースの重要な境界は以下。要求するのは意味の保持で、全行の逐語説明ではない。

| 条件 | 静的に導かれる結果 |
|---|---|
| 成功 | parent/codeを取得、親存在・期限（expires<=nowは拒否）・refresh_active、code存在・親対応・未使用、binding一致を確認。期限切れsessionを削除してcode消費/session登録を同じtx内で実施。正常context exit後にControllerがCookieを発行する。 |
| 各拒否 | purge/registerより前にRejected。maps変更とCookie発行は起きない。Dispatcherが403へ変換する。 |
| commit失敗 | transactionがparent/code/session mapsを復元。期限切れsession削除も復元。id serial増分は戻らない。ControllerのCookie発行へ進まずRuntimeErrorは伝播。 |
| Cookie発行失敗 | txは既に確定、codeは使用済み、sessionは残る。Cookie listは未追加、RuntimeErrorは伝播。 |
| code再利用 | usedで拒否。二重session/Cookie発行はない。 |
| cart | session Cookie→期限確認→session.userをコピーrequestへ渡す→そのuserのcart取得。未認証/期限切れは403。元request.userを信頼しない。 |

prepare/issueは外側callerが直接呼ぶ学習用API。binding Cookie設定とWebView搬送の実装は提供しない。
lock_*は辞書lookupであり実DBロックではない。txもsingle-threaded memory modelで、実DBの隔離水準・
並列競合・本番セキュリティを評価しない。一般DB INSERT/UPDATE/DELETEの内部解説は必要ない。
Dispatcherは機能ケースでも403変換が意味に効くため残すが、単なる辞書lookup等の詳細列挙を要求しない。
基盤ケースではDispatcher自体が主題なので説明対象になる。

版別適合と共通品質を分ける。baselineには旧版の「全体像・処理の流れ・概念からコードへの対応・根拠と限界」を適用。
candidate-only `398-process-and-effects` はIssue改善方針1〜4、`398-no-name-exclusion` は方針4と基盤対象の受入条件、
`398-preserve-gap` は方針2と未確認内容を補わない受入条件に対応する。corpusのissue_basisにも記録した。
各basisの共通source引用はaccuracy/事実区別の根拠に限る。新規粒度方針の根拠はIssue本文であり、
候補source引用の存在確認は候補SHA到着後のprovenance追加として行う。出力に合わせた期待値改変はしない。
意図的な粒度変更そのものを旧版のregressionとは呼ばない。

共通品質はtraceability/usefulness/accuracy/conciseness-without-loss。重要な作用をDB/Cookie等の固定キーワードで
検出せず、対象・作用・実装・条件と失敗境界の意味を独立judgeが判断する。異なる妥当な段落/図/表/見出しを許す。
短さ/行数だけを品質としない。意図適合や本番での安全性を断定しない。内部操作・実効モデルは未観測なら不明。

既存explain-this正常/境界/欠落依存/意図未共有の4回帰ケースはcorpus.jsonから入力・prompt・期待観測を保持し、
candidateの適用版だけを変更した。shipping fixtureの要求と実装の意味を変更していない。

scope提案: 初回は重点3cases×baseline/candidate各1回＋回帰4cases×candidate1回＝10試行。
機能ケースを最優先に、差が受入判断に重要な重点ケースは両版各3回へ拡張する。
同じ3casesすべてを拡張しても最大22試行。単回は探索的な出力評価に留め、方向付き比較は既存compareの
両版3回・独立judge要件を守る。#397全83件の再実行は責務がexplain-thisに限定される今回の変更には不要。
