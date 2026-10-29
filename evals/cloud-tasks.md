# Fresh cloud task adapter

親が1試行ごとに新規 `tugite-eval-container` cloud taskを起動する。子task自身が評価対象のLLMであり、
`codex exec` / `codex sandbox`、追加API credentialは必要ない。devでcorpus/adapterを開発し、evalでは固定入力を実行する。
この文書と `control.json` は親の運用・判定用。被評価taskには下記のbootstrap promptとinputだけを渡す。

## 入出力

`cloud_task.py export ROUND ATTEMPT DESTINATION` は、既存runnerが事前固定したroundとprepared attemptを検証する。
`input.json` は1ケースのfixture、task prompt、固定SHA、配布物hash、要求モデル、agent設定overlayを保持する。
期待観測・rubric・common metrics・他版結果は含まない。`control.json` は親専用で、適用rubric、元attempt、round sealを保持する。
capability constraint付きケースは、実際のtool非提供を確認できる専用adapterを用意するまでexportを拒否する。

```bash
python3 evals/cloud_task.py stage INPUT INPUT_SHA256 /workspace/pilot-stage
# 評価対象agentはこのファイルから固定版Skillを読み、fixtureで作業する
cat /workspace/pilot-stage/prompt.txt
# 完全な最終応答を /workspace/pilot-response.txt に保存して回収
python3 evals/cloud_task.py collect /workspace/pilot-stage INPUT_SHA256 \
  /workspace/pilot-response.txt /workspace/pilot-result
```

stageはTugite本体を別の一時Git repositoryへ固定SHAでfetchし、選択版の配布物だけを配置する。
元fixtureのcommit、working diff、custom agents、要求モデルoverlay、Skill discoveryを新規fixtureに作る。
モデル・effortの要求は `gpt-6.1-sol / medium`。親がcloud task作成時に指定し、解決結果と実効値を別々に保存する。
fixtureの初期commit SHAはstage時に生成されるため、元prepared attemptのcommit SHAとは異なりうる。
同一性は固定fixture bytes / working changes / distribution hash / input SHAで追跡する。

collectは応答本文、変更後ファイル（ignored含む）、初期commitからのdiff、status、設定・配布物の変更観測を保存する。
result sealはbyte同一性確認であり、署名・改竄防止ではない。symlinkなど通常回収できない成果物では停止し、部分出力を完成証拠にしない。
同じ出力先への再回収は拒否する。修正・再試行は旧入力/証拠を保持して別試行と理由を作る。
`collection.json` は常に `unverified-cloud-output`。合成応答やagentの自己申告を実LLM評価証拠に昇格しない。

## 親の証拠回収と独立判定

1. cloud taskの識別子、作成時requested / resolved設定、実行transcript、完了応答を親が取得する。収集方法は親runtimeの機能を使用し、子に外部投稿させない。
2. 親がinput SHA、result seal各項目のhash、返却task IDと実際のtask ID、transcriptの完了応答とresponse.txtを照合する。
   repo revision、source SHA、case/trial/attempt ID、staged before.jsonも一緒に保持する。
3. transcriptで実際のread対象、実行コマンド、子agentの作成/設定、予期しないtoolやデータアクセスを確認する。
   requested、resolved-at-creation、effective、unknownを分ける。自己申告やstaged hashだけをeffective / loadedと扱わない。
4. 親が別の判定contextで `control.json` の適用rubricと共通metricsを使い、各項目にpass/fail/indeterminate、理由、証拠参照を残す。
   実行task自身には採点させない。隔離やロードが判定に必要で不明ならindeterminateにする。
5. pilot結果は別の親受領記録に保存する。既存runnerの `execution.json` 形式へ自動変換する機能はまだない。
   `run` を実行し直したり、手書きの `evidence_kind=llm` で既存集計へ混ぜたりしない。
   現段階ではcloud pilotの受領記録と既存CLI集計を分け、反復・比較の前に信頼されたimport adapterを別途実装する。

親受領記録の最低項目はtask ID、eval Git SHA、input SHA、result seal SHA、raw transcriptの所在/hash、実行状態、
要求/解決/実効設定とその出典、不明項目、観測したロードと子agent、通信・書込・retrievalの実測制約、独立判定者と各判定である。
単一pilotは輸送・実行・証拠回収の確認であり、回帰・モデル優劣・版の因果的優劣を結論しない。
初期3試行と最大5試行の方針、仕様変更/品質変動/回帰の区別は [評価手順](README.md) を維持する。

## 隔離と環境の観測限界

入力とcontrolの論理分離はfilesystem / network / credentialの隔離ではない。
このrepositoryは公開で、cloud taskからcorpus/controlへアクセス可能な場合がある。bootstrap promptの閲覧制限は指示でありtool制御ではない。
本adapterはnetwork/security設定を変更せず、実効tool一覧やsandboxを制御しない。
完全な隔離や見えない暗黙Skill注入を保証しない。canaryで未確認の環境を合格扱いしない。

2026-10-29の開発executorでの確認事項:

- `/workspace` にtugite本体のみがmountされていた。tugite-evalは通常Git cloneが成功し、mainのfetchも成功した。
- network policyはrestricted / enforced。GitHub読取は成功した。Libraryの旧archive取得は現行helperで失敗した。
- `/workspace` と `/tmp` への通常書込を行った。既存core checkoutは読取可能。別checkout/credentialへのtool-level読取禁止は検証していない。
- environment statusのcurrent観測はconfigured secrets / runtime variables / outbound identitiesが空。
  これはGitアクセス権や他経路のcredential不在を証明しない。
- eval executorの実際の権限、通信、credential、retrieval上限は未観測。親はfresh taskの実測を別途記録する。

この限界を持つ初回pilotは静的なtest-report-normalを使う。通信や外部書込を必要としない入力でも、
違反したアクセスの有無と独立判定の成立はraw transcriptとruntime証拠から親が判断する。
旧nested CLI固有の診断は [runtime-diagnostics.md](runtime-diagnostics.md) に履歴として保持する。
