# Choosing and validating metrics

Choose the smallest set that can answer the optimization question. Define the requested outcome first; diagnostic counters help explain it. A metric becomes a search target only after its boundaries and limitations are understood.

## A metric contract

Record these fields when a measurement controls an acceptance decision:

| Field | Decision it supports |
| --- | --- |
| Operation and completion | Which useful, correct result counts as done; distinguish visible readiness from acknowledgement or durable completion. |
| Unit and direction | Time, useful operations/second, bytes, joules, cost, or another explicit outcome; state lower/higher is better. |
| Workload and denominator | Input shape, size, distribution, arrival pattern, concurrency, and work completed per sample. |
| Environment | Source identity, runtime/version, flags, hardware, power state, resource limits, and relevant external dependency behavior. |
| Aggregation | Per-operation samples, percentiles, total batch time, or normalized counters; retain raw data and failures. |
| Decision method | Noise estimate, repetition plan, meaningful threshold, confidence/uncertainty method, and stopping rule. |
| Constraints | Required semantics and agreed limits for memory, errors, freshness, energy, cost, quality, and other affected outcomes. |
| Evidence | Commands, raw artifacts, instrument version/settings, known blind spots, and validation against the requested outcome. |

Choose a threshold that exceeds ordinary drift and matters to the user. Do not invent arbitrary statistical precision or resource limits. If no meaningful difference can be resolved within the available budget, report the result as inconclusive.

An improvement for a lower-is-better outcome is (baseline - candidate) / baseline. A speedup factor is baseline / candidate; a 3x factor corresponds to roughly 67% less time, not 300% less time. For higher-is-better outcomes use the matching direction. State what statistic was compared; ratios of p95 measurements do not describe every request or every user.

## Adapt to the project

| Surface | Outcome candidates | Diagnostic candidates | Behavior to protect |
| --- | --- | --- | --- |
| Web / desktop UI | Trigger to usable interaction; acknowledgement/persistence latency; interaction latency; frame-stall distribution | Main-thread tasks, rendering phases, React commits, DOM mutations, style/layout work, allocation, network critical path | Input and IME handoff, Unicode, fresh cross-session state, late hydration, refresh immediately after submission, reconnect, ordering, error feedback |
| Service / database | Latency distribution at stated arrival rate; successful throughput under latency/error constraints; resource cost per useful operation | Queue time, critical spans, query plans, lock wait, cache hit/miss, retries, allocation, bytes transferred | Correct results, concurrency, isolation, cancellation, deadlines, deduplication where required, cache invalidation, restart/recovery and shutdown |
| CLI / compiler / build | End-to-end elapsed time, peak memory, output size, energy/cost; cold and incremental cases separately | Phase timings, process startup, filesystem work, parsing/IR passes, allocations, machine instruction counts | Output semantics, diagnostics, exit codes, debug/build variants, dependency changes and reproducibility where required |
| Native CPU / GPU / numeric | Completed-job latency, useful throughput, resource/energy use, validated numerical quality | Hardware counters, allocation, cache/branch behavior, device events, transfers, occupancy, synchronization | Numeric tolerances and edge inputs, aliasing, ordering, races, actual work completion, device memory limits |
| Realtime audio / deadline work | Missed deadlines or stream errors per stated exposure; correct output delivered on time | Callback entry/exit, ready-to-start delay, cycle/graph timing, lock wait, lost events | Fixed latency/buffering, output quality, timely state changes, bounded thread work, safe object lifetime and reclamation |
| Data / batch / ML pipelines | End-to-end time or cost at fixed output quality and workload; memory; useful records processed | Stage timing, serialization, I/O, batching, transfers, cache behavior | Completeness, determinism where required, schema/format, held-out quality, no dropped failures or altered accuracy targets |

Do not infer a library or runtime's current behavior from a familiar name. Read local source and relevant primary documentation before choosing version-sensitive flags, counters, or APIs.

## Validate proxies and their failure modes

