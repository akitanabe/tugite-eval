# Current coverage — 基本8ケースで通常対象が完結

Userは読者指定の実験を不要と判断し、evalからも除くことを指示した。
通常評価は[current.json](../../cases/explain-399/current.json)の基本8ケースのみ。
既に実施した8件は通常対象の全ケースであり、追加3件を終わらせる必要はない。

## 履歴上の11packetとの差

当時の11入力は基本8件に、normal / unknown-connection / infrastructureの読者指定版3件を加えたものだった。
追加版は依頼に一文を加えただけで、fixture・候補・モデル要求・判定基準は基本caseと同じ。
追加の反復条件ではなかった。現在はこの3件が廃止済みなので、通常評価の残件/欠損として数えない。
COVERAGE_DELTA.jsonの旧比較情報、固定corpus/packet/index/quality-protocolは履歴として保持する。

## 品質判定の証拠

8直接taskの完了は親から報告された。EXPECTED_CONDITIONS.jsonの静的照合は維持する。
このworkerに未供給の完了本文や実効条件は、受領/読取したかのように扱わない。
廃止は試行結果のPASSへの読み替えや元判断の削除ではない。実応答の独立品質確認と運用上の制約は引き続き区別する。
