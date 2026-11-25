# CLI execution probe, 2026-11-25

Codex CLI 0.172.0-alpha.2. Existing `codex login status` reported `Logged in using ChatGPT`. No authentication files or secret values were read or changed by the evaluator.

Executed:

```bash
codex exec --ignore-user-config --ephemeral --json -s read-only \
  -m gpt-6.1-sol -c 'model_reasoning_effort="medium"' \
  -c 'sqlite_home="/workspace/eval-407/.local/cli-probe/state"' \
  -c 'log_dir="/workspace/eval-407/.local/cli-probe/logs"' \
  -C /tmp --skip-git-repo-check 'Reply with READY only. Do not use tools.'
```

Exit 1 before model inference: `failed to initialize in-process app-server client: Read-only file system (os error 30)`. The state/log overrides did not solve initialization. stdout contains no model response. Requested model availability, resolved/effective settings, model transport and actual tool execution remain unverified. Authentication status alone does not establish model access.

A metadata-only strace diagnostic repeated the same initialization failure; the selected mkdir/openat trace did not locate a failing path. The exact internal read-only path remains unknown. No sandbox bypass, chmod, authentication copy, new login or alternate model was used. Existing runner uses the same nested CLI and requires its isolation canary; an infrastructure failure must not be counted as a Skill failure. Eight cells remain prepared, zero model-evaluated. A supported runtime with writable internal CLI state and nested sandbox is required, or parent fresh task execution as previously handed off.
