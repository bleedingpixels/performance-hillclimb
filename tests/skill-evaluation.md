# Evaluate the skill's decision support

Use planning evaluations alongside installer tests when changing this skill. A useful plan chooses an observable question, an appropriate artifact, a discriminating experiment, and an acceptance boundary. This evaluates guidance and retrieval, not application speed. Actual performance claims require a measured baseline and candidate in the target project.

## Fixed comparison protocol

1. Freeze the accepted baseline and candidate bundles before evaluation. Record their revision identities and the exact scenario text. Keep the initial four scenarios unchanged between versions.
2. Give each version a fresh agent context with the same model, effort, tools, prompt, and 2,000-word response limit. Permit reading only the selected bundle and scenarios. Prohibit browsing, profiling, implementation, and invented measurements. Ask agents to distinguish bundle-supported advice from prior knowledge.
3. Have a separate grader inspect both responses and necessary bundle citations using the rubric below. Evaluate decision quality separately from source grounding. Retain unsuccessful responses and the complete score table. For stronger evidence, repeat with pinned model versions and independent graders; randomize or blind version labels where practical.
4. Accept the candidate only if it has no correctness-critical zero, its causal/tool/experiment subtotal does not fall, and its source-grounding subtotal improves. A failed comparison identifies a specific guidance gap to revise and confirm in a fresh context; do not silently change the scenarios or scoring rule to obtain a win.
5. Check a separate domain with real constraints such as unavailable tools, fixed latency, or a numerical contract. Label whether the scenario was withheld from authors, generated after the revision, or reused for confirmation. Keep installation and privacy checks separate from planning scores.

Scoring for each scenario, with four dimensions worth 0–2 points each:

| Dimension | 0 | 1 | 2 |
| --- | --- | --- | --- |
| Causal model | Misleading or unsupported cause | Plausible but undifferentiated | Separates competing causes and gives a discriminating observation |
| Tool/artifact fit | Cannot answer the question or incompatible environment | Broadly useful profiler | Tool and artifact match the suspected time/resource domain, with a relevant blind spot or fallback |
| Experiment/guardrails | Accepts a proxy or semantic regression | General A/B and correctness advice | Controlled representative comparison, concrete guardrail/tradeoff, and claim boundary |
| Source grounding | Inaccurate source claim | Correct broad principles or labelled prior knowledge | Relevant bundle case/tool reference used accurately with its workload/evidence limit |

The maximum is 32 points across four scenarios. The decision-quality subtotal is the first three dimensions, with a maximum of 24; grounding has a maximum of 8. These are ordinal assessments, not interval measurements of skill quality.

## Fixed scenario prompt

For each scenario, give a concise diagnosis/hypothesis, first tool and artifact to obtain, one discriminating experiment with an acceptance rule, correctness/resource guardrails, and the scope of any claim. Assume permission for local investigation but no deployment or infrastructure spending. No new data can be acquired during this evaluation. Use the supplied skill and relevant references; distinguish bundle-supported advice from your own prior knowledge. Do not browse, run profilers, or invent measurements.

1. A Go HTTP service's p99 latency doubled after a change, while its p50 and average CPU utilization barely moved. Its existing CPU flame graph contains no dominant new hot function. The production workload has bursts and mixed request types. A proposed patch adds more workers.
2. A batch SQL workload reads remote Parquet. Engineers want to sort the data on ingest to speed repeated queries with two filter columns. Their small local benchmark looks faster. Ingest frequency, selectivity, storage latency, and total read/write cost matter; arbitrary input rows may tie on the sort key.
3. A GPU inference path has a timeline with many short kernels, visible host gaps between launches, and a large repeated host-to-device copy. A team member proposes optimizing one kernel's arithmetic or quantizing the model. There are both NVIDIA and AMD deployments, and existing quality/latency budgets must be preserved.
4. A JSON serialization benchmark improves on repeated plain-object inputs, but the application uses Unicode strings, optional getters, mixed object shapes, and a cycle-error path. The proposal claims a universal 2x app speedup from a lower instruction count under a predictability flag.

