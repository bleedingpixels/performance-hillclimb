---
name: performance-hillclimb
description: Discover useful performance metrics, validate benchmarks, and iteratively optimize software while preserving correctness and resource constraints. Use for performance investigations, metric design, regression guards, or repeated optimization across applications, services, tools, and CPU/GPU workloads.
---

# Performance Hill Climb

Turn a vague performance problem into a measured optimization loop. Adapt the workload, instruments, and acceptance criteria to the project. The deliverable is an improved outcome with traceable evidence, or a precise account of what remains unproven.

The workflow uses ordinary files and project commands. It does not require a particular provider, agent framework, telemetry service, or language. Follow the project's own measurement and verification tools when available.

Use the harness's available file-reading, editing, and command tools; tool names are not part of the procedure. Resolve the links below relative to the directory containing this `SKILL.md`, even when the project checkout or current working directory is elsewhere. Keep the complete skill folder together when moving it.

For global discovery, explicit activation, custom installation directories, or a harness without a skill loader, read [references/portability.md](references/portability.md). The optional installer requires Python 3.9 or newer; following the optimization workflow does not.

## Start with a bounded outcome

Read the project instructions and inspect the selected checkout, existing changes, runtime, tests, and available evidence before editing. Preserve unrelated work. Identify the operation the user wants improved, its meaningful completion condition, and the permitted change surface.

Use the user's resource/time budget. Otherwise choose and state a bounded investigation appropriate to the task; complete useful local work within it. Do not interpret this skill as permission to deploy, publish, spend on infrastructure, or run a perpetual job. Respect an explicitly read-only request.

Choose the entry point:

- **Discover:** the bottleneck or measurement is unclear. Produce a reproducible baseline, candidate metrics, and a ranked experiment backlog. Continue into implementation when the request already authorizes it.
- **Optimize:** a useful benchmark exists. Verify its definition and baseline, then run the candidate loop.
- **Guard or resume:** preserve a verified gain or continue an existing campaign. Recover its exact source, workload, and evidence before rerunning or changing ceilings.

Keep one compact campaign record in the project's existing artifact location, or a clearly named temporary directory when none exists. Do not scatter logs throughout the checkout or overwrite protected evidence. Use [assets/experiment-record.md](assets/experiment-record.md) as an adaptable record format, not a required extra document for every tiny edit.

## Discover measurements that matter

1. Trace the actual operation from its trigger to a correct result. Separate critical-path execution, waiting, initialization, rendering, background work, and persistence. A ready-looking interface is not automatically a completed operation.
2. Rank expensive or frequent paths by user impact, frequency, tail severity, estimated removable cost, and implementation complexity. Measurements can expose another bottleneck; revisit this ranking as evidence changes.
3. Define an **outcome metric** for the requested improvement, a small set of **diagnostic metrics** that explain cost, and **correctness/resource guardrails**. A counter may be the primary outcome if the user explicitly wants to reduce that counter; do not relabel it as a latency win.
4. Specify each metric's unit, direction, trigger/completion boundary, workload and denominator, runtime conditions, aggregation, noise, and raw evidence location. Separate cold/warm paths and materially different cohorts. Record failures and timeouts rather than dropping them from fast-success averages.
5. Inspect existing traces first. Add the smallest useful instrumentation or benchmark where a blind spot prevents a decision. Account for instrumentation overhead and use the same instrumentation on both sides.

Read [references/metrics.md](references/metrics.md) when choosing instruments, adapting to a new runtime, or interpreting an uncertain counter. Its examples are candidates, not a checklist to collect every possible metric.

Select an instrument by the question it can answer. A CPU profile cannot explain every blocked request, an allocation profile is not retained heap or RSS, and a GPU kernel counter is not a host/device timeline. Check the actual OS/device, runtime, symbols, permissions, and collection overhead. Use [references/tools.md](references/tools.md) for task-to-tool routing and interpretation limits; unavailable counters are a reason to use an accessible timer/trace and narrow the claim.

For rendering or XR, use [references/graphics.md](references/graphics.md) to establish a visual-quality contract and separate coverage, texture/shader, and temporal aliasing. A faster or smoother-looking still image cannot establish preserved detail, stereo consistency, or stability under motion; keep those requirements beside frame/resource budgets.

Form a bottleneck model before editing: unnecessary work, algorithm cost, locality/bandwidth, allocation/GC, contention/queues, transfer/launch overhead, or compilation/startup. Identify the affected phase's critical-path share and the workload conditions where the model should fail. Low average utilization does not rule out bursts, a saturated thread, or a slow cohort.

## Qualify the benchmark before climbing

Run the unchanged baseline enough times to estimate variability and to verify that the benchmark exercises the intended work. Preserve raw samples. Use stable workload seeds and equivalent environments; alternate or randomize baseline/candidate runs when drift is material.

Choose a stopping rule and a meaningful improvement threshold before evaluating candidates. For noisy timing, use repeated independent runs and an appropriate comparison interval or statistical method. Do not stop sampling only when a favorable result appears. An exact count still needs demonstrated repeatability.

For a diagnostic proxy, perform a small controlled change and measure both proxy and outcome on representative inputs. Record the conditions where they move together or disagree. A correlation on one hot path is provisional evidence, not a universal contract. Retire or revise a proxy that stops tracking the outcome.

