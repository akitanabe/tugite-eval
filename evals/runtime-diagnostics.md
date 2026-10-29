# Runtime diagnostics and completion boundary

この記録は実 LLM 評価の結果ではない。network policy / CLI / nested sandbox の観測であり、Skill の成否へ変換しない。
2026-10-29 の tugite-eval、Codex CLI 0.163.0 を対象とする。既存 proxy / CA / authentication を維持し、
認証情報の読出し、新 credential、sandbox 無効化、拒否先への迂回は行っていない。

## Backend 接続

実行した最小 probe（stdout / stderr を別ファイルへ保存）:

```bash
codex exec --ignore-user-config --ephemeral --json -s read-only \
  -m gpt-6.1-sol -c 'model_reasoning_effort="medium"' \
  -c 'sqlite_home="/workspace/eval-evidence/state"' \
  -c 'log_dir="/workspace/eval-evidence/logs"' \
  -C /tmp --skip-git-repo-check 'Reply with READY only. Do not use tools.'
```

非機密エラー:

```text
Proxy connection failed: HTTP CONNECT failed with status 403
url: wss://chatgpt.com/backend-api/codex/responses
```

既存認証は `codex login status` が `Logged in using ChatGPT` と報告したが、推論応答は得られていない。
`thread.started` は推論成功の証明ではない。CLI の自動再試行は停止した。

`environment_status` は現在 `observations_current=true` / policy `enforced`。
制限付き HTTP 許可リストは package manager preset と GitHub 等を含むが `chatgpt.com` を含まない。
従ってこれは proxy egress の境界であり、model不在、トークン不在、Tugiteの不具合と判定する材料ではない。

必要な最小設定案は、環境の正式なネットワーク設定で **chatgpt.com を既存許可リストへ追加**すること。
現在の既存認証方式では `api.openai.com` の追加や新 API key は不要。
同じ host に model catalog / responses / account由来MCPへのアクセスも現れている。
追加後も実際の認証・モデル利用権・各APIの可用性は再検証が必要であり、成功を保証しない。
proxy解除、TLS検証解除、別proxy/routeへの切替は解決策にしない。
本作業から環境設定は変更しておらず、この action は拒否のまま保留。

## Nested sandbox

canary は `runner.py` の named profile を `codex sandbox -P eval ...` に渡して起動する。
単純な cwd の問題を切り分けるため、存在する directory で次も確認した:

```bash
codex --no-daemon sandbox -P eval \
  -c 'default_permissions="eval"' \
  -c 'permissions.eval.file_system={"/"="read", "/tmp"="write"}' \
  -c 'permissions.eval.network.enabled=false' \
  -C /workspace/eval-evidence/canary-work true
```

非機密エラー:

```text
error building bubblewrap command:
app-server socket directory must be a user-owned directory with mode 0700
```

この shell 実行境界から見た `/tmp/codex-daemon-1000` は user-owned だが mode 000。
外側の managed sandbox の mount 設定には同 directory の遮蔽があり、単に cwd を直す問題ではない。
通常の `--no-daemon` でも同じエラー。standalone bwrap も uid map read-only error であった。
保護された directory の chmod・mount変更・本セッションの daemon socketへの接続は行わない。

必要なのは、**nested Codex sandbox を正式にサポートする runtime / 実行方法**である。
環境提供元が eval 用子プロセスに所有者・modeの整った専用 runtime directory を提供するか、
対応済み環境で同じ canary を実行する必要がある。現在のツールから変更可能な正式な設定項目は確認できない。
従って「ユーザーが特定の既存UI項目を切り替えれば直る」とは案内できない。
ネットワーク許可だけではこの制約は解消しない。sandbox を外すことや、外側の保護directoryを公開することは提案しない。

最初の CLI probe には `Read-only file system` による in-process app-server 初期化失敗もあった。
`sqlite_home` / `log_dir` を task directory へ向けただけでは未解消。
接続 probe 時だけの一時的な `.codex` 書込み許可で初期化は進んだが、恒久の権限変更は行っていない。
実稼働 runtime には、既存認証を安全に利用しつつ CLI の一時状態を書ける正式な経路も必要である。
認証ファイルを成果物へコピーしたり、新しい CODEX_HOME に資格情報を移す対応は行わない。

## 基盤側の補完と残る不可観測

| 項目 | 基盤側の実装 | 実環境の観測限界 |
|---|---|---|
| renderer不在 | browser群・image generation・view_image・shell群の無効化要求と `features list` の実値検査 | このruntimeは `unified_exec=false` を指定しても true。全除去を確認できず fail-closed。初回成功hostではserver側の別toolもないことを確認する必要あり |
| 子の設定・選択 | `collabAgentToolCall` の requested と `subAgentActivity(kind=started)` の resolved を別に抽出し、出典eventを保持 | CLIが該当eventを公開しなければ不明。resolved at creation は物理的backendモデルの証明ではない |
| 親の設定 | runtime settings と provider `response.completed` の返却model/effortを別に扱う | settingsや要求値だけなら effective はnull。現在の実接続はresponse未取得 |
| 配布物・依存参照 | exact cat の成功出力全文が固定ファイルと一致したときだけ hash / path / event位置を保持 | readタグ、catalog登録、model自己申告だけではロード済み扱いしない。全文が見えても意味遵守や全依存ロード完了は証明しない |

ローカル生成した Codex app-server v2 schema では、`collabAgentToolCall.model` は requested、
`subAgentActivity.model` は resolved at creation、`commandActions` は best-effort と明記されている。
この区別に沿って decoder を実装した。schemaを生成する操作はネットワーク・推論を必要としない。

```bash
codex app-server generate-json-schema --experimental --out /workspace/eval-evidence/protocol-schema
codex features list -c 'features.unified_exec=false' -c 'features.view_image=false'
```

全ケースの再実行はまだ許可・隔離の前提を満たさない。旧roundを保存し、コード・rubric更新後は新roundをfreezeする。
親QAで見つかった prepared-only comparison の欠陥は、未実行と破損した実行証拠を区別して修正した。
test-report-failure の共通期待は topology 観測に限定し、assertion識別力の診断は v7.4.0 / v7.5.0 の観測へ分離した。
この変更理由は実応答に合わせた期待値変更ではなく、固定版定義への整合である。
