# Choose an instrument for the question

Primary project documentation checked on 2026-10-05. Choose the observable question first, then the least intrusive available instrument. These tools are options, not dependencies. Verify local version, OS, device, symbols, permissions, and export format before using a command. If counters or attachment are unavailable, use project timers/traces and output checks; label the missing attribution instead of changing machine security settings automatically.

## Route the investigation

Low average CPU with high latency suggests waiting, queueing, bursts, or skew worth investigating; it does not prove any one cause. CPU-active memory stalls are also different from descheduled or blocked time. Attribute work to the requested operation and completed work. A flame graph is an aggregation, while a timeline exposes ordering and overlap; neither alone proves the application's causal bottleneck.

| Question / task | Tool and artifact | What it helps decide; important limit |
| --- | --- | --- |
| Did a complete CLI/build job get faster? | [Hyperfine](https://github.com/sharkdp/hyperfine): repeated command times, warmups/preparation, parameter sweeps, JSON export | Compare end-to-end commands and thread/input cohorts. It does not explain the cause or measure a persistent service's requests. Match cold/warm state and output. |
| Is a benchmark change distinguishable from noise? | [Google Benchmark](https://github.com/google/benchmark/blob/main/docs/user_guide.md); [benchstat](https://pkg.go.dev/golang.org/x/perf/cmd/benchstat) for Go-format samples | Repetition and sample comparisons support an acceptance decision. Statistical significance is not practical importance. Prespecify runs; interleave builds; preserve distinct workloads. Benchstat warns about multiple testing and supports exact counters separately. |
| Which native code executes, and what counters changed? | [Linux perf](https://perfwiki.github.io/main/tutorial/): `stat`, `record`, `report`, `annotate` | Count cycles/instructions and supported cache/branch events; inspect stacks/source/assembly. PMU availability, multiplexing, symbols, stack unwinding, and sampling affect attribution. Fewer instructions can still take longer. |
| Where does wall time go when CPU profiles are quiet? | [BCC offcputime](https://github.com/iovisor/bcc/blob/master/tools/offcputime_example.txt); [Perfetto scheduling](https://perfetto.dev/docs/data-sources/cpu-scheduling) | Blocked-duration stacks and scheduling/thread-state timelines distinguish waits and runnable delay. Idle workers inflate totals. Correlate request/task intervals and account for tracing overhead. |
| Are native allocations transient or retained? | [Heaptrack v1.5.0](https://github.com/KDE/heaptrack/blob/v1.5.0/README.md): allocation stacks, lifetimes, peak consumers | Remove churn or shrink retained structures. It misses stack allocation; custom pools may need annotations. Heap allocation metrics are not total RSS. |
| Did a Go revision introduce work? | [pprof comparison](https://github.com/google/pprof/blob/main/doc/README.md#comparing-profiles): matched CPU profiles and `-diff_base` | Locate additional cost before optimizing its body. Use equal work/sample definitions. `-base` is for cumulative-profile subtraction; normalization can hide absolute cost growth. |
| Is Go memory cost allocation volume or live heap? | [runtime/pprof](https://pkg.go.dev/runtime/pprof): `alloc_space` versus `inuse_space` | Allocation churn and retention require different changes. Heap samples reflect completed GC and do not explain all RSS. Record sampling/runtime settings. |
| Are goroutines waiting on holders, GC, syscalls, or scheduler queues? | [Go block/mutex profiles](https://pkg.go.dev/runtime/pprof#Profile) and [execution trace](https://pkg.go.dev/runtime/trace): tasks/regions and transition timeline | Block stacks identify waiters; mutex stacks commonly identify the holder's unlock path. Aggregated waiter time can exceed wall time. Request tasks cross goroutines; Go 1.25+ FlightRecorder can retain a recent window for rare events. |
| Is JVM time executing, waiting, allocating, or contending? | [async-profiler modes](https://github.com/async-profiler/async-profiler/blob/master/docs/ProfilingModes.md): CPU, wall, alloc, lock; JFR artifacts | Choose the mode for the question. Wall includes sleeping/blocked threads; it is not CPU time. Filter relevant threads and measure overhead rather than enabling every mode by default. |
| Is Python overhead interpreter work, native work, or allocation? | [py-spy](https://github.com/benfred/py-spy): sampled stacks; [Memray](https://bloomberg.github.io/memray/run.html): allocation/lifetime capture | Native/subprocess support and symbols matter. py-spy's idle filtering is heuristic; `--gil` misses active extensions that release it. Memray's Python-allocator tracing adds detail/overhead; aggregate mode loses temporary lifetimes. |
| What delayed a browser interaction or frame? | [Chrome Performance](https://developer.chrome.com/docs/devtools/performance) and [Perfetto analysis](https://perfetto.dev/docs/quickstart/trace-analysis): interaction/main-thread/rendering timeline | Separate scripting, rendering, dependency gaps, and scheduling. Simulated throttling is not a physical-device result; retain user-visible correctness and completion. |
| Did live audio miss a deadline despite short callbacks? | Existing bounded application events; [PipeWire pw-top](https://docs.pipewire.org/page_man_pw-top_1.html) node/graph timing and error reports | Correlate processing, scheduling, state changes, and stream failures. Follower WAIT and driver WAIT have different meanings; ERR includes both xruns and other errors. Callback duration alone misses late entry, and the nominal cycle interval is not a guaranteed callback budget. Check event losses, clock compatibility, realtime safety, and unchanged buffering; absent scheduler traces leave attribution uncertain. |
| Is SQL cost scans, cardinality, sorting, or spill? | [DuckDB profiling](https://duckdb.org/docs/current/dev/profiling): `EXPLAIN`, executing `EXPLAIN ANALYZE`, JSON; [metric definitions](https://duckdb.org/docs/current/dev/metrics) | Compare estimated/actual rows, scanned rows, bytes read, operator time, peak buffers/temp storage. `CPU_TIME` is cumulative operator timing, not a hardware CPU counter; blocked-thread time has a narrow definition. Peak temp size is not total spill bytes. Execute only the authorized query. |
| Did a service improve at the same offered load? | [k6 arrival-rate model](https://grafana.com/docs/k6/latest/using-k6/scenarios/concepts/open-vs-closed/), [dropped iterations](https://grafana.com/docs/k6/latest/using-k6/scenarios/concepts/dropped-iterations/); [wrk2](https://github.com/giltene/wrk2) corrected latency histograms | Measure offered/achieved arrivals, latency, errors, and dropped work. A closed loop can reduce arrivals when responses slow. An open generator can still run out of workers; disclose drops and generator saturation. Use a model matching real arrivals. |
| Is a GPU waiting for the host, copying data, or executing kernels? | [PyTorch Profiler](https://docs.pytorch.org/docs/2.14/profiler.html): CPU/device activities, shapes, allocations, trace export | Start with the timeline before selecting a kernel. Shapes/stacks perturb runs. CUDA trace completeness depends on CUPTI; absent kernels do not prove absent work. Prefer the maintained PyTorch interface over new standalone Kineto integrations. |
| What happens on AMD HIP devices? | [rocprofv3](https://rocm.docs.amd.com/projects/rocprofiler-sdk/en/latest/how-to/using-rocprofv3.html): HIP, kernel, memory-copy traces and supported counters | Trace launches/transfers before collecting targeted kernel counters. Check actual device support. Current SDK source is [ROCm/rocm-systems](https://github.com/ROCm/rocm-systems/tree/develop/projects/rocprofiler-sdk), not the retired standalone repository. |
| Which NVIDIA kernel resource limits useful work? | Optional vendor tools: [Nsight Systems](https://docs.nvidia.com/nsight-systems/UserGuide/) for timeline, [Nsight Compute](https://docs.nvidia.com/nsight-compute/ProfilingGuide/) for kernel counters/roofline | These are vendor tools, not open-source requirements. Compute replay/cache handling can alter execution and adds overhead; its measured duration is not ordinary application latency. Correlate kernel findings with the timeline and remeasure normally. |
| Does LLM serving satisfy user latency constraints? | [vLLM bench serve](https://docs.vllm.ai/en/latest/cli/bench/serve/) and [metric definitions](https://docs.vllm.ai/en/latest/design/metrics/): per-request results, latency percentiles, SLO goodput | Specify arrival rate explicitly; the default infinite rate submits at once. Preserve input/output token distributions, cache, weights, and stop behavior. TTFT, ITL, request-average TPOT, output tokens/s, and goodput answer different questions. |
| Can a trained build improve code layout or code generation? | [rust-analyzer PGO helper](https://github.com/rust-lang/rust-analyzer/blob/master/xtask/src/pgo.rs); [LLVM BOLT](https://github.com/llvm/llvm-project/blob/main/bolt/README.md) | Train on representative work, merge compatible profiles, compare optimized builds on held-out inputs. BOLT is post-link layout optimization for supported ELF targets and has symbol/relocation/code-generation requirements; it is not a replacement for algorithm analysis. |
| Would speeding this native region improve the chosen outcome? | [Coz](https://github.com/plasma-umass/coz): causal profile with throughput or latency progress points | Estimate sensitivity rather than equating hotness with impact. Requires supported native code/debug information and suitable progress points; interpreted/JIT language support is limited. Virtual speedup is a hypothesis, not proof of an implemented gain. |

## Small starting recipes

Adapt workload, version, and paths. Capture a diagnostic run, then do final comparisons without the profiler. These examples do not install tools or require that all tools be available.

```sh
# Command outcome, with a documented warm-state policy
hyperfine --warmup 3 --runs 15 --export-json comparison.json './baseline input' './candidate input'

# Native CPU counters and sampled attribution; select locally supported events
perf stat -e cycles,instructions,cache-misses -- ./program input
perf record -g -- ./program input
perf report

# Absolute matched profile comparison; keep work/units comparable
go tool pprof -diff_base baseline.pb.gz candidate.pb.gz

# Go-format sample comparison; collect repeated interleaved runs separately
benchstat baseline.txt candidate.txt

# Python allocation evidence, separately from final timing
memray run --native -o allocations.bin program.py

# AMD launch/transfer timeline; verify installed flags and device support
rocprofv3 --hip-trace --kernel-trace --memory-copy-trace -- ./gpu-program
```

For GPU tasks, do not assume host enqueue duration measures completion. Include the intended synchronization/transfer boundary. For long-lived compiled programs, report first-call/compile costs separately from steady state. For services, preserve workload-specific tails instead of pooling percentiles or averaging cohort percentiles.

## Record the artifact's meaning

Store the question, tool/version/mode, process/task scope, runtime/hardware settings, samples or capture window, lost/unresolved events, units, and overhead. State what the artifact cannot observe. Use [metrics.md](metrics.md) to bind it to an outcome and [strategies.md](strategies.md) to turn the observation into a falsifiable change. Current docs and moving code links are starting points; use the selected project's installed versions for exact behavior.
