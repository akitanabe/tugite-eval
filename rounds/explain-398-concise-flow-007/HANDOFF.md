# 短い処理フロー: 2 sample handoff

新candidate SHA待ち。candidate packet/index/snapshotはまだ作らない。
[要件と適用](../../cases/explain-398-concise-flow/README.md)、[harness監査](../../cases/explain-398-concise-flow/AUDIT.md)、
[事実参照](../../cases/explain-398-concise-flow/REFERENCE.md)、[登録](preregistration.json)を使用する。
旧004/005/006のfixture/input/rubric/resultsは保持し、新適合の根拠にしない。

中心は処理の流れと、その中で各関数/classが何をするか。実装識別子を先に短く説明し、重要な接続を追えること。
コード内部の解説や網羅的な関数役割catalogを目標にしない。導入・長い抜粋・全例外説明・操作一覧を必須としない。
短くするために重要な事実の誤りや必要接続の欠落を許さない。固定の語数/行数/templateや受理例文は使わない。

## 新SHA受領後だけ実施

```bash
python3 evals/prepare_398.py candidate <NEW_FINAL_CANDIDATE_SHA> .local/explain-398-concise-samples \
  --corpus cases/explain-398-concise-flow/corpus.json \
  --case explain-398-session-flow --case explain-398-infrastructure
```

旧candidateで新packetを代用しない。sourceは適用引用・配布identityだけを確認し、期待を候補出力に合わせて変えない。
2packetのpath/hashを照合し、新delivery commitへ保全する。

新caseは`response_reporting=task-response-only`を指定し、stage共通指示のファイル/command列挙要求を外す。
親は固定code/data SHAのfresh eval taskでstage→固定Skill→collect --qualityを使う。gpt-6.1-sol / medium。
control/rubric/REFERENCE/旧応答を被評価taskへ渡さない。Humanへ提示するのはresponse.txtの説明本文だけ。
seal/path等の輸送情報は親が別に保持し、応答本文へ参照一覧や環境報告を追記させない。
理解に影響する未確認接続や制約がある場合は説明の該当箇所に短く含める。運用上の拒否/失敗は別に正確に報告する。

**親が2caseを各1回だけ起動し、実際の本文をHumanへ提示して停止。追加case・反復・全件展開・version更新・PRは禁止。**
準備taskはLLM trialを起動せず、採点しない。完全内部証跡/実効model不明は制約のまま保持する。

事前固定corpus SHA-256: `ff942b689ca36a4fdca78edcd2875d6440279397516eda21b1218e0c941ab206`。

今回のpromptはフローと各関数/classの役割を尋ねる中立な依頼へ改訂した。回答templateや受理済みfixture回答を埋め込まない。
prompt・response reporting・rubricも旧006から変更されるため、結果をSkill変更だけの独立した改善とは主張しない。

source全体改訂で旧版の引用が無くなったため、適用source引用だけを固定candidateの実文へ更新した。
期待観測・prompt・fixture・共通metricに変更がないことをbasis除外で機械照合した。
