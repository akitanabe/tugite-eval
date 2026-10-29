# Round006 harnessの長文化要因

旧応答/採点を読まず、入力prompt・adapter・rubricを点検した。旧006が長すぎるとのHuman判断は親から受領した新しい仕様入力として扱う。
旧004/005/006の入力・fixture・基準・結果は変更しない。

| 箇所 | 観測 | 新007での扱い |
|---|---|---|
| cloud_task.py stageの共通prompt | 読んだファイル・commands・limitationsを回答へ列挙する指示があり、説明と無関係な末尾報告を増やし得る。 | caseの明示modeでtask responseだけを要求。機構の証拠はcollector/親が別に保持する。旧packetの既定指示は保持。 |
| session-flow prompt | 導入章や抜粋の量は指定しないが、何をどう実現しどのコードへ対応するかという広い依頼。 | 同じ範囲のフローと各関数/classの役割を尋ねる中立な依頼にする。短い実装先頭はSkill/rubricの期待として扱う。 |
| infrastructure prompt | route・呼出し順・request・例外・状態確定・限界を列挙して説明要求。 | 主要な接続と確定境界に絞る。独立した限界章や全例外説明を要求しない。 |
| 旧006の技術観測 | Cookie失敗後の状態、期限切れ削除、serial非rollback等まで出力へ残す義務に読め、正確さと網羅性が混ざる。 | 主要経路に必要な意味を達成条件にし、細部は事実参照として維持。全失敗modeや内部項目の列挙は不要。 |
| 旧bootstrapの最終返却 | 本文に加え読んだ参照・制約等を返すため、Human提示時に機構報告が混ざり得る。 | Humanにはresponse.txt本文を提示。seal/pathなど輸送情報は別に扱う。 |

ケースprompt自体に導入・要約章や長い抜粋の強制はない。Skill側の既定形式とharness側の列挙圧力は分けて考える。
今回の監査は因果的な出力量測定ではない。実際の長文化がどの指示に由来するかは断定しない。

最新の中心視点は処理の流れと、その中で各関数/classが何をするか。識別子先頭は維持するが、
コード内部説明の短縮版や全関数の役割catalogを目標にしない。正確さは重要な接続を保つための裏づけとして扱う。

候補SHA通知後、親の明示指示でcase promptをさらに中立化し、source/outputを読む前に記録した。
prompt・reporting・rubricとSkillの変更が同時なので、このrunをSkill単独の比較実験とは扱わない。
