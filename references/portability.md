# Use Performance Hill Climb across harnesses

This is an Agent Skills bundle: standard `name` and `description` frontmatter, Markdown instructions, relative references, an experiment template, and an optional local installer. It contains no provider calls and does not require an MCP server, agent framework, Python environment, or benchmark runner to follow the workflow. Use the target project's tools for measurement and verification.

## Universal activation

Any harness that can read files can use the skill. Give it the absolute path to `SKILL.md` and identify the project and desired outcome. For the default global installation, an example prompt is:

> Read `/absolute/path/to/performance-hillclimb/SKILL.md` and follow its referenced files as needed. Apply it to the project at `/absolute/path/to/project`. Discover a useful outcome metric, establish a reproducible baseline and correctness guardrails, then run a bounded optimization loop within the authorized scope. Preserve raw evidence and report what the measurements prove.

Replace the home and project paths for the machine being used. Reading only the frontmatter does not load the procedure. Resolve relative links against the skill folder, not the project checkout. Keep the project and evidence paths independent of where the skill is installed.

## Default global installation

From any complete copy of this bundle, run:

```sh
python3 "/absolute/path/to/performance-hillclimb/scripts/install.py" --global --dry-run
python3 "/absolute/path/to/performance-hillclimb/scripts/install.py" --global
python3 "$HOME/.agents/skills/performance-hillclimb/scripts/install.py" --global --check
```

The default installation creates a complete physical bundle in `$HOME/.agents/skills/performance-hillclimb` and a Claude Code skill-folder link at `$HOME/.claude/skills/performance-hillclimb`. Current documentation supports the shared user directory for Codex, Devin CLI, Cursor, Gemini CLI, OpenCode, Goose, and Grok Build. The physical shared bundle avoids depending on a loader's symlink traversal. Claude Code explicitly supports linked skill folders.

The installer uses Python 3.9 or newer and only its standard library, and makes no network requests. It locates the source from its own file path, so relocation and an unrelated current working directory work. It copies the explicit bundle inventory and adds a receipt listing the managed file hashes. It preflights all requested targets, refuses conflicting paths and modified managed copies, preserves valid links, and rolls back its preceding target changes if a later write fails. It never edits project instructions or other skills.

Repeat installation to update an unchanged managed copy. A conflict is a reason to inspect the destination, not to delete local work. A byte-identical unmanaged bundle may be adopted; a differing unmanaged directory is refused. `--check` and `--dry-run` perform no writes.

## Custom roots and physical copies

Install into another loader's documented skills root, or a project-local skills directory when project instructions call for one:

```sh
python3 "/absolute/path/to/performance-hillclimb/scripts/install.py" \
  --skills-dir "/absolute/path/to/another-harness/skills"

python3 "/absolute/path/to/performance-hillclimb/scripts/install.py" \
  --global --skills-dir "/absolute/path/with spaces/skills"

python3 "/absolute/path/to/performance-hillclimb/scripts/install.py" --global --copy
```

Each custom root receives a complete physical `performance-hillclimb` folder. `--copy` also uses a physical copy for a new Claude destination. Existing valid links and existing physical copies retain their form. `--home PATH` selects a different home for installation or isolated tests; it does not configure a running harness's home. Use the same custom arguments with `--check` to inspect those destinations.

No loader is required: copying the complete folder to an accessible location and explicitly reading `SKILL.md` is sufficient for a capable file-reading harness. If a harness cannot access local files, provide the instructions and required references through its supported attachment or repository mechanism.

## Native discovery and activation

Documentation checked on 2026-10-05. Loader support is version dependent; use the local harness's list or inspection command where available. A documented root and a valid installation do not prove an actual optimization run.

| Harness | User discovery root | Activate or inspect |
| --- | --- | --- |
| Codex | `$HOME/.agents/skills` | Use `$performance-hillclimb` or select it through `/skills`. Skills are normally detected automatically; restart if needed. |
| Claude Code | `$HOME/.claude/skills` | Use `/performance-hillclimb`; inspect `/skills`. Skill changes are watched; use `/reload-skills` if a new directory is not discovered. |
| Devin CLI | `$HOME/.agents/skills`; native alternatives include `$HOME/.config/devin/skills` | Use `/performance-hillclimb`. Inspect `devin skills paths`, `devin skills list --json`, or `devin skills show performance-hillclimb`. A shared-root listing may qualify the name as `agents:performance-hillclimb`. |
| Cursor | `$HOME/.agents/skills`; native alternative `$HOME/.cursor/skills` | Use `/performance-hillclimb` or select with `@`. Inspect Customize → Skills. Discovery occurs at startup; restart if needed. |
| Gemini CLI | `$HOME/.agents/skills`; native alternative `$HOME/.gemini/skills` | Ask it to use `performance-hillclimb`; activation follows the harness's consent flow. Inspect `gemini skills list`; use `/skills reload` or `/skills refresh` in an existing session. |
| OpenCode | `$HOME/.agents/skills`; native alternative `$HOME/.config/opencode/skills` | Ask it to use `performance-hillclimb`; its native skill tool accepts that name. Start a fresh session if needed. |
| Goose | `$HOME/.agents/skills` | Inspect `goose skills list`; use `/skills performance-hillclimb` or ask naturally. Discovery occurs at session start. |
| Grok Build | `$HOME/.agents/skills`; native alternative `$HOME/.grok/skills` | Use `/performance-hillclimb`; inspect `agent inspect` or `grok inspect`. Current documentation describes automatic refresh. |

The Codex-specific `agents/openai.yaml` supplies optional picker metadata. Other loaders can ignore it; the authoritative procedure is `SKILL.md`. The skill has no required named tool permissions. Delegation is optional and must be supported and authorized in the active environment.

For Cursor, use the physical shared bundle or a physical copy in its native root; do not assume symlink discovery based on older installations. To make a native copy:

```sh
python3 "$HOME/.agents/skills/performance-hillclimb/scripts/install.py" \
  --skills-dir "$HOME/.cursor/skills"
```

## Remote and cloud environments

Global means discoverable by local harnesses using the same home directory. It does not install into another machine, container, remote account, or hosted agent. Copy this complete folder to that environment, then run the installer there or place it in that harness's supported repository skill directory. Use explicit file activation when automatic discovery is unavailable.

Claude Code's local personal skill directory is separate from account-enabled cloud or Cowork skills. Cursor's optional cloud skill sync uses its native `$HOME/.cursor/skills` directory; installing in the shared root alone does not enable that sync. A Devin CLI listing proves local discovery, not Devin cloud availability. Follow the remote product's supported setup within the user's authorized scope; this installer does not publish or change account settings.

## Primary references

- [Agent Skills specification](https://agentskills.io/specification)
- [Codex skills](https://learn.chatgpt.com/docs/build-skills)
- [Claude Code skills](https://code.claude.com/docs/en/skills)
- [Devin CLI skills overview](https://docs.devin.ai/cli/extensibility/skills/overview) and [format](https://docs.devin.ai/cli/extensibility/skills/creating-skills)
- [Cursor skills](https://cursor.com/docs/skills)
- [Gemini CLI skills](https://geminicli.com/docs/cli/skills/) and [management](https://geminicli.com/docs/cli/using-agent-skills/)
- [OpenCode skills](https://opencode.ai/docs/skills/)
- [Goose skills](https://goose-docs.ai/docs/guides/context-engineering/using-skills/)
- [Grok Build skills guide](https://github.com/xai-org/grok-build/blob/main/crates/codegen/xai-grok-pager/docs/user-guide/08-skills.md)
