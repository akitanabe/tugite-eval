# Evaluation results

## Scope and current status

The primary question is whether observable output/artifact quality is maintained. This is not a complete audit of internal operations. Requested model: `gpt-6.1-sol`, effort `medium`; effective runtime settings remain unknown where unavailable.

Evaluation code is fixed at `19f0126119a59c93ea5acf2eac31bbf603f99cab`. Inputs and expectations were frozen before the corresponding runs. The early bootstrap pilot is excluded.

## Normal cases: completed quality review

| Skill | Versions / trials | Output quality | Report |
|---|---|---|---|
| test-report | v7.3.7, v7.4.0, v7.5.0; 3 each | 9 PASS | [Responses and judgments](cloud-normal-002/test-report-normal.json) |
| test-verify | same; 3 each | 9 PASS | [Tests, responses and judgments](cloud-normal-002/test-verify-normal.json) |
| impl-lead | same; 3 each | 9 PASS | [README changes and judgments](cloud-normal-002/impl-lead-normal.json) |
| visualize-that | same; 3 each | 9 PASS | [HTML and judgments](cloud-normal-002/visualize-that-normal.json) |
| explain-this, review-propose, impl-plan, impl-review | v7.5.0; 1 each | 4 PASS | [New-skill attainment](cloud-normal-002/new-skill-attainment.json) |

No material output-quality deterioration was observed in these 40 normal-case outputs. This conclusion is limited to the small, synthetic fixtures used; it does not establish general equivalence, model superiority, or causal effects of a version change.

Separate observable scope deviations were recorded for visualize-that: v7.3.7 trial 2 retained a diagnostic log, trial 3 retained screenshots, and v7.4.0 trial 2 retained a diagnostic log despite the case's diagram-only write scope. These are not concealed by output-quality PASS. Rendering was not independently verifiable for every artifact; each report preserves its actual visual/static evidence and limitations.

## Remaining scope

Boundary, failure and ambiguous cases are being evaluated separately using [cloud-nonnormal-003](../rounds/cloud-nonnormal-003/README.md). Of 48 version-specific cells, 43 are prepared; [five are not supported](../rounds/cloud-nonnormal-003/BLOCKED.md) because the cloud adapter cannot reliably enforce the specified absence of a renderer or reviewer. They are not counted as Skill failures.

A single nonnormal observation is not enough to claim a significant regression. Suspected differences require comparison with the applicable version specification and, where appropriate, repeated trials. Hidden internal activity, effective-model identity, and complete isolation are not inferred from self-reports.
