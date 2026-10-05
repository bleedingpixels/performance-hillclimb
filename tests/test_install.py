# testing artifact
"""Isolated installer tests; never reads or writes the actual home directory."""
import contextlib
import importlib.util
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

INSTALLER = Path(__file__).resolve().parents[1] / "scripts/install.py"
SPEC = importlib.util.spec_from_file_location("skill_installer", INSTALLER)
MOD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MOD)


class InstallerTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="hillclimb-installer-test-")
        self.root = Path(self.temporary.name)
        self.source = self.root / "source" / MOD.NAME
        for name in MOD.FILES:
            entry = self.source / name
            entry.parent.mkdir(parents=True, exist_ok=True)
            if name == "scripts/install.py":
                shutil.copyfile(INSTALLER, entry)
            else:
                entry.write_text("fixture " + name + "\n", encoding="utf-8")
        self.home = self.root / "isolated home"
        self.home.mkdir()
        self.shared = self.home / ".agents/skills" / MOD.NAME
        self.claude = self.home / ".claude/skills" / MOD.NAME

    def tearDown(self):
        self.temporary.cleanup()

    def invoke(self, *arguments, source=None):
        output = io.StringIO()
        args = MOD.parser().parse_args(["--home", str(self.home), *map(str, arguments)])
        with contextlib.redirect_stdout(output):
            code = MOD.run(source or self.source, args)
        return code, json.loads(output.getvalue())

    def state(self, path):
        return MOD.snapshot(path)

    def legacy_copy(self, path, managed=True):
        for name in MOD.LEGACY_FILES:
            entry = path / name
            entry.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(self.source / name, entry)
        if managed:
            receipt = {"schema": 1, "name": MOD.NAME, "hashes": MOD.inventory(path)[0]}
            (path / MOD.RECEIPT).write_text(json.dumps(receipt) + "\n", encoding="utf-8")

    def test_first_global_install(self):
        code, report = self.invoke()
        self.assertEqual(code, 0, report)
        self.assertFalse(self.shared.is_symlink())
        self.assertEqual(self.claude.resolve(), self.shared)
        self.assertEqual(set(MOD.inventory(self.shared)[0]), set(MOD.FILES) | {MOD.RECEIPT})
        receipt = json.loads((self.shared / MOD.RECEIPT).read_text())
        self.assertEqual(set(receipt), {"schema", "name", "hashes"})
        self.assertNotIn(str(self.source), json.dumps(receipt))

    def test_repeat_is_idempotent(self):
        self.assertEqual(self.invoke()[0], 0)
        before = self.state(self.shared)
        inode = self.shared.stat().st_ino
        code, report = self.invoke()
        self.assertEqual(code, 0, report)
        self.assertEqual(before, self.state(self.shared))
        self.assertEqual(inode, self.shared.stat().st_ino)
        self.assertEqual([row["status"] for row in report["targets"]], ["unchanged", "linked"])

    def test_dry_run_writes_nothing(self):
        code, report = self.invoke("--dry-run")
        self.assertEqual(code, 0, report)
        self.assertEqual(list(self.home.iterdir()), [])

    def test_check_missing_and_installed(self):
        self.assertEqual(self.invoke("--check")[0], 1)
        self.assertEqual(list(self.home.iterdir()), [])
        self.assertEqual(self.invoke()[0], 0)
        self.assertEqual(self.invoke("--check")[0], 0)

    def test_relocation_spaces_and_unrelated_cwd(self):
        relocated = self.root / "relocated source with spaces" / MOD.NAME
        shutil.copytree(self.source, relocated)
        custom = self.root / "custom skills with spaces"
        result = subprocess.run([sys.executable, str(relocated / "scripts/install.py"),
                                 "--home", str(self.home), "--skills-dir", str(custom)],
                                cwd=self.root, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual((custom / MOD.NAME / "SKILL.md").read_bytes(),
                         (relocated / "SKILL.md").read_bytes())
        self.assertEqual(list(self.home.iterdir()), [])

    def test_local_edit_refused(self):
        self.assertEqual(self.invoke()[0], 0)
        (self.shared / "SKILL.md").write_text("local edit\n")
        before = self.state(self.shared)
        code, report = self.invoke()
        self.assertEqual(code, 1, report)
        self.assertIn("local changes", report["targets"][0]["error"])
        self.assertEqual(before, self.state(self.shared))

    def test_foreign_symlink_refused(self):
        foreign = self.root / "foreign"
        foreign.mkdir()
        self.shared.parent.mkdir(parents=True)
        self.shared.symlink_to(foreign, target_is_directory=True)
        self.assertEqual(self.invoke()[0], 1)
        self.assertEqual(self.shared.resolve(), foreign)
        self.assertFalse(self.claude.parent.exists())

    def test_dangling_symlink_refused(self):
        self.shared.parent.mkdir(parents=True)
        self.shared.symlink_to(self.root / "missing")
        self.assertEqual(self.invoke()[0], 1)
        self.assertTrue(self.shared.is_symlink())

    def test_global_later_conflict_does_not_update_earlier_target(self):
        self.assertEqual(self.invoke()[0], 0)
        before = self.state(self.shared)
        (self.source / "references/metrics.md").write_text("new release\n")
        self.claude.unlink()
        self.claude.write_text("foreign file\n")
        code, report = self.invoke()
        self.assertEqual(code, 1, report)
        self.assertEqual(before, self.state(self.shared))
        self.assertEqual(self.claude.read_text(), "foreign file\n")

    def test_update_managed_copy(self):
        self.assertEqual(self.invoke()[0], 0)
        (self.source / "references/metrics.md").write_text("new release\n")
        self.assertEqual(self.invoke("--check")[0], 1)
        code, report = self.invoke()
        self.assertEqual(code, 0, report)
        self.assertEqual(self.claude.joinpath("references/metrics.md").read_text(), "new release\n")
        self.assertEqual(self.invoke("--check")[0], 0)

    def test_legacy_managed_copy_upgraded(self):
        self.legacy_copy(self.shared)
        self.claude.parent.mkdir(parents=True)
        self.claude.symlink_to(self.shared, target_is_directory=True)
        code, report = self.invoke()
        self.assertEqual(code, 0, report)
        self.assertEqual([row["status"] for row in report["targets"]], ["updated", "linked"])
        self.assertTrue(self.claude.is_symlink())
        for name in MOD.FILES:
            self.assertEqual((self.shared / name).read_bytes(), (self.source / name).read_bytes())
        receipt = json.loads((self.shared / MOD.RECEIPT).read_text())
        self.assertEqual(receipt["schema"], 1)
        self.assertEqual(set(receipt["hashes"]), set(MOD.FILES))
        self.assertEqual(self.invoke("--check")[0], 0)
        self.assertEqual([row["status"] for row in self.invoke()[1]["targets"]],
                         ["unchanged", "linked"])

    def test_legacy_check_reports_outdated_without_changes(self):
        self.legacy_copy(self.shared)
        self.claude.parent.mkdir(parents=True)
        self.claude.symlink_to(self.shared, target_is_directory=True)
        before_shared, before_claude = self.state(self.shared), self.state(self.claude)
        with mock.patch.object(MOD, "transact") as transact:
            code, report = self.invoke("--check")
        self.assertEqual(code, 1, report)
        self.assertEqual([row["status"] for row in report["targets"]], ["outdated", "outdated"])
        transact.assert_not_called()
        self.assertEqual(self.state(self.shared), before_shared)
        self.assertEqual(self.state(self.claude), before_claude)

    def test_legacy_local_edit_refused(self):
        self.legacy_copy(self.shared)
        (self.shared / "SKILL.md").write_text("user edit\n")
        before = self.state(self.shared)
        code, report = self.invoke()
        self.assertEqual(code, 1, report)
        self.assertIn("local changes", report["targets"][0]["error"])
        self.assertEqual(self.state(self.shared), before)
        self.assertFalse(self.claude.parent.exists())

    def test_legacy_missing_file_refused(self):
        self.legacy_copy(self.shared)
        (self.shared / "references/portability.md").unlink()
        before = self.state(self.shared)
        code, report = self.invoke()
        self.assertEqual(code, 1, report)
        self.assertIn("missing files", report["targets"][0]["error"])
        self.assertEqual(self.state(self.shared), before)
        self.assertFalse(self.claude.parent.exists())

    def test_legacy_extra_file_refused(self):
        for name in ("notes.txt", "references/tools.md"):
            with self.subTest(name=name):
                skills = self.root / Path(name).stem
                path = skills / MOD.NAME
                self.legacy_copy(path)
                (path / name).write_text("user file\n")
                before = self.state(path)
                code, report = self.invoke("--skills-dir", skills)
                self.assertEqual(code, 1, report)
                self.assertIn("unexpected", report["targets"][0]["error"])
                self.assertEqual(self.state(path), before)

    def test_legacy_unexpected_directory_refused(self):
        self.legacy_copy(self.shared)
        (self.shared / "references/user experiments").mkdir()
        before = self.state(self.shared)
        code, report = self.invoke()
        self.assertEqual(code, 1, report)
        self.assertIn("directories", report["targets"][0]["error"])
        self.assertEqual(self.state(self.shared), before)

    def test_legacy_internal_symlink_refused(self):
        self.legacy_copy(self.shared)
        entry = self.shared / "references/portability.md"
        entry.unlink()
        entry.symlink_to(self.source / "references/portability.md")
        receipt = (self.shared / MOD.RECEIPT).read_bytes()
        code, report = self.invoke()
        self.assertEqual(code, 1, report)
        self.assertIn("symlink", report["targets"][0]["error"])
        self.assertTrue(entry.is_symlink())
        self.assertEqual((self.shared / MOD.RECEIPT).read_bytes(), receipt)
        self.assertFalse(self.claude.parent.exists())

    def test_unmanaged_legacy_copy_refused(self):
        self.legacy_copy(self.shared, managed=False)
        before = self.state(self.shared)
        code, report = self.invoke()
        self.assertEqual(code, 1, report)
        self.assertEqual(self.state(self.shared), before)
        self.assertFalse((self.shared / MOD.RECEIPT).exists())

    def test_unrecognized_receipt_file_sets_refused(self):
        layouts = {
            "partial-upgrade": set(MOD.LEGACY_FILES) | {"references/tools.md"},
            "extra-user-file": set(MOD.FILES) | {"notes.txt"},
            "missing-current-file": set(MOD.FILES) - {"references/metrics.md"},
        }
        for scenario, names in layouts.items():
            with self.subTest(scenario=scenario):
                skills = self.root / scenario
                path = skills / MOD.NAME
                for name in names:
                    entry = path / name
                    entry.parent.mkdir(parents=True, exist_ok=True)
                    entry.write_text("fixture " + name + "\n")
                receipt = {"schema": 1, "name": MOD.NAME, "hashes": MOD.inventory(path)[0]}
                (path / MOD.RECEIPT).write_text(json.dumps(receipt) + "\n")
                before = self.state(path)
                with mock.patch.object(MOD, "transact") as transact:
                    code, report = self.invoke("--skills-dir", skills)
                self.assertEqual(code, 1, report)
                self.assertIn("invalid or foreign", report["targets"][0]["error"])
                transact.assert_not_called()
                self.assertEqual(self.state(path), before)

    def test_mixed_current_and_legacy_global_copies_upgraded(self):
        self.assertEqual(self.invoke("--copy")[0], 0)
        before_claude, inode = self.state(self.claude), self.claude.stat().st_ino
        shutil.rmtree(self.shared)
        self.legacy_copy(self.shared)
        code, report = self.invoke()
        self.assertEqual(code, 0, report)
        self.assertEqual([row["status"] for row in report["targets"]], ["updated", "unchanged"])
        self.assertEqual(self.state(self.claude), before_claude)
        self.assertEqual(self.claude.stat().st_ino, inode)
        self.assertFalse(self.claude.is_symlink())
        self.assertEqual(self.invoke("--check")[0], 0)

    def test_legacy_upgrade_later_global_conflict_preserves_all_targets(self):
        self.assertEqual(self.invoke("--copy")[0], 0)
        shutil.rmtree(self.shared)
        self.legacy_copy(self.shared)
        (self.claude / "notes.txt").write_text("user file\n")
        before_shared, before_claude = self.state(self.shared), self.state(self.claude)
        with mock.patch.object(MOD, "transact") as transact:
            code, report = self.invoke()
        self.assertEqual(code, 1, report)
        self.assertEqual([row["status"] for row in report["targets"]], ["update", "conflict"])
        transact.assert_not_called()
        self.assertEqual(self.state(self.shared), before_shared)
        self.assertEqual(self.state(self.claude), before_claude)
        self.assertEqual(list(self.home.rglob("." + MOD.NAME + "-install-*")), [])

    def test_legacy_upgrade_rollback_restores_layout_and_receipts(self):
        self.legacy_copy(self.shared)
        self.legacy_copy(self.claude)
        before_shared, before_claude = self.state(self.shared), self.state(self.claude)
        receipts = {path: (path / MOD.RECEIPT).read_bytes() for path in (self.shared, self.claude)}
        original = os.replace

        def fail_later(source, destination):
            if Path(source).name == "replacement" and Path(destination) == self.claude:
                raise OSError("injected legacy upgrade failure")
            return original(source, destination)

        with mock.patch.object(MOD.os, "replace", side_effect=fail_later):
            code, report = self.invoke("--copy")
        self.assertEqual(code, 1, report)
        self.assertIn("all replacements rolled back", report["error"])
        self.assertEqual(self.state(self.shared), before_shared)
        self.assertEqual(self.state(self.claude), before_claude)
        for path, receipt in receipts.items():
            self.assertEqual((path / MOD.RECEIPT).read_bytes(), receipt)
            self.assertEqual(set(MOD.inventory(path)[0]), set(MOD.LEGACY_FILES) | {MOD.RECEIPT})
        self.assertEqual(list(self.home.rglob("." + MOD.NAME + "-install-*")), [])

    def test_identical_unmanaged_copy_adopted(self):
        shutil.copytree(self.source, self.shared)
        code, report = self.invoke()
        self.assertEqual(code, 0, report)
        self.assertEqual(report["targets"][0]["status"], "adopted")
        self.assertTrue((self.shared / MOD.RECEIPT).is_file())

    def test_partial_unmanaged_copy_refused(self):
        self.shared.mkdir(parents=True)
        (self.shared / "SKILL.md").write_bytes((self.source / "SKILL.md").read_bytes())
        self.assertEqual(self.invoke()[0], 1)
        self.assertEqual(list(self.shared.iterdir()), [self.shared / "SKILL.md"])

    def test_unexpected_file_refused(self):
        self.assertEqual(self.invoke()[0], 0)
        (self.shared / "notes.txt").write_text("user notes")
        self.assertEqual(self.invoke()[0], 1)
        self.assertEqual((self.shared / "notes.txt").read_text(), "user notes")

    def test_unexpected_empty_directory_refused(self):
        self.assertEqual(self.invoke()[0], 0)
        (self.shared / "my experiments").mkdir()
        self.assertEqual(self.invoke()[0], 1)
        self.assertTrue((self.shared / "my experiments").is_dir())

    def test_source_artifacts_not_copied(self):
        (self.source / "__pycache__").mkdir()
        (self.source / "__pycache__/cache.pyc").write_bytes(b"cache")
        (self.source / "transcript.jsonl").write_text("private artifact\n")
        self.assertEqual(self.invoke()[0], 0)
        self.assertFalse((self.shared / "__pycache__").exists())
        self.assertFalse((self.shared / "transcript.jsonl").exists())

    def test_copy_mode_and_preserve_existing_links(self):
        self.assertEqual(self.invoke("--copy")[0], 0)
        self.assertFalse(self.claude.is_symlink())
        self.assertEqual(self.invoke()[0], 0)
        self.assertFalse(self.claude.is_symlink())
        remove_home = self.root / "second isolated home"
        code, report = self.invoke("--home", remove_home)
        self.assertEqual(code, 0, report)
        second_claude = remove_home / ".claude/skills" / MOD.NAME
        self.assertTrue(second_claude.is_symlink())
        self.assertEqual(self.invoke("--home", remove_home, "--copy")[0], 0)
        self.assertTrue(second_claude.is_symlink())

    def test_global_plus_multiple_custom_roots(self):
        first, second = self.root / "one", self.root / "two"
        code, report = self.invoke("--global", "--skills-dir", first, "--skills-dir", second)
        self.assertEqual(code, 0, report)
        self.assertEqual(len(report["targets"]), 4)
        self.assertTrue((first / MOD.NAME / MOD.RECEIPT).is_file())
        self.assertTrue((second / MOD.NAME / MOD.RECEIPT).is_file())

    def test_existing_source_link_preserved(self):
        custom = self.root / "custom"
        custom.mkdir()
        link = custom / MOD.NAME
        link.symlink_to(self.source, target_is_directory=True)
        code, report = self.invoke("--skills-dir", custom)
        self.assertEqual(code, 0, report)
        self.assertTrue(link.is_symlink())

    def test_symlinked_ancestor_refused(self):
        outside = self.root / "outside"
        outside.mkdir()
        self.home.joinpath(".agents").symlink_to(outside, target_is_directory=True)
        code, report = self.invoke()
        self.assertEqual(code, 1, report)
        self.assertEqual(list(outside.iterdir()), [])
        self.assertEqual(report["targets"][0]["status"], "conflict")

    def test_self_source_invocation(self):
        self.assertEqual(self.invoke()[0], 0)
        before = self.state(self.shared)
        result = subprocess.run([sys.executable, str(self.shared / "scripts/install.py"),
                                 "--home", str(self.home)], cwd=self.root,
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(before, self.state(self.shared))
        self.assertEqual(json.loads(result.stdout)["targets"][0]["status"], "source")

    def test_invalid_receipt_refused(self):
        self.assertEqual(self.invoke()[0], 0)
        receipt = self.shared / MOD.RECEIPT
        receipt.write_text('{"schema": 1, "name": "foreign", "hashes": {}}')
        self.assertEqual(self.invoke()[0], 1)
        self.assertIn("foreign", receipt.read_text())

    def test_missing_source_file_refused(self):
        (self.source / "references/portability.md").unlink()
        self.assertEqual(self.invoke()[0], 1)
        self.assertEqual(list(self.home.iterdir()), [])

    def test_rollback_restores_all_old_copies(self):
        self.assertEqual(self.invoke("--copy")[0], 0)
        before_shared, before_claude = self.state(self.shared), self.state(self.claude)
        (self.source / "SKILL.md").write_text("new release\n")
        original = os.replace

        def fail_later(source, destination):
            if Path(source).name == "replacement" and Path(destination) == self.claude:
                raise OSError("injected later write failure")
            return original(source, destination)

        with mock.patch.object(MOD.os, "replace", side_effect=fail_later):
            code, report = self.invoke("--copy")
        self.assertEqual(code, 1, report)
        self.assertIn("all replacements rolled back", report["error"])
        self.assertEqual(self.state(self.shared), before_shared)
        self.assertEqual(self.state(self.claude), before_claude)
        self.assertEqual(list(self.home.rglob("." + MOD.NAME + "-install-*")), [])

    def test_failed_rollback_retains_recovery_copy(self):
        self.assertEqual(self.invoke("--copy")[0], 0)
        before_claude = self.state(self.claude)
        (self.source / "SKILL.md").write_text("new release\n")
        original = os.replace

        def fail_write_and_rollback(source, destination):
            if Path(destination) == self.claude and Path(source).name in {"replacement", "previous"}:
                raise OSError("injected failure")
            return original(source, destination)

        with mock.patch.object(MOD.os, "replace", side_effect=fail_write_and_rollback):
            code, report = self.invoke("--copy")
        self.assertEqual(code, 1, report)
        self.assertIn("rollback incomplete", report["error"])
        recovery = list(self.claude.parent.glob("." + MOD.NAME + "-install-*/previous"))
        self.assertEqual(len(recovery), 1)
        self.assertEqual(self.state(recovery[0]), before_claude)

    def test_stage_failure_does_not_mutate_destinations(self):
        self.assertEqual(self.invoke("--copy")[0], 0)
        before = self.state(self.shared)
        (self.source / "SKILL.md").write_text("new release\n")
        original = Path.write_bytes

        def fail_stage(path, data):
            if "-install-" in str(path) and path.name == "SKILL.md":
                raise OSError("injected staging failure")
            return original(path, data)

        with mock.patch.object(Path, "write_bytes", new=fail_stage):
            code, report = self.invoke("--copy")
        self.assertEqual(code, 1, report)
        self.assertEqual(self.state(self.shared), before)

    def test_outdated_shared_link_requires_global_update(self):
        self.assertEqual(self.invoke()[0], 0)
        custom = self.root / "custom"
        custom.mkdir()
        (custom / MOD.NAME).symlink_to(self.shared, target_is_directory=True)
        (self.source / "SKILL.md").write_text("new release\n")
        self.assertEqual(self.invoke("--skills-dir", custom)[0], 1)
        self.assertEqual(self.invoke("--skills-dir", custom, "--check")[0], 1)
        self.assertEqual(self.invoke("--skills-dir", custom, "--global")[0], 0)

    def test_actual_staged_bundle_install(self):
        source = INSTALLER.parents[1]
        code, report = self.invoke(source=source)
        self.assertEqual(code, 0, report)
        for name in MOD.FILES:
            self.assertEqual((self.shared / name).read_bytes(), (source / name).read_bytes())

    def test_duplicate_aliased_custom_roots_install_once(self):
        custom = self.root / "custom"
        code, report = self.invoke("--skills-dir", custom, "--skills-dir", custom / ".." / "custom")
        self.assertEqual(code, 0, report)
        self.assertEqual(len(report["targets"]), 1)

    def test_overlapping_roots_refused(self):
        custom = self.root / "custom"
        code, report = self.invoke("--skills-dir", custom, "--skills-dir", custom / MOD.NAME / "nested")
        self.assertEqual(code, 1, report)
        self.assertEqual(len(report["targets"]), 2)
        self.assertFalse(custom.exists())

    def test_dangling_ancestor_refused(self):
        custom = self.root / "custom"
        custom.symlink_to(self.root / "missing", target_is_directory=True)
        code, report = self.invoke("--skills-dir", custom)
        self.assertEqual(code, 1, report)
        self.assertTrue(custom.is_symlink())
        self.assertFalse((self.root / "missing").exists())

    def test_source_nested_under_destination_refused(self):
        nested_source = self.root / "custom" / MOD.NAME / "nested" / MOD.NAME
        shutil.copytree(self.source, nested_source)
        before = self.state(self.root / "custom" / MOD.NAME)
        code, report = self.invoke("--skills-dir", self.root / "custom", source=nested_source)
        self.assertEqual(code, 1, report)
        self.assertEqual(before, self.state(self.root / "custom" / MOD.NAME))


if __name__ == "__main__":
    unittest.main(verbosity=2)
