# #399 remaining coverage — Round019

2026-10-31、Userが現在の仕上がりを概ね承認し、残りevalの実行を依頼したとの親の明示指示に基づく。
2代表ケースのみという以前の制限はこの残り評価について解除された。候補は018と同じ完全SHAに固定する。

## 残りの特定

既存#398計画の候補回帰集合は重点3件＋shipping4件。#399ではsession-flowに相当する機能評価を
separated/mixedの2形態へ置換し、018の両ケースは実行済みとの親報告を受領した。この2件は再実行しない。
そのため残りは以下6件、candidate各1回。旧候補での実行は現候補の完了とは数えない。
#397全32case/他Skill/全旧比較セルは今回のexplain-this修正の残りに含めない。

| New case | 入力の出典 | 確認範囲 |
|---|---|---|
| explain-399-infrastructure | cases/explain-398/corpus.json のinfrastructure | 基盤自体が対象の配線・認証・例外・状態確定の主要経路/意味 |
| explain-399-unknown-connection | 同unknown-connection | 既知の部分経路と未提供adapter/認証接続の境界 |
| explain-this-normal | 既存shipping正常 | 検査・通常額・速達加算の意味と経路 |
| explain-this-boundary | 既存shipping境界 | テストなしで境界の意味をコードから説明 |
| explain-this-failure | 既存shipping欠落依存 | 外部処理を創作せず既知分岐/委譲と未知を示す |
| explain-this-ambiguous | 既存shipping意図未共有 | 実装説明を先に行い、Human意図への適合を断定しない |

fixture/prompt/overrideは元corpusのbytesを再利用。webviewは018 separatedとも同一。
正常fixtureにあるrequirements/plan/testsはそれぞれ資料であり、説明依頼が変更authorityを与えるわけではない。
欠落依存variantの古いrequirements/testsを実装済みの外部挙動と取り違えない。
意図未共有variantも提供requirementsを無視させるものではなく、未共有のHuman固有意図を創作しないという観測。

## 現行基準への適用

旧#398の観測/metricsは機械コピーしない。現行#399の意味/実経路/重要条件・副作用/根拠と限界と、
013の正の構造観測・必須gate、014の詳細選択、016の意味表現の既存適用を用いる。
shipping4件の責務観測は元の意味を保持し、共通品質は現行018の5metricsと既存authority-and-scopeを適用する。
基盤/未知接続の観測は#399へ適用根拠を置換し、旧serial欠番説明必須等の周辺detail checklistを継承しない。
固定短文/identifier-first-only/長いコード抜粋/基盤除外/全内部列挙は求めない。

必須displayed-execution-structureは、単一関数では主要な内部経路、欠落依存では既知部分と明示したgapを評価する。
未提供内部の完全経路や架空の認証接続を要求しない。構造FAIL/不明を事実PASSで相殺して総合PASSにはできない。
意味/重要な条件/作用が保たれるかと、経路の見やすさ/説明重複は独立に読む。

新roundの観測は新しい対象範囲へ適用する事前登録であり、旧失敗や018判断を再解釈するものではない。
被評価promptにrubric/校正例/fixture解答を注入しない。task-response-onlyで運用証跡を本文へ混ぜず別管理する。

## 実行と分類

fresh trialの作成APIはこのworkerのtool一覧で見つからない。既存docsのnested CLI経路には既知の
sandbox/socket/proxy拒否履歴があるため、その経路で代用/再試行しない。親が6fresh taskを起動するhandoffを作る。
各試行は明示的gpt-6.1-sol / medium、実効値不明はunknownのまま。モデル代替をしない。

状態は準備済み/未実行。後続で結果を保存する際は、候補内容の問題、基準/入力の不整合、運用・環境失敗を分ける。
失敗を都合よく取り直さず、元結果を保持し、復旧が必要なら理由/元attemptを結び付けた別記録とする。
各1回は現在候補の回帰スモークであり統計比較や版差の因果推論ではない。
全歴史を保持し、Tugite本体変更/version/PR/merge/releaseは行わない。