Before optimization, establish the relevant behavior checks. Add missing checks for the behavior a proposed change could break, using an independent expected result or oracle. Do not weaken assertions, remove work, change input mix, or narrow the completion boundary to make the score improve. Fix an invalid harness and rebaseline both sides before interpreting its numbers.

Compare profiles with equivalent work and compatible units/modes. Retain absolute cost per completed operation when a normalized view might conceal growth. Separate profiling runs from ordinary outcome measurements; trace collection, predictable runtimes, replay, and retained shape/stack information can change execution.

Include costs outside the hot interval when the operation requires them. Preprocessing, compilation, cache population, and offload can move cost to startup, maintenance, memory, or another device. Evaluate repayment over the expected lifetime and separate cold/warm cases; test services at the intended arrival process with dropped work and generator capacity accounted for.

## Run the candidate loop

Repeat while authorized scope, useful opportunities, and the budget remain:

1. **Hypothesize.** Name the suspected cause, supporting trace, proposed change, expected outcome, protected behavior, and plausible regressions. Label unknown causes as hypotheses.
2. **Change.** Make the smallest coherent implementation change that tests the hypothesis. Prefer eliminating unnecessary work before adding caches or coordination. Architectural changes are valid when evidence supports them; compare the complete resulting behavior.
3. **Check.** Verify correctness, then compare against the same accepted baseline using equivalent workloads and settings. Include relevant adverse cases and at least one representative case not used to tune the candidate when overfitting is plausible.
4. **Decide.** Accept a candidate only when its evidence meets the chosen outcome threshold and all required guardrails. A lower proxy with worse latency, stale state, changed semantics, or a breached memory limit is not an accepted latency optimization. A valid tradeoff needs an explicit rationale within the user's priorities.
5. **Record.** Keep the exact change identity, commands, raw samples, results, and accept/reject/inconclusive decision. Restore only your rejected changes; preserve shared or unrelated edits. An inconclusive run should improve measurement or remain unproven, not trigger a favorable ceiling update.
6. **Reprofile.** Confirm which bottleneck remains after an accepted change. Promote that revision to the next baseline and preserve the original baseline for cumulative comparisons. Probe a different approach when a local optimum or diminishing returns makes small tweaks unproductive.

Useful candidate families include removing duplicate work, changing data layout or algorithms, avoiding repeated serialization or allocation, narrowing invalidation, incremental computation, batching, reordering critical-path dependencies, and moving eligible work off a constrained thread. Caching, prefetching, parallelism, and deferral require explicit correctness and resource checks; none is automatically faster.

Read [references/strategies.md](references/strategies.md) to choose among mechanisms, bound potential benefit, or escape a plateau. Use [references/case-studies.md](references/case-studies.md) for recent open-source hypotheses and counterexamples, loading only relevant cases. Distinguish a published result, released implementation, moving source branch, and local replication. Transfer the mechanism and test its assumptions; do not transfer a headline percentage.

Try a broad mechanism before a large parameter sweep. Preserve losing cohorts and use representative untuned inputs or a fresh confirmation run after selecting a winner. For interacting changes, compare the integrated result and retain a separate comparison or ablation when needed to identify the cause. Approximate math and quantization need an explicit quality contract; an implementation speedup and an accuracy tradeoff are separate candidates.

For independent bottlenecks, parallelize only when delegation is available and appropriate. Give each worker a narrow metric/workload, file ownership, budget, and guardrails. Separate edits or use isolated worktrees. Do not run competing timed benchmarks on the same constrained machine. Validate the integrated result because isolated improvements can interfere.

## Preserve wins without freezing mistakes

Add a regression guard only after the outcome gain and measurement reliability are established. Keep correctness checks beside performance checks. Ratchet validated deterministic ceilings; use tolerances, repeated comparisons, or scheduled runs for noisy timing.

Version ceilings with the workload, metric definition, runtime, and relevant hardware configuration. When these change, rerun old and new code under the new harness; do not silently carry across or relax a ceiling. If the old baseline cannot run, label the new baseline incomparable. A diagnostic ceiling may increase when an authorized change improves the actual outcome and its tradeoff is documented.

Local verification does not establish production impact. When deployment or physical-device evaluation is authorized, use the project's existing rollout controls, inspect field or device evidence, and stop a rollout that violates required guardrails. Otherwise deliver the local improvement with that remaining boundary explicit. Clean up temporary flags through the project's normal process after they have served their purpose.

## Finish or hand off with evidence

Report the improved operation and exact comparison, why the change affects it, the checks actually run, and the scope of proof. Include:

- Baseline/candidate identities, workload, environment, and raw result paths.
- Outcome change with appropriate uncertainty; diagnostic changes separately.
- Guardrail results, rejected approaches that inform the next decision, and material tradeoffs.
- Status: **verified in the measured environment**, **partial**, **inconclusive**, or **blocked**, with the specific remaining boundary.
- The next useful experiment if the budget or available evidence ends before the objective is established.

Do not generalize a percentile to all users, simulated frame scheduling to real throughput, a microbenchmark to the full service, or a green scoped test to full parity. If work continues later, leave a checkpoint that names the accepted source, remaining hypotheses, measurement contract, commands, and first resume action.

Read [references/sources.md](references/sources.md) when explaining this skill's origin or checking the source-specific caveats.
