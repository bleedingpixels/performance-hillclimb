# Performance Hill Climb

A portable AI skill for discovering useful performance metrics and iteratively optimizing software with evidence. Use it with Codex, Claude Code, Devin CLI, Gemini CLI, Cursor, Goose, OpenCode, Grok Build, or any agent that can read files and run the target project's commands.

The workflow starts with a correct, useful outcome, establishes a reproducible baseline, tests a bounded hypothesis, and keeps a change only when it meets the chosen improvement threshold and correctness/resource guardrails. It distinguishes elapsed-time outcomes from diagnostic proxies, preserves raw evidence, and reprofiles after accepted changes.

## Install globally

```sh
git clone https://github.com/bleedingpixels/performance-hillclimb.git
cd performance-hillclimb
python3 scripts/install.py --global --dry-run
python3 scripts/install.py --global
python3 scripts/install.py --global --check
```

The optional installer requires Python 3.9 or newer and uses only the standard library. Following the skill's optimization procedure has no Python, provider API, MCP, or framework dependency.

The default installation creates a complete physical bundle at `$HOME/.agents/skills/performance-hillclimb` and a Claude Code link at `$HOME/.claude/skills/performance-hillclimb`. Use `--copy` to create a physical copy for a new Claude destination. Other documented loader roots can receive complete copies:

```sh
python3 scripts/install.py --skills-dir "/absolute/path/to/another-harness/skills"
```

The installer checks all targets before writing, preserves valid existing links, refuses modified or conflicting destinations, and rolls back preceding replacements after ordinary write failures. It copies only the ten explicit skill files; repository tests and development files are not installed. Unchanged managed seven-file installations upgrade safely. See [installation and portability](references/portability.md) for updates, custom roots, refresh behavior, and remote environments.

## Use it

| Harness | Activation |
| --- | --- |
| Codex | `$performance-hillclimb` or select through `/skills` |
| Claude Code and Devin CLI | `/performance-hillclimb` |
| Cursor | `/performance-hillclimb` or select with `@` |
| Goose | `/skills performance-hillclimb` |
| Gemini CLI and OpenCode | Ask the agent to use `performance-hillclimb` |
| Grok Build | `/performance-hillclimb` |

For a harness without automatic skill discovery, give it the absolute path to the skill:

> Read `/absolute/path/to/performance-hillclimb/SKILL.md` and follow its referenced files as needed. Apply it to the project at `/absolute/path/to/project`. Discover a meaningful outcome metric, establish a reproducible baseline and correctness guardrails, then run a bounded optimization loop within the authorized scope. Preserve raw evidence and report what the measurements prove.

Choose an entry point:

- **Discover:** identify the operation, bottleneck, and useful measurements.
- **Optimize:** qualify the benchmark and run the candidate loop.
- **Guard or resume:** preserve a verified gain or recover an existing campaign.

The skill adapts to UI, service/database, CLI/compiler, native CPU/GPU, and data/ML workloads. It does not promise a particular speedup or authorize deployment, publication, infrastructure spending, or perpetual jobs. A local installation is separate from installation in a hosted account or remote machine.

## Bundle

- [SKILL.md](SKILL.md): the procedure and acceptance rules.
- [Metric guide](references/metrics.md): metric contracts, instruments, proxy validation, and workload-specific caveats.
- [Tool guide](references/tools.md): which CPU, waiting, memory, query, load, or device artifact answers the question.
- [Strategy guide](references/strategies.md): mechanisms, critical-path bounds, repayment, tradeoffs, and experiments.
- [Recent cases](references/case-studies.md): nine 2025-2026 project reports with implementation links, gains, regressions, and proof boundaries.
- [Experiment record](assets/experiment-record.md): an adaptable evidence template.
- [Portability guide](references/portability.md): discovery, activation, installation, and cloud boundaries.
- [Sources and caveats](references/sources.md): the article, critique, and primary technical references behind the method.
- `agents/openai.yaml`: optional Codex picker metadata; other harnesses can ignore it.
- `scripts/install.py`: an offline, relocatable installer.

The method draws on Anthropic's performance sprint and critique plus recent work from V8, Go, Dolt, DuckDB, rust-analyzer, vLLM, PyTorch/Diffusers, and FlashAttention. The source guide separates reported results, released/current code, technical constraints, and unproven explanations. Reported speedups are workload-specific leads, not promises for another project.

## Validate changes

Run the isolated installer tests without writing to your actual home:

```sh
python3 -B -m unittest discover -s tests -v
```

Tests cover first installation, repeated installation, relocation, paths with spaces, custom directories, local-edit preservation, conflicting paths, missing files, managed updates, and injected write/rollback failures. The installer does not guarantee recovery from power loss or hostile concurrent directory replacement.

Use [the decision-support evaluation](tests/skill-evaluation.md) to compare guidance on fixed scenarios before accepting a research revision. It records the 2026-10-05 planning comparison, separate audio case, acceptance rubric, and proof limits. Installer success and planning scores do not establish an application's performance gain.

Before publishing changes, inspect every tracked file and the complete commit history for secrets and identifying data. Keep installation receipts, generated benchmark evidence, local configuration, and session transcripts out of this repository.

## License

MIT. Public source references retain their own terms.
