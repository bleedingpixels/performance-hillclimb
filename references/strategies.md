# Choose an optimization mechanism

Choose a mechanism from the observed limiting resource. The table suggests experiments, not a fixed ordering or a promise of speed. Source cases are summarized in [case-studies.md](case-studies.md); choose instruments in [tools.md](tools.md).

## Bound the opportunity before editing

Separate executed work, CPU-active memory stalls, runnable delay, blocking, device transfer, and waiting on a dependency. Low average utilization can conceal bursts, a hot single thread, or one slow cohort. Find the part on the requested operation's critical path and its frequency; summed concurrent worker time is not critical-path wall time.

Use a rough upper bound. If a serial phase occupies fraction `f` and improves by factor `s` while everything else stays fixed, the overall speedup is `1 / ((1 - f) + f / s)`. The assumptions fail when the change alters queueing, overlap, or work elsewhere; measure those effects rather than promising the bound. A large local improvement to a small phase may have little visible impact.

Classify the candidate by what it changes: work performed, representation/locality, algorithm, scheduling/coordination, generated code, or accuracy/resource tradeoff. Prefer a change that distinguishes competing causes, and record the conditions that would falsify its rationale.

## Match an experiment to a mechanism

| Evidence / suspected cause | Candidate to test | Discriminating measurement and guardrail |
| --- | --- | --- |
| Repeated enumeration, conversion, parsing, or reconciliation | Remove unnecessary work; narrow invalidation; reuse an already valid result | Count work per completed operation and compare absolute CPU/latency. Check newly required work, invalidation, and error paths. Dolt's catalog fix shows why removing a call can matter more than tuning it. |
| Repeated shape checks or buffer growth | Guard a common fast path; specialize representation; grow segmented output | Measure validation/copying and full output. Exercise mixed shapes, Unicode, callbacks and fallback/errors. V8 preserves a general serializer beside its optimized path. |
| Large scan/decompression cost before useful results | Push down eligible work; prune partitions/row groups; cluster selective dimensions | Inspect actual rows/bytes read and query plan. Compare representative selectivity/filter combinations, read savings, and ingest/maintenance costs. Check result completeness and ties/order only where promised by the interface. |
| Repeated merging, pointer chasing, payload movement, or spills | Change algorithm/data layout; move narrow keys rather than full payloads; tile/batch locality | Sweep size, input order, key/payload width, memory limit, and threads. Track cache/memory and spill evidence plus complete elapsed time. DuckDB's sort rewrite has both wins and a single-thread regression. |
| Allocation churn or pointer-rich live state | Remove intermediates; shrink live graphs; improve locality; evaluate a runtime change separately | Distinguish allocation volume, live heap, RSS, and GC cost. Test lifetimes/ownership, peak memory, and latency. Pools can retain memory and locks; a newer collector cannot fix every representation problem. |
| Lock waits, runnable queues, or serial coordination | Shorten critical sections; separate independent state; batch coordination; adjust bounded concurrency | Collect holder/waiter/task evidence and measure at matched offered load. Sweep concurrency; protect ordering, cancellation, backpressure and memory. More workers can amplify contention or queues. |
| CPU hot path remains after ordinary release optimization | PGO/LTO where supported; post-link code layout; vectorize a suitable operation | Match build/toolchain and train on representative work. Hold out sizes/shapes/cold paths and check generated code/counters. A profile biased to tiny ASCII inputs is not evidence for large Unicode workloads. Code size/build cost and CPU-target compatibility matter. |
| Host gaps, repeated GPU transfers, many tiny launches | Remove/reuse transfer; keep inputs resident; persistent batches; fuse eligible work; graph replay | Inspect host/device timeline and compare launch/transfer costs and completion latency. Check device memory, stream ordering, dynamic shapes, capture restrictions and cancellation. Change one mechanism before tuning a small kernel. |
| A measured GPU execution/memory pipeline is saturated | Tile/layout changes, overlap, fusion, backend autotuning, or supported precision changes | Sweep relevant shapes and actual devices. Validate numerical output/gradients and deterministic requirements against an independent reference. Higher occupancy or peak FLOPs is not automatically lower full-job time. Approximation/quantization needs a separate quality contract. |
| Repeated compilation or graph breaks with expensive startup | Compile reusable regions; reduce graph breaks; bound shape variants and reuse artifacts | Compare cold compilation, first call, warm time, recompilation, memory and process lifetime. Dynamic inputs can invalidate reuse. PyTorch regional compilation illustrates why optimizing cold cost and steady state separately matters. |

## Include costs that a favorable benchmark can hide

For a preprocessing or compilation step, estimate a repayment point: if it costs extra `B` time and saves `d` per use, it needs roughly `B / d` uses to break even when `d > 0`. Include maintenance, cache misses, lifetime, and resource cost when they matter; do not use this simple arithmetic for a changing workload without remeasurement. Storage clustering and regional compilation can benefit long-lived/read-heavy workloads while hurting frequent reloads or short-lived tasks.

Caching, prefetching, offload, approximate math, and quantization can shift cost rather than remove it. Measure freshness/quality and retained or device memory beside latency. Treat a tradeoff as a separate candidate with an agreed contract. The PyTorch case shows that a lower device-memory peak can coincide with much slower inference.

For services, compare offered and achieved arrivals, failures/drops, and tail latency under the same workload. If queues or contention change, a small CPU reduction can have a nonlinear latency effect near saturation; test that hypothesis across load levels. Do not infer the effect from a CPU percentage alone.

## Explore without overfitting the hill

Test broad mechanisms before sweeping dozens of parameters. A small bounded sweep over size, batch, thread count, or tile shape can identify a useful region; preserve every candidate and its guardrails. Stop tuning a proxy that no longer tracks the requested outcome.

Retest the chosen candidate with fresh representative inputs or independent runs. Repeated selection favors noise; a significant result among many comparisons is not sufficient confirmation. Preserve per-cohort regressions alongside any weighted aggregate; workload weights must reflect the intended use rather than the winning result.

After accepting a change, reprofile. When a local plateau persists, change the algorithm, representation, critical-path ordering, or resource model instead of adding small unverified tweaks. Integrate interacting improvements incrementally: two isolated wins can compete for memory/cache/bandwidth or introduce coordination. Keep an ablation or separate comparison when it explains which change produced the outcome.

Treat published results as leads. Reconstruct the method, inspect the released/current code boundary, and measure your own workload. A report's broad lesson may transfer even when its percentage, hardware configuration, or preferred library does not.
