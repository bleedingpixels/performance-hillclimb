# Origin and evidence boundaries

Sources were checked on 2026-10-05. This skill generalizes their engineering method; it does not promise the same results, model capabilities, tools, or scale.

The source base extends beyond the original article and critique. Read [case-studies.md](case-studies.md) for nine 2025-2026 open-source optimization reports, implementation anchors, measured tradeoffs, and reproducibility limits; read [tools.md](tools.md) for primary tool documentation. [strategies.md](strategies.md) turns those cases into project-specific experiments. None of the published benchmarks was reproduced to create this skill.

## Article

[Anthropic's performance sprint](https://claude.dev/blog/how-we-made-claude-ai-faster/) describes discovering bottlenecks, building measurements, validating improvements, retaining regression guards, and using engineers to steer tradeoffs. Its speedup claim concerns selected app journeys at p75. It is not evidence for faster model inference, universal speedups, or autonomous change approval.

## Critique

[Theo's video](https://www.youtube.com/watch?v=FsDUOUV9Vs8) was examined through automatic English captions, without independently reproducing the reported bugs or inspecting the private implementation.

- [06:05](https://www.youtube.com/watch?v=FsDUOUV9Vs8&t=365) and [08:23](https://www.youtube.com/watch?v=FsDUOUV9Vs8&t=503): reported missing or stale sidebar state motivates checking useful completion and cross-session consistency.
- [25:33](https://www.youtube.com/watch?v=FsDUOUV9Vs8&t=1533) and [37:28](https://www.youtube.com/watch?v=FsDUOUV9Vs8&t=2248): suspected caching and measurement incentives are hypotheses.
- [39:54](https://www.youtube.com/watch?v=FsDUOUV9Vs8&t=2394): Theo acknowledges that repository access is needed to test his causal explanation.

The adopted lesson is to measure correct outcomes alongside performance. Do not cite the critique as proof that a particular optimization introduced a regression.

## Primary technical references

| Source | Constraint carried into the skill |
| --- | --- |
| [Valgrind Cachegrind manual](https://valgrind.org/docs/manual/cg-manual.html) | Machine instruction counts complement elapsed-time measurements; repeatability and scope need verification. |
| [Google Benchmark user guide](https://github.com/google/benchmark/blob/main/docs/user_guide.md) and [variance guidance](https://github.com/google/benchmark/blob/main/docs/reducing_variance.md) | Timing needs warm-up, repetition, controlled conditions, and a suitable statistical decision. |
| [V8 flag definitions](https://github.com/v8/v8/blob/main/src/flags/flag-definitions.h) | Predictability flags can change runtime behavior; results need validation under intended settings. |
| [V8 strings](https://github.com/v8/v8/blob/main/src/objects/string.h), [substring creation](https://github.com/v8/v8/blob/main/src/heap/factory.cc), [regex paths](https://github.com/v8/v8/blob/main/src/regexp/regexp.cc) | Encoding and substring storage affect performance; narrowing must preserve characters. |
| [DevTools begin-frame protocol](https://chromedevtools.github.io/devtools-protocol/tot/HeadlessExperimental/#method-beginFrame) and [rendering performance](https://web.dev/articles/rendering-performance) | Synthetic cadence is distinct from elapsed execution and physical display throughput. |

Recheck source and documentation for the project's actual versions before applying implementation-sensitive behavior. Published success reports do not replace measurements in the selected checkout and environment.
