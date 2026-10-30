# #399 preregistration — new candidate待ち

[再利用監査と新基準](../../cases/explain-399/README.md)、[corpus](../../cases/explain-399/corpus.json)、[登録](preregistration.json)。
#398の旧candidateは使用しない。新#399はmainから別開発taskで構築中。旧roundを変更せず新しい達成基準で扱う。

ケースはexplain-399-separated、explain-399-mixedの2件。promptはどちらも合成Session機能の説明依頼のみ。
全体の意味フロー、忠実な実コード実行フロー、主要処理の意味/条件/効果を確認する。
経路と説明の一体化、適切な段落/図/表などは許し、旧brevity/identifier-first-only/基盤省略基準を課さない。

## 新SHA受領後

まずcorpusのbasis_pendingを新sourceの正確なpath/quoteによるbasisへ解決する。
期待・fixture・promptは固定のまま、source provenance補完を別commitで記録する。
未解決corpusを旧sourceや架空quoteで実行しない。現時点でinput/index/snapshotは作らない。

source provenance解決後だけ、既存helperを明示corpusで使える:

```bash
python3 evals/prepare_398.py candidate <NEW_ISSUE399_SHA> .local/explain-399-012 \
  --corpus cases/explain-399/corpus.json \
  --case explain-399-separated --case explain-399-mixed
```

helper名は旧名だが、新caseは旧398版/期待値を継承しない。candidateのみ・各1回に限定する。
固定SHAの配布物全体とagent定義をstageし、親がfresh task（requested gpt-6.1-sol/medium）を起動する。
被評価taskへcorpus/rubric/旧結果/本handoffを渡さない。説明本文と操作証拠は分け、collect --qualityを利用する。
独立judgeは#399要件と実codeで構造・忠実性・説明粒度を判断し、Reference Outputの文面一致や内部全列挙をoracleにしない。

新candidate SHA未提供のため、配布identity/source引用確認・packet freeze・実LLM評価は未実施。
全歴史を保持し、旧結果から新合格/モデル優越を主張しない。全suite、余計な説明agent、version/PRは対象外。

準備QA: tests/explain-399-test.pyの3検査成功。分離fixture byte一致、新基準の#399根拠、
新candidate/source basis未解決、2case scopeを確認。両fixtureの成功・binding拒否・commit失敗・再利用拒否・
認証状態取得・Cookie失敗後の確定状態を実行確認した。混在variantに架空のexchange委譲がないことも確認。
このfixture検証はLLM評価ではない。静的読解でも実装上の状態境界を照合し、期待の最終責任は準備ownerにある。
単回sampleの出力品質判断と、既存reportの3回完了gateを区別し、1回から反復比較/因果効果を主張しない。
