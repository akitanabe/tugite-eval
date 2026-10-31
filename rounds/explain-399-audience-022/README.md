# Round022 — audience-only experiment

Userが現Skillのまま15歳くらいを対象に説明する実験を依頼したため、021と同じ3case各1回を別roundへ固定する。
候補commit/tree、配布Skill、fixture、モデル要求gpt-6.1-sol / medium、reporting、全観測/metrics/必須gateを変更しない。

各caseの元promptの末尾へ改行と、次の一文だけを追加する:

> 15歳くらいの人に伝わるように説明してください。

比喩の指定、コード禁止、初心者の断定、追加の短文化規則、回答例や他の指示を加えない。
corpusとresolved-corpusの変更は各promptへのこの一文追加だけ。judge-only校正は021とbyte一致。
新しい「15歳向け」合否基準を作らず、現在の構造/意味/正確性/粒度の基準を維持し、読者指定による表現の変化を観察する。

比較対象は同じ候補の021 normal / unknown-connection / infrastructure。
親が両roundの同じcaseの実応答を対応づけ、用語・意味の伝達・経路の明瞭さ・重要条件/限界の保持などを同じ基準で読む。
旧応答が未取得なら比較未完了とし、旧判断を変更したり記憶から応答を再構成しない。
単回の小標本なので、観測された差を年齢指定の安定した因果効果やモデル優越として断定しない。

親が3fresh trialを起動する。準備workerはLLM起動/採点をしない。
Tugite本体、version、PRの変更なし。旧round/履歴を保持する。
