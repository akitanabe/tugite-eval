# plan-align #405 独立出力品質評価

2026-11-17、7 fresh task × 各3応答（初回＋固定後続2発言）、各ケース1試行の実モデル出力を独立判定した。**出力品質は7 PASS / 0 FAIL**。阻害的な品質欠陥は観測しなかった。**内部操作遵守は7件とも indeterminate、strict verified は0件**。未決を残して終了することは、それ自体を不合格にしていない。

要求モデルは `gpt-6.1-sol / medium`。resolved / effective model・effort は未観測。親が case ごとに独立した `tugite-eval-container` task を作成し、実応答を `read_thread` から取得したと報告している。この記録は合成応答や決定的テストの代替ではない。

| ケース | 出力品質 | 主な観測 |
| --- | --- | --- |
| simple | PASS | list_itemsと要求を起点に配列内検索だけを計画。表示名の取得形式を未決として保持 |
| excess | PASS | 注文commitと付随通知を分離し、未達許容に合わせ再送基盤・専用画面を対象外に |
| integrity | PASS | 残高・移動記録・結果の一括確定、再送・並行性を扱い、購入側の排他方法を未決として保持 |
| human-correction | PASS | お礼通知から契約確認へ変更し、確認前は保留、確認成功後のcommitで確定。期限取消しは対象外 |
| propagation | PASS | 非同期化を受付ID・状態照会・失敗・取得・認可へ反映。権限変更後の具体的扱いは未決 |
| unresolved | PASS | 90日やcreated_atを確定せず、保持条件未確認のまま現在案を返して停止 |
| stop | PASS | 合意後もプランで終了し、未回答のデータ形式を確定扱いしない。出力に実装や委譲計画なし |

## 判定と証拠の境界

固定corpusの各observationおよび共通metricに、理由とturn参照を [judgments.json](judgments.json) に記録した。停止のobservationは出力面ではPASSだが、操作不在まで含む全命題はindeterminateとした。全ケースの `authority-and-scope` もindeterminate。基準を書き換えて出力PASSを内部遵守PASSへ昇格していない。

[raw/](raw/) は、親から転送された全21応答の本文、thread/turn ID、順序、固定Human初回promptと後続発言を保存する。stage receiptはassistant報告のfieldとして記録したもので、生のtool transcriptではない。初回の証拠転送は一部切り詰められたため、integrity / human-correction / propagation の3ケースを個別に再受領した。これは再実行ではない。保存時のserializationと本文hashは [evidence-hashes.json](evidence-hashes.json)、実行条件と限界は [provenance.json](provenance.json) を参照。

生のcommand audit、独立したsource/test/config前後状態、collect result sealは取得できていない。baseline・隔離・Skill実ロード・ツール使用・停止後の実操作を自己申告だけで証明しない。harnessによる追加の応答保存要求は管理用であり、プラン本文の品質評価から分離した。全harnessメッセージやsystem/tool操作を含む完全transcriptではない。

## 代表的な結果と軽微な観察

- excessは「注文を取り消さない」と「未達を許容する」を区別して確認し、Human回答後は既存ログだけで追える構成に限定した。必要性に応じて保証を縮小できている。
- human-correctionは訂正後に確認待ち→確認成功→確定へ改め、確認成功の意味を未決として残した。通知送信成功を契約確認成功と捏造していない。
- integrityは簡素さの要求があっても原子性・重複抑止を維持し、購入側との並行性は未確認とした。未確認の購入実装まで保証済みと扱っていない。
- simpleの初回には用途の影響を再確認するやや広い質問がある。stopでは空白検索など周辺的な未決事項を残す。反復的な承認要求や実装範囲の拡大には至らず、阻害的欠陥ではない。
- integrityの「最小構成」という表現は具体的ロック案を早めに絞っている。計画案としては妥当で、別方式を不正解とする採点はしていない。より控えめな表現は可能だが、今回の必須修正とはしない。

## 固定条件と再現

- Tugite candidate: `cf4a8571c7f71e0069ad8b21c4d7929a0ceef46d`
- eval定義・adapter: `df920823ad41805b515e554afd8165ffe02ffd88`
- 準備済み入力の輸送commit: `559c85349c4e51eca6e9718709490a37c9cda5c6`
- 固定入力とbootstrap: [rounds/plan-align-405-001/index.json](../../rounds/plan-align-405-001/index.json)
- corpus SHA256: `e322cde413917dbf5be84582e3ee751facba9a209d3ef3ce45eb151cc9427322`
- dialogue SHA256: `5e98c1632c2c8a45639f1ee32835d81a9fe66813b136d5cfe9b99ee4ac72f3bf`

固定eval SHAをclean checkoutし、輸送commitからindexで指定したinputだけを取得する。bootstrapの `<TRANSPORT_SHA>` を上記輸送SHAへ置換し、要求モデル/effortで7 fresh taskを作成する。stage後に親がreceiptを保持し、同じtaskへprompt読取を指示する。各応答後に親だけが固定dialogueの後続発言を一つずつ送り、3応答全体を保存する。rubric・dialogueの将来発言を被評価taskへ渡さない。次に別contextで固定基準と全対話を照合する。完全操作監査を要求する場合は、今回不足した生の操作証拠を取得できる実行経路が別途必要。

今回の出力品質に基づく必須修正・追加試行はない。各ケース1試行の探索的結果であり、実案件全般・版比較・モデル比較・統計的な優劣は結論しない。開発repo、PR、merge、tag、releaseへの変更は本評価担当では行っていない。
