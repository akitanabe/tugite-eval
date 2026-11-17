# Issue #403: code-explain / walkthrough-assist

新しい座席予約fixtureによる単独達成評価。正本は `corpus.json` と親だけが読む `dialogue.json`。
固定SHAをGit経由で独立した `tugite-eval-container` へ取得し、fresh 10ケース・30応答の実評価と独立判定を完了した。旧ケースや旧出力を流用せず、旧結果を本評価の証拠に含めない。

評価対象は本体 `1b1862379ec521de5ad2905378e3ebf29b8d8499`、eval adapter/corpus `dba7308dfb1a07e1aafa3c3e69479051b382a406`。eval変更はmainへ直接push済み。
出力上の不合格は0件。固定rubricは20 pass / 0 fail / 2未確定、共通metricは18 pass / 0 fail / 10未確定。
未確定事項は基礎Skill先行利用の内部証明と、authority-and-scopeの操作ログ独立確認。要求モデルは `gpt-6.1-sol / medium` で、実効model/effortは未観測。
出力品質の観測を内部遵守・権限操作の全面的な保証に読み替えない。
その後の本体 `53fdd1ef797a0c178651aab4b82902f4a608c2ef` はv7.6.0の版表記のみの変更であり、このHEAD自体の実モデル再評価は未実施。

## 対象と判断

| ケース | 観測する境界 |
| --- | --- |
| tests-no-report | test-report先行、主要機能と件数の区別、質問から新発見 |
| tests-current | 現状に適合する報告の再利用、取消しassertの見逃し |
| tests-stale | 古い実装判定の更新と、生きているテスト指摘の保持 |
| human-merge | 重複指摘の統合、新指摘、要求変更の伝聞と未確定 |
| skip-scope | Humanの分類・範囲指定、skip/nextと承認の区別 |
| code-no-explanation | code-explain先行、通知失敗と確定状態 |
| code-current | 説明再利用、指定箇所の深掘り、次・終了 |
| code-unknown | 未提供通知内部とHumanの推測・承認の区別 |
| code-explain-separated | 全体→実経路→意味単位、複数関数にまたがる役割 |
| code-explain-mixed | 同一関数の意味分解と実経路の忠実性 |

各IDのprefixは `walkthrough-403-`。独立要求はfixtureの `requirements.md`。
提示テストは意図的に不完全であり、取消しの状態復元と重複予約の退行を見逃す。
開発側の決定的テストは、これらのmutationが提示テストを通過し独立要求に違反することを確認する。
意味判断はcorpusの観測基準で行い、特定の見出し・分割数・言い回しを唯一解にしない。
基礎Skillの再利用は回答品質と運用記録から判断し、出力だけから内部Skill呼び出しを断定しない。

## 独立eval環境での実行

devでは実モデルを起動しない。親は `evals/cloud-tasks.md` のfresh cloud taskとstage/collectを使う。
要求モデルは既存品質protocolと同じ `gpt-6.1-sol / medium`。まず各ケース1試行の達成観測とし、比較・統計的優劣は主張しない。
不明な実効model/effort、ロードや子agentの情報はunknown。CLI初期化失敗や輸送失敗をSkill試行に数えない。

以下のprepareは、明示的に再評価する場合の再実行手順。完了済み評価の残作業ではない。再評価対象の固定commit SHAと新しいround出力先を指定する。
本体とeval adapter/corpusのrevisionを別々に固定し、作業treeの変更をbase SHAの配布物と取り違えない。

```bash
python3 evals/prepare_398.py candidate FULL_CANDIDATE_SHA .local/issue403-new-round \
  --corpus cases/walkthrough-403/corpus.json
```

`prepare_398.py` は既存の輸送helper名であり、必ず本corpusを明示する。
prepare前にcorpusとdialogue双方のSHA256を親の実行記録へ固定し、実行後も照合する。
`dialogue.json` は親にだけ渡し、被評価taskへ将来の発言・rubric・期待出力をまとめて渡さない。
親はstageされた初回promptに対する応答を保存し、その同じケースtaskへ定義済みの発言を一つずつ逐語的に送る。
ケースごとはfresh task、ケース内は同じ対話。分割・順序が異なっても発言を期待回答へ誘導するよう変更しない。
不意の追加確認で固定発言が意味をなさなくなった場合はad-libせず、その逸脱を保存して該当項目をindeterminateとする。
最後の応答までの全Human/assistant発言を区切りと順序付きで保存し、最終まとめだけで採点しない。
`collect --quality` のresponseに全対話記録を渡し、source/test/configの前後差分とともに回収する。
独立判定者は必須観測ごとにpass/fail/indeterminate、理由、turnと根拠箇所を記録する。
Humanの終了後の追加調査や無許可変更があれば、最終文章が良くても権限・対話項目をpassにしない。

初期準備時にはLibrary取得がdevのネットワークで拒否された。その通信制約の解消は未確認。
その後、許可されたcommit/pushとGitHubの固定SHA fetchにより移送と今回の評価は完了しており、Libraryの制約は今回評価の未解決blockerではない。
今後も通信制限を迂回せず、新たな移送失敗があればその経路と影響を区別して報告する。

## 開発側の決定的検証

```bash
TUGITE_SOURCE_REPO=/workspace/tugite python3 tests/walkthrough-403-test.py
python3 tests/cloud-task-test.py
python3 tests/cloud-receipt-test.py
python3 tests/eval-runner-test.py
git diff --check
```

`TUGITE_SOURCE_REPO` は今回の生成済み候補を指定する。省略時はその候補との引用照合だけskipする。
fixture/oracle、runnerの明示version指定、引用の存在・欠落拒否の検証であり、LLMの意味遵守を実証するものではない。
