# #399 structural acceptance correction

親から、旧012のPASSはUserの形式上の指摘と独立監査後に撤回されたとの報告を受領した。
事実として多くの要件が記述されていても、短い経路断片と散在する散文から読者が経路を再構成する必要があり、
Reference A/Bのように主要なコード実行フローそのものが追える表示ではなかった、という評価盲点の修正である。
本準備は旧応答を読んだり旧判断を採点し直したりしない。旧012の入力・出力・元判断はそのまま残し、
本登録に「親報告によるPASS撤回/元判断superseded」を追記して、歴史と現在の受入判断を区別する。

## 正の構造条件

`displayed-execution-structure`を追加し、factual `execution-faithfulness`と分ける。
表示された経路自体から主要節点の順序、必要な呼出しの入れ子/帰属、同一関数内処理、呼出し元へ戻った後の
Cookie発行・応答/終了までの続きが追えることを要求する。この合成fixtureの応答はdictであり、実HTTP送信を捏造しない。
全体像/処理説明の情報が正しいだけでは、この構造条件を満たさない。Readerが複数段落を組み直して経路にする必要があるものはFail。

説明を経路に統合してよく、入れ子・表・図等の適切なlayoutを許す。見出し、矢印、語句、全call、任意の長さを固定しない。
全てのreturnを列挙する要求ではなく、主要経路の続きが途中で切れていないかを見る。
分離実装で委譲先へ入った後のControllerへの復帰を示すことと、混在実装でController内の検証等を
架空のValidator呼出しへ変換しないことを、同じ忠実性/構造の観点で確認する。

## 回帰確認と集計

calibration.jsonは**judgeだけ**の合成校正例であり、LLMの実応答・模範解答・評価taskの入力ではない。
同じexchange主要経路の事実を散文断片で述べるnegativeと、構造表示するpositiveを分離/混在で用意した。
校正は構造観測だけのsliceで、これだけで全caseの全体像/全経路が合格したとは扱わない。
事実正確さは両方Passでも、構造はnegative Fail/positive Passとなることを確認する。
表と入れ子の別layoutを使い、fence/矢印の有無を判定器にしない。意味判断は人がcodeと表示を読む責務のままである。

機械testは校正dataの組合せ保持と、構造Fail/不明を事実Passで相殺して総合PASSにできない受入gateを確認する。
文章を採点するparserやregexは追加しない。`required_quality_observations`で新構造観測を必須化し、
独立judgeがoutput_quality.result=passとしながら必須観測がpassでない矛盾をadjudicateで拒否する。
旧roundにはこのfieldを追加せず、旧judgmentを自動変更しない。

## 待機範囲

fixtures・中立prompt・reporting・旧factual観測は012と同一。新観測と受入gateのみ追加。
rubric/calibration/Referenceを被評価promptへ注入しない。新candidateは未提供、packet/snapshot/LLM評価は作らない。
2case各1回のみを親が起動する。追加case・説明専用agent・全suite・version/PRは自動追加しない。