## Research iteration result, 2026-10-05

Compared baseline revision `47871d6b0fb9c43b084438d1b0f4f2cbec4a1979` with the integrated research revision `c1705c6aa9b5`. One fresh response was produced per version with the same inherited model and effort, followed by a separate agent grader using the preselected rubric. There were no profiling or benchmark runs. This was a small, unblinded check; the model version was not pinned in the public artifact. It is not a statistical efficacy study.

| Scenario | Baseline decision / 6 | Revised decision / 6 | Baseline grounding / 2 | Revised grounding / 2 |
| --- | ---: | ---: | ---: | ---: |
| Go tail regression | 6 | 6 | 1 | 2 |
| Remote Parquet | 6 | 6 | 1 | 2 |
| GPU inference | 6 | 6 | 1 | 2 |
| JSON serialization | 6 | 6 | 2 | 2 |
| **Total** | **24/24** | **24/24** | **5/8** | **8/8** |

Overall totals were **29/32 → 32/32**, with no zero scores. Both reports already made sound decisions under this rubric. The revision improved task-specific bundle grounding for Go waiting/queues, SQL pruning and lifetime cost, and host/device inference. The baseline already grounded its JSON instruction-count and runtime-flag caveats well. The result supports better reference coverage in this sample; it does not demonstrate better decisions, faster agents, faster software, or general superiority.

The baseline's specialized tools/mechanisms in the first three cases were explicitly labelled prior knowledge. The revised report used the new tool/case/strategy references accurately, including Go waiter-versus-holder semantics, SQL scan/ingest tradeoffs, GPU replay and completion boundaries, and scoped V8 fast paths. Both preserved correctness, resource limits, and inconclusive outcomes. The evaluated revision precedes the separate deadline refinement below.

## Additional domain and refinement

A separate evaluator chose a synthetic live C++ audio case outside the four domains, after the initial revision. The scenario was not supplied to the skill authors beforehand. It prohibited privileged tracing or process attachment, extra buffering, altered sample rate, and changed sound quality. It supplied a bounded application event ring, an offline renderer, a preset script, and accessible PipeWire xrun reports; expected cycle-deadline fields were absent. Its illustrative timing and error numbers were invented evaluation inputs, not measurements.

The plan selected the existing event export and server reports, separated graph-lock blocking from DSP cost and late scheduling, and protected preset timing, crossfades, graph lifetime, and bounded reclamation. It recognized that callback duration and offline rendering cannot establish live deadline reliability. It also identified a coverage gap: the bundle lacked a concrete deadline-work example and realtime instrumentation constraints.

The refinement adds those distinctions to the metric and tool guides, grounded in primary PipeWire documentation. Callback execution, ready-to-start delay, and deadline failure are separate observations. Driver and follower WAIT fields have different meanings; ERR combines xruns and other errors. Estimated next wakeup is not a guaranteed hardware deadline. Instrumentation and publication/reclamation on the realtime thread must remain bounded.

A fresh-context confirmation on this now-known audio case correctly distinguished execution, late entry, and cycle success; interpreted both WAIT fields and the mixed ERR counter; chose the restricted-tool fallback; and preserved output/state/lifetime checks. No blocking case-level guidance gap remained, while installed-runtime timing and actual deadline-field validation stayed application-specific. This is separate from the four-case score and is not another unseen holdout. Actual dropout improvement, physical-device performance, and runtime correctness remain unmeasured.

## Other required gates

- Run the isolated installer suite, including unchanged seven-file managed bundle upgrades, refusal to replace local edits or foreign layouts, preflight across all targets, and rollback failures.
- Validate the skill structure and referenced relative files. Keep specialized guidance in optional references rather than requiring every task to load every tool and case.
- Inspect public file content and all history being published for identifying data and secrets; a scanner must fail on missing scope, unreadable objects, or unexpected files. Do not publish local evaluation logs or harness/session metadata as test evidence.
- Verify an actual global update against source hashes when changing the managed bundle. Separate successful file installation from native harness discovery and hosted-environment availability.
