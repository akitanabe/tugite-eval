# test-report #407: independent evaluation handoff

Candidate: `a196a7c65495de00230261e71c79b42337421305` (#408)。
Baseline: `cf4a8571c7f71e0069ad8b21c4d7929a0ceef46d` (#406)。
正本はcorpus.json、固定SHAはversions.json、入力hashと要求設定はcurrent.json。
本directoryを含むeval commitを取得して実行する。mainや#408の最新HEADへ追従しない。

既存のrunner / prepare_398 / cloud_task / output-quality-v1を再利用する。
4ケースを同一fixture・prompt・共通rubricで両版に適用し、初回は各セル1試行、計8 fresh taskを実施する。
これは小標本の探索的な品質観測。既存runnerの3試行比較要件を満たす正式比較や因果的優劣を主張しない。
既存baselineの全件詳細提示は仕様上の意図された方針であり、baseline仕様違反と混同しない。
候補の抽象化達成と共通の意味保持・診断品質を別に読む。

- aggregate: 同一振る舞いの集約、境界期待値、逐次と並行性、問題なし領域、取消の見逃しと順序の誤拒否。
- missing: 要求にはある取消に対応するEvidence不在、限定観測範囲と追跡可能性。
- unknown: skipされた逐次テストの存在と未実行を分離、並行性の要求未確定を維持。
- details: 全体の集約と利用上限・取消の選択詳細を同時に要求。

期待値はfixtureのrequirements.mdと実際のassertionから事前固定した。
開始10は可、終了20は不可、99.9円の割引は99、上限1000という意味を保持する。
取消は戻り値のみのassertionで復元を識別しない。独立readの順序は要求上どちらでもよい。
件数、文字数、特定のheading/table、固定の表現、唯一の分類をoracleにしない。
全体を理解できること、重要条件を失わないこと、具体的根拠へ辿れること、不要な検証を強制しないことを意味で判断する。

## Independent environment steps

1. このブランチの完全eval SHAをclean checkoutする。既存作業があれば保持し、新しいcheckoutを使う。
2. 次を実行し、モデルを起動せず固定Git配布物から8入力を生成する。

```bash
python3 tests/test-report-407-test.py
python3 evals/prepare_398.py both \
  a196a7c65495de00230261e71c79b42337421305 \
  .local/test-report-407-001 \
  --baseline-sha cf4a8571c7f71e0069ad8b21c4d7929a0ceef46d \
  --corpus cases/test-report-407/corpus.json
```

3. index.jsonの各inputについてfresh tugite-eval taskを作成。要求model/effortはgpt-6.1-sol / medium。被評価taskへinputとbootstrapだけを渡し、corpus/control/期待値や他版出力を渡さない。
4. evals/cloud-tasks.mdに従ってstageし、prompt.txtのtest-report入口から作業する。one-shot応答を全量保存し、cloud_task.py collect --qualityで回収する。今回は後続Human発言なし。要求されたテスト/コードは実行しない。開発テストでのfixture実行とは区別する。
5. 別contextの判定者がcontrolの必須observationとcommon metricごとにpass/fail/indeterminate、理由と応答・source参照を保存。出力の意味と操作遵守を分け、操作監査がなければauthorityはindeterminate。モデル実効値の不明もunknownとして記録する。候補で全件列挙がなくても意味と追跡可能性があれば許容する。
6. eval SHA、candidate/baseline SHA、input/result seal hash、全応答、操作記録、判定、実効設定の観測限界を返す。corpusの前後hashを照合する。結果に合わせて期待値を変えず、必要な修正は理由付き別roundにする。

既存prepare helperのfocus-trialsはこのcase IDでは常に1。3試行が必要になった場合は既存runner prepare/exportのtrial指定を使い、事前に追加理由を固定する。
輸送拒否や環境不成立をSkill不合格にしない。完全隔離や暗黙ロードはhashだけで保証しない。

開発QA：要件は#407、共通oracleは同じ要求・同じfixture、baselineとcandidateの差分は本体の固定commit。
検証面は入力固定と引用照合を既存runner、実動作の反例成立をfixtureテスト、意味判断を独立evaluatorが所有する。
取消更新を除く変更でもsuiteが通る見逃し、公開契約を満たすread順序変更でsuiteが落ちる誤拒否を決定的に確認する。
被評価応答の文字列検査や本体Gunte保証の複製はしない。
実モデル評価は開発環境で未実施。mainへの直接push、本体・#408変更は行わない。

開発側の実績：fixtureテスト3件成功。上記prepare/export入口をGitHubの両固定SHAから実行し、8入力を生成。各inputのrepo_sha・skill・input hash・rubric非混入を確認し、両版各caseで引用を欠落させる一時的な変更を既存validate_caseが拒否することを確認した。git diff --check成功。生成packetは/tmpに置き、持続的な引き渡しはこのcommitと再生成コマンドで行う（実行時生成されるround IDやfixture commitは内容hashとともに記録する）。
