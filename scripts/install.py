#!/usr/bin/env python3
"""Optional, offline installer; the skill's runtime does not require Python."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import stat
import sys
import tempfile


NAME = "performance-hillclimb"
RECEIPT = ".performance-hillclimb-install.json"
FILES = (
    "SKILL.md",
    "agents/openai.yaml",
    "assets/experiment-record.md",
    "references/metrics.md",
    "references/sources.md",
    "references/portability.md",
    "scripts/install.py",
)
DIRECTORIES = {str(Path(name).parent) for name in FILES if "/" in name}


class Conflict(Exception):
    pass


def digest(data):
    return hashlib.sha256(data).hexdigest()


def inventory(root):
    """Inspect every entry, including empty directories; never follow symlinks."""
    hashes, directories = {}, set()
    for directory, children, files in os.walk(root, followlinks=False):
        for name in children + files:
            entry = Path(directory) / name
            relative = entry.relative_to(root).as_posix()
            mode = entry.lstat().st_mode
            if stat.S_ISLNK(mode):
                raise Conflict("unexpected symlink inside installation: " + relative)
            if stat.S_ISDIR(mode):
                directories.add(relative)
            elif stat.S_ISREG(mode):
                hashes[relative] = digest(entry.read_bytes())
            else:
                raise Conflict("unexpected non-regular entry: " + relative)
    return hashes, directories


def snapshot(path):
    if path.is_symlink():
        return ("link", os.readlink(path))
    if not path.exists():
        return ("missing",)
    if not path.is_dir():
        raise Conflict("destination is not a directory")
    hashes, directories = inventory(path)
    return ("directory", hashes, directories)


def load_source(source):
    payload = {}
    for name in FILES:
        entry = source / name
        if any(part.is_symlink() for part in [entry] + list(entry.parents)[:-1]):
            raise Conflict("source file or ancestor is a symlink: " + name)
        if not entry.is_file():
            raise Conflict("source is incomplete; missing regular file: " + name)
        payload[name] = (entry.read_bytes(), stat.S_IMODE(entry.stat().st_mode))
    return payload


def validate_copy(path, expected):
    hashes, directories = inventory(path)
    if directories != DIRECTORIES:
        raise Conflict("unexpected or missing directories in installation")
    receipt_hash = hashes.pop(RECEIPT, None)
    if set(hashes) != set(FILES):
        raise Conflict("unexpected or missing files in installation")
    if receipt_hash is None:
        if hashes != expected:
            raise Conflict("unmanaged directory differs from the complete source")
        return "adopt"
    try:
        receipt = json.loads((path / RECEIPT).read_text(encoding="utf-8"))
    except (ValueError, UnicodeError) as error:
        raise Conflict("invalid installation receipt: " + str(error)) from error
    if (
        not isinstance(receipt, dict)
        or set(receipt) != {"schema", "name", "hashes"}
        or type(receipt["schema"]) is not int
        or receipt["schema"] != 1
        or receipt["name"] != NAME
        or not isinstance(receipt["hashes"], dict)
        or set(receipt["hashes"]) != set(FILES)
        or any(
            not isinstance(value, str)
            or len(value) != 64
            or any(character not in "0123456789abcdef" for character in value)
            for value in receipt["hashes"].values()
        )
    ):
        raise Conflict("invalid or foreign installation receipt")
    if hashes != receipt["hashes"]:
        raise Conflict("managed files have local changes; refusing replacement")
    return "unchanged" if hashes == expected else "update"


def destination(root):
    root = Path(root).expanduser().absolute()
    # Keep ancestors visible to preflight: resolving here could hide redirects.
    path = root / NAME
    if any(ancestor.is_symlink() for ancestor in path.parents):
        return path
    # Normalize benign aliases (including '..') so each destination is staged once.
    return root.resolve() / NAME


def contained(path, parent):
    try:
        path.relative_to(parent)
        return True
    except ValueError:
        return False


def preflight(path, kind, source, shared, expected):
    for ancestor in path.parents:
        if ancestor.is_symlink():
            raise Conflict("symlinked destination ancestor: " + str(ancestor))
        if ancestor.exists() and not ancestor.is_dir():
            raise Conflict("parent is not a directory: " + str(ancestor))
    before = snapshot(path)
    if path.is_symlink():
        try:
            resolved = path.resolve(strict=True)
        except (OSError, RuntimeError) as error:
            raise Conflict("dangling or unresolvable destination symlink") from error
        if resolved not in {source, shared}:
            raise Conflict("foreign destination symlink")
        # A valid existing link is preserved, including under --copy.
        if resolved == source:
            action = "linked"
        else:
            action = "outdated-link" if validate_copy(resolved, expected) == "update" else "linked"
        return {"path": path, "kind": kind, "action": action, "before": before}
    if path.resolve() == source:
        action = "source"
    elif not path.exists():
        action = "install"
    else:
        action = validate_copy(path, expected)
        # Preserve existing physical copies when the default is a Claude link.
        kind = "copy"
    return {"path": path, "kind": kind, "action": action, "before": before}


def remove(path):
    if path.is_symlink() or not path.is_dir():
        path.unlink()
    else:
        shutil.rmtree(path)


def transact(plans, payload, shared):
    """Stage all replacements, retain backups until every target is installed."""
    changed, parents, stages, warnings = [], [], [], []
    try:
        for plan in plans:
            if plan["action"] not in {"install", "adopt", "update"}:
                continue
            path = plan["path"]
            missing = []
            parent = path.parent
            while not parent.exists():
                missing.append(parent)
                parent = parent.parent
            for parent in reversed(missing):
                parent.mkdir()
                parents.append(parent)
            stage = Path(tempfile.mkdtemp(prefix="." + NAME + "-install-", dir=path.parent))
            stages.append(stage)
            replacement = stage / "replacement"
            if plan["kind"] == "link":
                replacement.symlink_to(shared, target_is_directory=True)
            else:
                replacement.mkdir()
                for name, (data, mode) in payload.items():
                    entry = replacement / name
                    entry.parent.mkdir(parents=True, exist_ok=True)
                    entry.write_bytes(data)
                    entry.chmod(mode)
                receipt = {"schema": 1, "name": NAME, "hashes": {
                    name: digest(data) for name, (data, _) in payload.items()
                }}
                (replacement / RECEIPT).write_text(
                    json.dumps(receipt, sort_keys=True, indent=2) + "\n", encoding="utf-8"
                )
            plan["stage"] = stage
            plan["installed_state"] = snapshot(replacement)
        # Recheck all destinations after staging, before the first replacement.
        for plan in plans:
            if snapshot(plan["path"]) != plan["before"]:
                raise Conflict("destination changed after preflight: " + str(plan["path"]))
        for plan in plans:
            if "stage" not in plan:
                continue
            path, stage = plan["path"], plan["stage"]
            if snapshot(path) != plan["before"]:
                raise Conflict("destination changed during installation: " + str(path))
            changed.append(plan)
            plan["backed_up"] = False
            plan["installed"] = False
            if plan["before"][0] != "missing":
                os.replace(path, stage / "previous")
                plan["backed_up"] = True
            os.replace(stage / "replacement", path)
            plan["installed"] = True
    except (OSError, Conflict) as error:
        rollback_errors = []
        retained = set()
        for plan in reversed(changed):
            try:
                if plan["installed"]:
                    if snapshot(plan["path"]) != plan["installed_state"]:
                        raise Conflict("new destination changed; preserving it and its backup")
                    remove(plan["path"])
                if plan["backed_up"]:
                    os.replace(plan["stage"] / "previous", plan["path"])
            except (OSError, Conflict) as rollback_error:
                retained.add(plan["stage"])
                rollback_errors.append(str(plan["path"]) + ": " + str(rollback_error)
                                       + "; recovery directory: " + str(plan["stage"]))
        for stage in stages:
            if stage not in retained:
                try:
                    shutil.rmtree(stage)
                except OSError as cleanup_error:
                    rollback_errors.append("cleanup " + str(stage) + ": " + str(cleanup_error))
        for parent in reversed(parents):
            try:
                parent.rmdir()
            except OSError:
                pass  # Never remove a populated directory or retained recovery data.
        raise Conflict("installation failed: " + str(error) + (
            "; rollback incomplete: " + "; ".join(rollback_errors)
            if rollback_errors else "; all replacements rolled back"
        )) from error
    for stage in stages:
        try:
            shutil.rmtree(stage)
        except OSError as error:
            warnings.append("installed; could not remove backup directory " + str(stage) + ": " + str(error))
    return warnings


def parser():
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("--global", dest="global_install", action="store_true",
                        help="install in ~/.agents/skills and ~/.claude/skills (default without custom roots)")
    result.add_argument("--skills-dir", action="append", default=[], metavar="PATH",
                        help="also install a physical copy in this Agent Skills root; repeatable")
    result.add_argument("--copy", action="store_true",
                        help="create physical copies, including new Claude installations; preserve valid existing links")
    modes = result.add_mutually_exclusive_group()
    modes.add_argument("--dry-run", action="store_true", help="preflight all targets without writing")
    modes.add_argument("--check", action="store_true", help="verify all installations without writing")
    result.add_argument("--home", type=Path, default=None, metavar="PATH",
                        help="override the home directory, useful for isolated tests")
    return result


def run(source, args):
    report = {"source": str(source), "mode": "check" if args.check else "dry-run" if args.dry_run else "install",
              "targets": []}
    try:
        source = source.resolve(strict=True)
        payload = load_source(source)
        expected = {name: digest(data) for name, (data, _) in payload.items()}
        home = (args.home if args.home is not None else Path.home()).expanduser().absolute()
        shared = destination(home / ".agents" / "skills")
        targets = []
        if args.global_install or not args.skills_dir:
            targets.extend([(shared, "copy"), (destination(home / ".claude" / "skills"),
                                                "copy" if args.copy else "link")])
        targets.extend((destination(root), "copy") for root in args.skills_dir)
        unique = {}
        for path, kind in targets:
            if path not in unique or kind == "copy":
                unique[path] = kind
        paths = list(unique)
        layout_errors = {}
        for path in paths:
            canonical = path.parent.resolve() / path.name
            if source != canonical and contained(source, canonical):
                layout_errors[path] = "destination contains the source"
            if canonical != source and contained(canonical, source):
                layout_errors[path] = "destination is inside the source"
            if any(path != other and contained(path, other) for other in paths):
                layout_errors[path] = "requested destinations overlap"
        plans, failed = [], False
        for path, kind in unique.items():
            row = {"path": str(path)}
            try:
                if path in layout_errors:
                    raise Conflict(layout_errors[path])
                plan = preflight(path, kind, source, shared, expected)
                plans.append(plan)
                row["status"] = plan["action"]
                if args.check and plan["action"] in {"install", "update", "outdated-link"}:
                    row["status"] = "missing" if plan["action"] == "install" else "outdated"
                    failed = True
            except (OSError, RuntimeError, Conflict) as error:
                row.update(status="conflict", error=str(error))
                failed = True
            report["targets"].append(row)
        shared_will_update = any(plan["path"] == shared and plan["action"] in {"update", "adopt"}
                                 for plan in plans)
        for row, plan in zip(report["targets"], plans) if not failed else []:
            if plan["action"] == "outdated-link":
                if shared_will_update and not args.check:
                    plan["action"] = "linked"
                    row["status"] = "linked"
                else:
                    row.update(status="outdated", error="linked shared copy needs an update; include --global")
                    failed = True
        if failed:
            report["error"] = "preflight failed; no destinations were changed"
            print(json.dumps(report, indent=2))
            return 1
        if not args.check and not args.dry_run:
            report["warnings"] = transact(plans, payload, shared)
            for row, plan in zip(report["targets"], plans):
                row["status"] = {"install": "installed", "update": "updated", "adopt": "adopted"}.get(
                    plan["action"], plan["action"]
                )
        print(json.dumps(report, indent=2))
        return 0
    except (OSError, RuntimeError, Conflict) as error:
        report["error"] = str(error)
        print(json.dumps(report, indent=2))
        return 1


def main(argv=None):
    return run(Path(__file__).resolve().parents[1], parser().parse_args(argv))


if __name__ == "__main__":
    sys.exit(main())
