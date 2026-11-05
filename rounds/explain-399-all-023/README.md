# #399 full prepared coverage at5cc3e4 — Round023

2026-11-05、Userが最新候補について用意済みevalすべての実行を依頼したとの親指示に基づく。
対象Skillはexplain-this。core/version/PR/merge/releaseの変更は対象外。
候補出力を読む前に、入力再利用・対象集合・最新適用基準を固定する。

## 全対象の棚卸し

| 対象 | 元round | 件数 |
|---|---|---:|
| separated / mixed Session機能 | 018 | 2 |
| infrastructure / unknown-connection / shipping正常・境界・欠落依存・意図未共有 | 019 | 6 |
| normal / unknown-connection / infrastructureへの15歳読者指定一文追加 | 022 | 3 |

合計11case各1回、固定候補、要求gpt-6.1-sol / medium。モデルを代替しない。
読者指定3件は既に用意した比較入力なので全対象に含めるが、年齢別の新しい合否基準は追加しない。
旧004–022の候補ごとの反復roundは独立した新しい問いではないため、全履歴の全セルを再実行しない。
#398の旧session-flowは#399でseparated/mixedへ置換済み。旧brevity/identifier-first等の失効した形式試験は現候補へ課さない。
#397の別Skill・旧3版比較は今回のexplain-this準備集合に含めない。全fixture/元依頼/overrideは元caseから保持する。

## 現行要件と旧受入句の調整

現行要件は、全体説明→主要コード実行経路→意味上の処理単位ごとの詳細説明。
構造/意味/正確性・重要条件/副作用/限界を独立に見る。形式だけのPASSでは説明品質のPASSとしない。
020–022の意味観測を全11件に適用し、旧「意味が伝われば図/注釈だけでもよい」という句だけを
最新指示に従い、後段の意味単位の詳細を代替しない条件へ置換する。旧判断を再採点/上書きしない。
`ordered-semantic-detail`を加え、構造・意味と合わせ3観測を総合quality PASSの必須gateとする。

意味の区切りを全関数/class一覧や図の各nodeへの逐語解説へ固定しない。意味処理が複数関数を横断したり
一関数内に複数の意味処理があっても、実装上の呼出し/所属とコード根拠を正確に示す。
自然に意味と関数境界が一致することを禁止せず、任意の分割数・heading語句・長さを固定しない。
欠落依存では既知部分の役割と不明を区別し、未知内部の完全な説明を強制しない。
小さなshipping関数でも3段階は簡潔でよく、一般講義/コードdump/全field列挙を要求しない。

## 実行条件と未実行の扱い

fresh cloud taskの作成APIは準備workerのtool一覧にない。既知のnestedCLI初期化Read-only/socket/proxy問題と
同じ経路を再試行する新しい根拠はなく、代用やモデル変更をしない。親が11fresh taskを作るhandoffを用意する。
このroundの実LLM実行・独立品質採点は準備workerでは未開始。static/stage確認を実応答品質PASSと数えない。

各完了時にresponse path/hash、result seal、task ID、requested/resolved/effectiveモデルの出典、不明を保存し、
独立judgeが表示順/経路、意味単位/意味の達成、事実/条件/副作用/境界、粒度・権限を読んで判定する。
候補内容の問題、基準/入力の不整合、運用・環境失敗を分け、欠損をPASSにもSkill failureにも変換しない。
失敗を隠した取り直しはせず、復旧が必要なら元attemptと理由を保存する。旧完了は現候補の実行数に数えない。
単回11件は全用意済みシナリオのスモークであり、安定性や版差の因果的優越は主張しない。

## 親からの実行開始報告による現在の範囲

準備中に、親からcanonical8件を固定候補・fixture repo17c18c2cで既に直接起動したとの報告を受領した。
[DIRECT_TASKS.json](DIRECT_TASKS.json)にthread対応を保存し、8件を重複起動しない。
11個の既存準備入力という棚卸しは保持するが、現在実行中バッチは8件。読者指定3件はこのバッチ外の保留資料と分ける。
直接taskは元依頼/overrideを適用するとの親報告であり、今回sealed packetをstageして実行した証拠ではない。
品質判定には実際の完了本文と条件を使い、未使用のinput sealを実行証拠に遡及流用しない。
このworkerへ完了本文・実行条件は未供給なので、現時点の品質判定は未実施。
