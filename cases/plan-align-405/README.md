# Issue #405: plan-align

プログラミングの要求からHumanと実装範囲・失敗許容・保証を決めるSkillの単独達成評価。
実モデル評価は未実施。開発環境ではケース準備と機械的検証だけを行う。

候補は `akitanabe/tugite` の `feat/405-plan-align`、固定SHAは
`cf4a8571c7f71e0069ad8b21c4d7929a0ceef46d`。
baseはPR #404の `7a9d6bbdbc2a9be28f23a0c71c4a74aafe420710`。配布versionは7.6.0。
このdirectoryを含むeval commitをinput/adapter revisionとして固定する。branchの最新を実行時に追従しない。

## 固定シナリオと判定

正本は `corpus.json`、Humanの後続発言は親だけが読む `dialogue.json`。
issue #405全文とコメント0件を2026-11-17に確認した。

| Case suffix | 独立した要件・観測 |
| --- | --- |
| simple | 既存コードへの小さな機能追加。根拠のある仮案、短いフロー、不要な基盤追加の回避 |
| excess | 付随通知。一般的な防御案を必要性と許容失敗で選別 |
| integrity | 金銭に準ずるポイント。再送・並行性の下で残高と移動記録を保つ |
| human-correction | 付随通知から契約上の確認へHumanが前提を修正。現在版を更新 |
| propagation | 非同期帳票。受付・状態・失敗・ダウンロード・認可へ波及を反映 |
| unresolved | 復旧不能な顧客削除。保持期限等を推測で確定せず未決で終了 |
| stop | 合意後もプランだけを返し実装・検証・委譲へ自動遷移しない |

各caseの必須observationsと共通metricsにpass/fail/indeterminate、理由、該当turn/操作証拠を付ける。
仕様引用は適用候補の根拠であり、被評価応答に同じ表現を要求するものではない。
質問数、承認回数、文字数、構成要素数、特定アルゴリズム、固定文言を正解にしない。
要求に対する範囲・保証の妥当性、Humanの修正への応答、対話負荷を評価する。
重要な整合性を省く「簡素化」と、要求外の防御を積み増す行為の両方を失敗として識別する。
提示順や分割に複数の適切な結果があることを許容し、未決を正直に残すことを未完了の失敗にしない。

## 独立環境への引き渡し

1. 親がこのdirectoryを含むevalの完全SHAと、上記候補SHAを記録する。独立した `tugite-eval-container` でeval repoをそのSHAへclean checkoutする。元のmain履歴を保持しforce/reset/cleanは使わない。
2. 次のコマンドで、固定Git SHAから配布物全体・7ケースの入力・親用controlを作る。モデルは要求値 `gpt-6.1-sol / medium`。この準備はモデルを起動しない。

```bash
sha256sum cases/plan-align-405/corpus.json cases/plan-align-405/dialogue.json
python3 evals/prepare_398.py candidate \
  cf4a8571c7f71e0069ad8b21c4d7929a0ceef46d \
  .local/plan-align-405-001 \
  --corpus cases/plan-align-405/corpus.json
```

3. `index.json` の7ケースをそれぞれfresh taskで実行する。親だけがcorpus/control/dialogueを保持し、被評価taskには対応するinputとbootstrapだけを渡す。`evals/cloud-tasks.md` のcheckout確認・stage手順を使う。出力品質は `collect --quality` で回収可能。
4. 初回promptの応答を保存し、同じtaskへ `dialogue.json` の当該caseの発言を順に一つずつ送る。将来の発言やrubricを先に渡さない。7ケース各3応答（初回＋後続2発言）を観測する設計だが、この数は品質基準ではない。追加確認で固定発言が意味をなさなくなったらad-libせず逸脱を保存し、判断不能の項目を明示する。異なる構成や順序だけで失敗にしない。
5. 全Human/assistant発言を順序・区切り付きで保存し、最終プランだけで採点しない。操作transcript、source/test/configの前後状態、input/result hash、要求・解決・実効model/effortを記録する。未観測の実効値はunknown。自己申告や配布hashだけで内部遵守を証明しない。
6. 独立した判定contextで固定rubricに照らして裁定する。操作証拠不足はauthority項目でindeterminateとし、出力品質と分ける。前後でcorpus/dialogue hashを照合する。結果に合わせて基準を変更せず、必要な再試行・修正は理由付き別roundにする。
7. 候補SHA・eval SHA・7ケースの結果と限界を開発側へ返す。結果受領後にPR #404をbaseとするstacked PR作成へ進む。merge/tag/releaseは行わない。

本評価は単独達成の初回1試行/ケース。過去の評価や他Skillとの優劣比較を含めない。
通信や権限の拒否を迂回せず、輸送不成立をSkillの失敗と区別する。

## 開発側の検証とQA境界

```bash
TUGITE_SOURCE_REPO=/workspace/tugite python3 tests/plan-align-405-test.py
python3 tests/cloud-task-test.py
python3 tests/cloud-receipt-test.py
python3 tests/eval-runner-test.py
git diff --check
```

QA ownerは今回の開発担当。Task Specはissue #405と明示された独立評価の依頼、baseは本体PR #404とeval `935218446442864fb27beaa42fa92b6647dd343a`。
要件とoracleはcorpusの独立したrequirements/Human修正・期待観測に固定し、Skill出力から導かない。
候補の配布・起動契約は本体のGunte、入力/引用/輸送は既存runnerと上記決定的テスト、意味品質は後続の独立評価が所有する。
引用欠落と未登録必須観測の拒否を変更テストで確認する。合成witnessはadapter検証だけに使い、意味品質のmutation evidenceとは扱わない。
コードfixtureは静的な計画根拠であり、被評価Skillがコード・テストを実行する必要はない。Gunte保証の複製やLLM応答の文字列判定を追加しない。

機械的検証の実績: 新規3件、既存walkthrough 6件、cloud-task 30件、cloud-receipt 24件、runner 17件が成功。上記固定候補からprepare/exportで7入力の生成が成功し、inputにrubric/dialogueを含めないことを確認した。固定入力のSHA256とcase一覧は `current.json` に記録した。これらは実モデルの品質結果ではない。
