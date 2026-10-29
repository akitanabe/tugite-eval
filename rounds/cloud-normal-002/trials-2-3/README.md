# Continuing normal cells: trial 2/3

継続4 Skill × 固定3版 × trial 2/3 = 24入力。同一round/specから既存runnerのprepare/exportで作成した。
trial 1との差はinput内の `attempt_id` / `trial` のみ。fixture、prompt、配布物hash、要求model/effort、rubric、round sealは同じ。
この追加はGit保存する評価入力とprepared metadataだけで、評価runnerの機能・既存protocolは変更しない。
実評価はここでは起動していない。結果を読んで期待値を作り直していない。

- Round: `e7da77d4-bb42-4965-a8a0-6945b5c62f61`
- Eval code revision: `19f0126119a59c93ea5acf2eac31bbf603f99cab`
- Required requested baseline: `gpt-6.1-sol / medium`
- Quality protocol SHA-256: `1f63eb00f44e527aaea2393c43d4daa739001b5daff6b89bb52cef38895e1513`
- Human-readable list: [INPUTS.md](INPUTS.md)
- Machine-readable path/hash/case/version/trial/attempt list: [index.json](index.json)

## 子taskへの入力取得

評価codeを19f0126に固定したまま、追加入力だけをこの追加のdata commitから取得できる。
親は最終handoffの完全data SHAを `<DATA_SHA>` に、indexから選んだpath/hashを対応するplaceholderへ入れる。
新規taskでrepository URL/cwd/origin/cleanを確認し、各Gitコマンドの成功を逐次確認する。force/reset/cleanは使わない。

```bash
git fetch --no-tags https://github.com/akitanabe/tugite-eval.git <DATA_SHA>
git cat-file -e 19f0126119a59c93ea5acf2eac31bbf603f99cab^{commit}
git checkout --detach 19f0126119a59c93ea5acf2eac31bbf603f99cab
git rev-parse HEAD
# 上記HEAD一致を確認してから、単一inputだけを取得する。
git show <DATA_SHA>:<INPUT_PATH_FROM_INDEX> > /workspace/trial-input.json
python3 evals/cloud_task.py stage /workspace/trial-input.json <INPUT_SHA256_FROM_INDEX> /workspace/quality-stage
```

続いて固定prompt/Skillを読んで実行し、既存 `collect --quality` で回収する。
評価agentへcontrolやprepared metadataを読ませない。
評価code SHAは19f0126、input data SHAはこの追加commitとして親の受領記録で区別する。
新data checkoutをそのまま使う場合も、runner/adapterのbytesは19f0126と同一であるが、実際のcheckout SHAを正確に記録する。

## 親roundへのprepared metadata追加

元のsnapshotはtrial 1だけを保持するため、この追加にはtrial 2/3の4つのprepared入力ファイルを別保存した。
既存の親roundを使うか、既存restoreでfresh roundを作ってから、以下の手順で追加する。実行結果・裁定はコピーしない。
親のGit checkoutはこのdata commitを含むものを使う。code bytesは19f0126と同じ。

```python
from pathlib import Path
import hashlib
import json
import shutil
import sys
sys.path.insert(0, str(Path('evals').resolve()))
import runner as r
import cloud_receipt as receipts

supplement = Path('rounds/cloud-normal-002/trials-2-3')
parent_round = Path('.local/quality-normal').resolve()  # 親の実際のroundへ置換
receipts.verify_tree(supplement, 'supplement-seal.json')
index = json.loads((supplement / 'index.json').read_text())
assert r.verify_round(parent_round)['round_id'] == index['round_id']
assert hashlib.sha256((parent_round / 'spec.json').read_bytes()).hexdigest() == index['spec_sha256']
entries = list((supplement / 'attempts').iterdir())
assert all(not (parent_round / 'attempts' / entry.name).exists() for entry in entries), '既存attemptを上書きしない'
for entry in entries:
    destination = parent_round / 'attempts' / entry.name
    shutil.copytree(entry, destination)
    r.verify_attempt(parent_round, destination)
```

その後、各input/resultを既存quality-importに渡し、別contextで独立評価する。
品質protocolの既存indexはcase/version登録を持ち、trial 2/3はこの同じfrozen spec/attemptへ照合できるため、protocol変更は不要。
新規4 Skillの追加試行、trial 4/5、境界/失敗/曖昧の追加はこのdataに含めない。
