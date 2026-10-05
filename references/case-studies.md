# Recent open-source optimization cases

Primary reports and implementation links checked on 2026-10-05. These are reported results, not benchmarks reproduced by this skill. A release or code link anchors an implementation; it does not establish the exact revision used in a report unless the report says so. Moving branches are identified below. Use the cases to form hypotheses, then measure the selected project.

## Eliminate unnecessary work: Dolt, 2025-06-20

The [Dolt differential-profiling report](https://www.dolthub.com/blog/2025-06-20-go-pprof-diffing/) embeds the relevant fix. Generated system tables made a catalog path over three times slower in one regression suite. A profile difference exposed unnecessary enumeration in `Database.tableInsensitive`; excluding generated tables removed that work. The separate read-benchmark table reports improvements of 0–3.45%, not a universal threefold gain. The exact fix commit was not established here.

**Experiment to transfer:** compare equivalent baseline/candidate CPU profiles and count enumerations per completed query. Remove an unnecessary lookup before optimizing its body. Check system-table visibility, results, and full-query latency. Use pprof's documented comparison semantics rather than blindly copying the report's flags; see [tools.md](tools.md).

## Specialize a safe fast path: V8, 2025-08-04

[V8's JSON serializer report](https://v8.dev/blog/json-stringify) describes V8 13.8 / Chrome 138: an iterative path for side-effect-free data, one-byte/two-byte specialization, reuse of object-shape eligibility, improved number conversion, and segmented output buffers. It reports over twice the speed on JetStream2's `json-stringify-inspector`. [Current serializer code](https://github.com/v8/v8/blob/main/src/json/json-stringifier.cc) is a moving branch, not the report's pinned revision.

**Experiment to transfer:** profile representation checks and buffer copying on real payload shapes; test a guarded common path with a complete fallback. Exercise Unicode, getters, `toJSON`, replacers, formatting, errors, and cycles. Preserve observable semantics. Measure full serialization and the enclosing operation; the serializer benchmark does not imply a twofold application improvement.

## Change work organization and locality: Go, 2025-10-29

The [Green Tea GC report](https://go.dev/blog/greenteagc) describes page-oriented marking and local metadata that reduce irregular access and queue pressure. Reported reductions are 10–40% of **GC CPU cost**, usually around 10%, rather than total application time. It was experimental in Go 1.25 and became default in [Go 1.26](https://go.dev/doc/go1.26#runtime). The [Go 1.26.0 mark loop](https://github.com/golang/go/blob/go1.26.0/src/runtime/mgcmark.go) provides a pinned implementation anchor.

**Experiment to transfer:** distinguish allocation churn, live pointer-rich heaps, and scanning locality. Compare matched runtime builds or one representation change at a time, collecting CPU/request, allocation/live-heap profiles, GC data, and latency. If GC is a small share, bound the possible whole-operation benefit. A lower GC counter alone does not establish improved tail latency. Version-specific experiment switches need local verification.

## Change the algorithm and spill path: DuckDB, 2025-09-24

[DuckDB's v1.4.0 sort report](https://duckdb.org/2025/09/24/sorting-again) links [PR #17584](https://github.com/duckdb/duckdb/pull/17584), merged at commit `4759904`. Static normalized keys, adaptive sorting, paged runs, and a streaming parallel k-way merge reduce interpretation and payload movement. On an M1 Max at ten threads, random billion-integer sort time fell 17.554→6.493 seconds; a spilling TPC-H SF100 case fell 273.982→80.919 seconds. A random 100-million-integer **single-thread** case regressed 3.240→4.234 seconds.

**Experiment to transfer:** sweep input order, key/payload widths, threads, and memory limits. Inspect operator timing, peak buffers/temp storage, and actual result equivalence. The report isolates sorting and excludes full result materialization. Keep regressions visible instead of selecting only the best parallel case; do not infer total spill traffic from peak temporary storage.

## Avoid reads through storage layout: DuckDB, 2025-06-06

The [multi-column clustering report](https://duckdb.org/2025/06/06/advanced-sorting-for-fast-selective-queries) includes SQL for approximate multidimensional keys and row-group analysis, tested on v1.2.2. Clustering narrows zone-map ranges so selective filters skip more data. In its roughly 1.1 GB remote flight-data experiment, an origin-oriented sort reduced one filter case from 16 to 1.6 seconds; sorted-table creation cost 48–61 seconds versus 21.4 seconds unsorted. Other layouts serve multiple filter dimensions more evenly.

**Experiment to transfer:** test all common filter combinations at realistic selectivity, network/cache conditions, and ingest frequency. Track rows scanned, bytes read, returned rows, build/maintenance cost, and query latency. Connection recreation was excluded from report timing; row-group macros have insertion-layout assumptions. Calculate when repeated read savings repay the extra layout cost rather than declaring sorting universally beneficial.

## Optimize generated code with a training profile: rust-analyzer, 2025-04-21

[Release v0.3.2431](https://rust-analyzer.github.io/thisweek/2025/04/21/changelog-282.html), commit `723121e`, shipped PGO for most builds except ARM and reports roughly 20% improvement. The [initial PR](https://github.com/rust-lang/rust-analyzer/pull/19582) describes an `analysis-stats` result; it is not an interactive-latency workload matrix. The [current PGO helper](https://github.com/rust-lang/rust-analyzer/blob/master/xtask/src/pgo.rs) is a moving implementation: generate profiles, exercise analysis, require nonempty raw profiles, merge with the toolchain's `llvm-profdata`, and rebuild using the profile.

**Experiment to transfer:** use representative training inputs, compatible tools, an optimized non-PGO baseline, and held-out projects. Keep build flags and runtime settings matched; record warnings and the profile's provenance. Separate a workload-trained build improvement from an algorithm change, and verify large, rare, and different-language inputs rather than relying on the training workload's gain.

## Keep accelerators fed: vLLM, 2025-01-27

The [V1 alpha report](https://vllm.ai/blog/2025-01-27-v1-alpha-release) reports up to 1.7× throughput versus V0 without multi-step scheduling on its model/dataset comparisons. It attributes much of the benefit to CPU overhead reduction while kernels remain similar: an isolated engine loop, persistent batches updated incrementally, request caching, chunked prefill, compilation, and piecewise CUDA graphs. [v0.7.0](https://github.com/vllm-project/vllm/releases/tag/v0.7.0), commit `5204ff5c3feeb96e8a6eea65dfcb78395f90d4d8`, anchors the V1 release, not every benchmark revision. Alpha-era feature restrictions are historical.

**Experiment to transfer:** obtain a host/device timeline before changing arithmetic. Compare incremental batch preparation, reduced transfer, or graph replay separately. Preserve arrival rate, token distributions, cache state, generated-output quality, and cancellation. Report TTFT, inter-token/end-to-end latency, throughput, and SLO goodput; a faster kernel or saturated batch is insufficient service evidence.

## Amortize compilation without hiding startup: PyTorch/Diffusers, 2025-07-17

The [regional-compilation report](https://pytorch.org/blog/torch-compile-and-diffusers-a-hands-on-guide-to-peak-performance/) links a [mutable benchmark script](https://gist.github.com/sayakpaul/91fa328e949c71dc4420ebb50eb35ca3). On one H100 and its FLUX.1-dev workload, inference fell 6.7→4.5 seconds; regional compilation preserved similar runtime gains while cold compilation fell 67.4→9.6 seconds. CPU offload reduced device memory but increased latency substantially. Optimization code is open-source; the [model weights have separate non-commercial terms](https://huggingface.co/black-forest-labs/FLUX.1-dev).

**Experiment to transfer:** measure cold compile, warm execution, recompilation, and memory separately. Compile a repeated region or remove a graph break before compiling everything. Keep shape/step/dtype/seed settings recorded; use a numerical or task-quality oracle. Treat offload and quantization as separate tradeoffs. Evaluate whether the process lifetime repays startup cost; the linked script is not a complete environment lock.

## Tune for the actual hardware bottleneck: FlashAttention-4, 2026-03-05

The [versioned paper](https://arxiv.org/html/2603.05451v1) studies attention kernels with asynchronous matrix/softmax overlap, polynomial exponential evaluation, and changes to backward memory traffic. The [author's updated report](https://tridao.me/blog/2026/flash4/) says newer cuDNN versions now perform similarly to FA4, so the older comparison is not a current universal lead. The paper's main text names B200 while its appendix names B100 and a conflicting date: preserve this reproducibility limit. [Current code](https://github.com/Dao-AILab/flash-attention/tree/main/flash_attn/cute) and [reference output/gradient tests](https://github.com/Dao-AILab/flash-attention/blob/main/tests/cute/test_flash_attn.py) are moving sources, distinct from the paper revision.

**Experiment to transfer:** profile the limiting execution/memory pipeline on the actual device and shape. Validate outputs and gradients, approximation error, and deterministic behavior. Sweep sequence/head dimensions and compare current libraries. A peak kernel-throughput comparison does not establish full-model latency or quality.

## How to use this ledger

Select the nearest mechanism and a dissimilar workload that could falsify it. Record whether a source is a benchmark report, released implementation, current code, or a local replication. Prefer a rejected or regressing cohort over another favorable headline when it helps define the boundary. Convert the example into a project-specific hypothesis using [strategies.md](strategies.md), then select an instrument using [tools.md](tools.md).