- **Machine instruction counts:** Valgrind/Cachegrind `Ir` counts executed machine instructions, including measured engine/runtime code. It is not a JavaScript statement or bytecode count. A single-run count comparison is appropriate only after reproducibility is demonstrated. Pin the workload and runtime. Check representative execution without instrumentation, especially if predictability flags alter scheduling, compilation, or GC.
- **Calls and commits:** JavaScript function calls, React commits, HTTP requests, queries, and DOM mutations are different events. Fewer events can mean batching, cheaper code, lost work, or stale output. Inspect the critical path and verify useful completion before declaring a win.
- **Cache metrics:** Hit rate, fewer fetches, and stable layouts do not prove state is current. Define permitted staleness and invalidation/reconciliation behavior. Exercise update, deletion, failure, concurrent sessions, and reconnect as appropriate. The goal is correct state with less unnecessary work.
- **Layout shifts:** Separate unwanted loading movement from movement required to show legitimate changed data. A stable-but-wrong UI fails correctness. Measure both stability and freshness; adjust an overbroad zero-movement assertion rather than suppressing new data.
- **Frame rates:** Artificial begin-frame timestamps control scheduling. They do not prove real-time work finishes before the display deadline. Measure elapsed frame work, presentation/dropped frames on the intended device when needed, and input responsiveness. Browser/rendering overhead consumes part of the total frame interval.
- **String representation:** V8 can use one-byte Latin-1 or two-byte storage; slices can retain their parent's representation. Copying eligible substrings can narrow storage, but must preserve characters outside Latin-1. Benchmark the actual parser/regex workload with representative Unicode, not only ASCII.
- **Microbenchmarks:** Use them to locate and explain a cost. Validate an accepted claim at the layer it describes: full operation, real service, representative document, or physical device. A toy scheduler trace cannot establish service concurrency or lifecycle correctness.

Initially label a diagnostic proxy **exploratory**. Promote it to **validated for this workload** only after repeatability and an outcome comparison. Demote it when that relationship breaks or the workload changes. Keep rejected metrics and why they failed in the record when this prevents repeated mistakes.

Use [tools.md](tools.md) to select the artifact for a diagnostic question. Record whether time is executing, CPU-active but stalled, runnable, blocked, transferring, or waiting on a dependency; summed parallel worker time is not the operation's wall time. Separate allocated bytes, live heap, RSS, buffer peaks, and peak temporary storage instead of calling all of them memory usage.

For LLM serving, distinguish time to first token, streamed inter-token latency, average time per output token, full-request latency, output tokens/second, and SLO goodput. Fixed token distributions, arrival process, stop behavior, cache state, and quality checks are needed for a comparable result. Do not substitute one of these metrics for another or assume a throughput benchmark describes interactive latency.

For compiled or preprocessed workloads, pair cold/first-use cost with warm time, lifetime/use count, recompilation/maintenance, and peak resources. A layout or compile step can repay its cost only after enough uses. For storage pruning, retain rows/bytes read and result cardinality beside query time; a lower scan count is diagnostic evidence until the full operation is checked.

For deadline work, measure execution duration separately from late entry and actual deadline success. A nominal cycle interval is not the entire available execution budget. Verify clock domains, graph dependencies, and the runtime's deadline definition; do not treat an estimated next wakeup as a guaranteed device deadline. Preserve missed events and exposure time; zero observed failures is limited by that exposure. When tracing is restricted, use existing bounded application events and accessible server reports, with uncertainty stated. For audio, keep instrumentation and publication/reclamation bounded on the realtime thread; avoid allocation, formatting, I/O, or blocking there. Validate output and state adoption independently of dropout counts. [PipeWire clock semantics](https://docs.pipewire.org/structspa__io__clock.html) and [realtime stream callbacks](https://docs.pipewire.org/page_streams.html) illustrate these constraints; verify the installed runtime before applying them elsewhere.

## Obtain comparable measurements

For timing, establish cold/warm state, repetitions, and sampling units explicitly. Warm up relevant compilation/caches when measuring steady state; retain initialization when measuring startup. Interleave baseline/candidate repetitions or otherwise control drift. Include allocation/GC and asynchronous work that belongs to the operation.

Instrument both revisions equally. Measure instrumentation overhead when material. Use an independent output oracle so the candidate cannot reduce work by changing semantics. Keep representative untuned inputs or hold-out workloads for repeated search. Repeatedly selecting the best observed candidate can overfit noise; confirm the selected candidate with a fresh comparison.

For services, specify load-generator arrival behavior and ensure its capacity is not the bottleneck. A generator that waits for responses may omit the waiting time that users would experience under independent arrivals. Preserve errors/timeouts, saturation, queue buildup, and tail results. For lifecycle-sensitive changes, apply a hard timeout, verify clean shutdown, and account for drained work and resources.

For asynchronous CPU/GPU work, timing enqueue alone measures dispatch rather than completion. Include the relevant synchronization and transfer boundaries. Treat a simulator and a real device as separate environments.

When useful metrics disagree, inspect the reason. A lower counter with worse required latency is a failed latency candidate. A faster operation that breaches a required memory, quality, or freshness limit fails acceptance. If the user authorizes a tradeoff, record the new acceptance contract before selecting a winner; do not rewrite the contract after seeing an inconvenient score.

## Rank the next experiment

Use rough expected impact and cost, not false precision. Prioritize removable critical-path cost, frequent work, severe tails, and high-confidence causes. A phase occupying 1% of the operation cannot explain a large end-to-end speedup without another effect; investigate that mismatch.

After a win, reprofile. When small changes plateau, test a distinct approach such as representation, dependency order, incremental work, or an algorithm. Retain the best verified candidate and original comparison, rather than stacking unverified edits.
