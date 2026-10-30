# Round011: meaning/purpose clarification — candidate待ち

[監査と変更理由](AUDIT.md)、[corpus](corpus.json)、[登録](preregistration.json)を参照。
prompt・fixture・reportingは007〜010と同じ。最新の明示要件により期待の中心を、処理単位の意味・機能上の目的へ明確化した。
戻り値/受渡し/fields/statusは、流れの理解に不可欠な場合だけ補足する。各節点の既定項目にしない。
コードに根拠を持つ機能上の寄与と、共有されていない歴史的設計意図を区別し、捏造しない。

新candidate SHA未提供。packet/index/snapshotは作成しない。source引用は最終SHA到着後に確認し、必要なら引用だけ対応づける。
候補受領後の既存adapter手順:

```bash
python3 evals/prepare_398.py candidate <NEXT_CANDIDATE_SHA> .local/explain-398-round011 \
  --corpus rounds/explain-398-role-meaning-011/corpus.json \
  --case explain-398-session-flow --case explain-398-infrastructure
```

実LLM評価は親が起動する。caseは2件各1回だけ。全attemptと全出力を保持し、都合のよいsampleだけを選ばない。
役割・意味を基準に親が品質を判断し、必要なら次候補の同じ2caseへ進む。全suite/追加case/version/PRは行わない。
旧結果を新基準への適合根拠にせず、要件明確化を含む比較をSkill単独の因果効果としない。
