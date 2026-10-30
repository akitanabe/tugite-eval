# Round013 — structural correction, final SHA待ち

[修正理由と判定](README.md)、[preregistration](preregistration.json)、[corpus](corpus.json)。
新candidate未提供。packet/index/snapshotは作らない。012のfixture/中立prompt/reportingを保持したまま、
表示されたフロー自体が追跡可能である正の構造観測を追加した。事実忠実性とは別に判定する。

source引用を最終SHAで解決後、既存helperでseparated/mixedを各1packetだけ生成する。
新候補outputを見て基準を合わせない。旧012を含め全履歴/元judgmentを保存する。
親報告の012 PASS撤回は本登録へ追記した歴史状態であり、新しい実行結果ではない。

独立judgeにはcalibration.jsonを事前校正用として渡せる。prose-only fragmentsは事実Passでも構造Fail、
structured separated/mixedは構造Passとなる境界を確認する。これはexchange sliceの合成校正で全caseの唯一解ではない。
被評価taskにはcorpus/rubric/calibration/Reference/旧結果を渡さず、元の中立promptだけを維持する。

新rubricはrequired_quality_observationsで構造観測を必須にする。
judgeのoutput_quality.result=passは、displayed-execution-structure=passのときだけ記録できる。
accuracy Passや他metricで構造Failを相殺しない。構造評価の意味判断は独立judgeがcodeと表示を読む責務である。
実LLM task起動は親だけ。2case各1回、追加case/説明専用agent/全suite/version/PRは追加しない。
