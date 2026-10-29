# 評価結果（2026-10-29）

## 結論

今回の固定コーパスでは、**83件の評価結果が出力・成果物の品質PASS**でした。v7.5.0への重大な出力品質低下は観測していません。これは小さな合成fixtureに対する結果であり、実案件全般の品質同等性、統計的有意性、モデルや版変更の因果的優劣を保証しません。

評価の主軸は、利用者の判断に基づく「クオリティが維持されているか」です。完全な内部操作証跡は必須としていません。観測できない内部手順・実効モデル・完全隔離などは不明／判定不能のまま保持しています。

## 実行・判定数

| 区分 | 範囲 | 品質判定 |
|---|---|---|
| 継続4 Skill・正常ケース | 3版 × 各3回 = 36試行 | 36 PASS |
| 新規4 Skill・正常ケース | v7.5.0 × 各1回 = 4試行 | 4 PASS |
| 境界・失敗・曖昧ケース | 実行可能な43セル × 各1回 | 43 PASS |
| 能力不在を強制できないケース | 5セル | 未実行／非対応。Skill失敗ではない |

失敗ケースのPASSには、存在しない必須コマンドを勝手に置き換えずに停止する、要求・対象・因果関係が未決なら確認を求める、といった適切な停止・限定報告を含みます。対象ソフトウェアやテストの実行成功を一律に意味しません。

最後のimpl-review曖昧ケースは、元の試行が保存中に中断され、再開時にはローカル成果物が失われていました。利用者が別途許可した新しい試行を評価しています。元の中断試行は判定不能として別記録に残し、二重計上・事後的な検証済み扱いはしていません。初期のbootstrap pilotも比較母集団から除外しています。

## 正常ケースの詳細

| Skill | 試行数 | 記録 |
|---|---:|---|
| test-report | 9 | [応答・独立判定・比較](cloud-normal-002/test-report-normal.json) |
| test-verify | 9 | [生成テスト・独立検証・比較](cloud-normal-002/test-verify-normal.json) |
| impl-lead | 9 | [文書変更・独立判定・比較](cloud-normal-002/impl-lead-normal.json) |
| visualize-that | 9 | [HTML・描画制約・独立判定](cloud-normal-002/visualize-that-normal.json) |
| explain-this / review-propose / impl-plan / impl-review | 各1 | [新規Skillの達成評価](cloud-normal-002/new-skill-attainment.json) |

test-reportではv7.3.7の対応関係中心の報告と、v7.4.0以降の根拠付き診断という意図的な責務変更を分離しました。test-verifyはテストメソッド数ではなく、要求への対応と具体的な不具合の識別能力を確認しました。

## 境界・失敗・曖昧ケースの詳細

- [impl-lead](cloud-nonnormal-003/impl-lead.json)
- [test-report](cloud-nonnormal-003/test-report.json)
- [test-verify](cloud-nonnormal-003/test-verify.json)
- [visualize-that](cloud-nonnormal-003/visualize-that.json)
- [explain-this](cloud-nonnormal-003/explain-this.json)
- [review-propose](cloud-nonnormal-003/review-propose.json)
- [impl-plan](cloud-nonnormal-003/impl-plan.json)
- [impl-review・中断／新規試行の区別](cloud-nonnormal-003/impl-review.json)

これらは各セル1回の探索的評価です。反復した正常ケースと同じ強さで一般化しません。重大な品質低下を疑う結果がなかったため、追加試行やデグレIssueの起票は行っていません。

## 品質PASSと別に残した問題・限界

- visualize-thatのv7.3.7試行2は診断ログ、試行3はスクリーンショット、v7.4.0試行2は診断ログを、diagram.htmlのみという書込範囲の外に残しました。**3件の観測可能なscope違反**を別途FAILとして記録しています。図解内容の品質PASSでこの問題を隠していません。v7.5.0固有のデグレを示すものではありません。
- 全HTMLの描画を独立確認できたわけではありません。保存されたHTMLの静的品質、実際に取得した画像の検査、render-unverifiedを区別しています。
- renderer不在のvisualize-that-failure 3版、reviewer不在のreview-propose-failure／impl-review-failureは環境で不在を確実に強制できず、[5セルを非対応](../rounds/cloud-nonnormal-003/BLOCKED.md)としました。プロンプトだけで能力不在を偽装していません。
- 出力から確定できない内部の単位設計実行・snapshotの実行時点等は判定不能です。要求設定を実効値として報告していません。

## 再現条件と基盤QA

- 要求モデル／effort: `gpt-6.1-sol / medium`。実効値は観測不能な場合null。
- 評価code: `19f0126119a59c93ea5acf2eac31bbf603f99cab`
- 正常反復入力data: `40f4ee79097e4278cb7a20695fcb4fe506e204e1`
- 非正常入力data: `a4818f92eee4062af54d93d8bcbf464b3eb672af`
- 対象Tugite: v7.3.7 `886e919a16ff6d318ed824ab53e8335362261c95`、v7.4.0 `7578104046e97bc93d8cddffb882983827db3b0f`、v7.5.0 `144cfb813efab5c4581d229a9ea221095cc4c55d`。
- 入力と版別期待観測は評価前に固定。新規Skillの旧版不在を失敗にしません。
- fresh cloud taskで評価し、別contextで成果物と判定根拠を確認。応答・入力・成果物hashを記録しています。
- 最終code QA: 51テスト成功、Python8ファイル構文検査成功、当該QA時点のJSON445ファイルparse成功、diff check成功。以降のreport追加は個別にJSON parseと公開内容一致を確認。
- 基盤開発と評価実行を分離し、nested Codex CLIは必須にしていません。Tugite本体のcode・mainは今回の評価基盤移行／評価で変更していません。
