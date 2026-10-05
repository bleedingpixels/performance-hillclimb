# Performance experiment record

Adapt or remove fields that do not affect this decision. Fill absent evidence as unknown or unmeasured. Store paths relative to this record for a portable handoff, or use exact absolute paths where needed.

## Campaign

- Requested operation and permitted change surface:
- Time/resource budget and stopping rule:
- Original source identity and existing unrelated changes:
- Current accepted baseline:
- Runtime, flags, hardware/device, external dependencies:
- Workloads, cohorts, arrival pattern/concurrency, cold/warm state:
- Source lead and evidence type (report, release, current code, local replication):
- Bottleneck model, critical-path share, and conditions that could falsify it:
- Selected instrument/mode, artifact meaning, availability, and blind spots:
- Startup/preprocessing/maintenance repayment and memory/quality tradeoffs:

## Measurement contract

| Role | Metric, unit, direction, and completion boundary | Workload / denominator / aggregation | Acceptance condition and decision method | Command and raw evidence |
| --- | --- | --- | --- | --- |
| Outcome | | | | |
| Diagnostic proxy | | | | |
| Correctness / freshness | | | | |
| Resource / quality guardrail | | | | |

- Baseline samples, noise, warm-up, repetitions, and instrument overhead:
- Outcome/proxy validation and known blind spots:
- Failures/timeouts and required lifecycle checks:
- Independent oracle and representative untuned workload:
- Threshold/uncertainty method selected before comparison:

## Experiment

- ID, date, baseline/candidate revision or source hashes:
- Hypothesis and supporting trace:
- Change and why it should affect the outcome:
- Behavior at risk and relevant checks:
- Exact reproduction commands and environment differences:

| Measurement | Baseline result and samples | Candidate result and samples | Delta / uncertainty | Meets condition? |
| --- | --- | --- | --- | --- |
| Outcome | | | | |
| Diagnostic | | | | |
| Correctness / freshness | | | | |
| Resource / quality | | | | |

- Decision: accepted / rejected / inconclusive.
- Explanation and tradeoffs:
- Rejected changes restored or isolated:
- Fresh confirmation and cumulative comparison to original baseline:
- New bottleneck or next hypothesis:

## Regression guard and handoff

- Benchmark / metric / fixture / runtime versions:
- Guard location, ceiling/tolerance, and valid environment:
- Local proof; field/device evidence if available:
- Status and remaining boundary:
- Exact accepted source, artifact paths, and first resume action:
