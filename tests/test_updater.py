from __future__ import annotations

import importlib.util
import subprocess
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "instant_docs_updater", ROOT / "scripts" / "start_docs.py"
)
assert SPEC and SPEC.loader
updater = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(updater)


class UpdaterTests(unittest.TestCase):
    def test_pull_uses_the_proven_rebase_autostash_cycle(self) -> None:
        with mock.patch.object(updater.subprocess, "run") as run:
            updater.pull_latest_version()
        run.assert_called_once_with(
            ["git", "pull", "--rebase", "--autostash"],
            check=True,
            cwd=updater.PROJECT_ROOT,
        )

    def test_changed_commit_is_validated(self) -> None:
        with (
            mock.patch.object(updater, "pull_latest_version"),
            mock.patch.object(updater, "get_version", return_value="b" * 40),
            mock.patch.object(updater, "validate_site") as validate,
        ):
            self.assertEqual(updater.update_once("a" * 40), "b" * 40)
        validate.assert_called_once_with()

    def test_unchanged_commit_does_not_repeat_validation(self) -> None:
        with (
            mock.patch.object(updater, "pull_latest_version"),
            mock.patch.object(updater, "get_version", return_value="a" * 40),
            mock.patch.object(updater, "validate_site") as validate,
        ):
            self.assertEqual(updater.update_once("a" * 40), "a" * 40)
        validate.assert_not_called()

    def test_validation_failure_retries_the_changed_commit(self) -> None:
        with (
            mock.patch.object(updater, "pull_latest_version"),
            mock.patch.object(updater, "get_version", return_value="b" * 40),
            mock.patch.object(
                updater,
                "validate_site",
                side_effect=subprocess.CalledProcessError(1, ["unittest"]),
            ),
        ):
            self.assertEqual(updater.update_once("a" * 40), "a" * 40)

    def test_manual_cycle_validates_even_without_a_new_commit(self) -> None:
        with (
            mock.patch.object(updater, "pull_latest_version"),
            mock.patch.object(updater, "get_version", return_value="a" * 40),
            mock.patch.object(updater, "validate_site") as validate,
        ):
            self.assertEqual(updater.update_once("a" * 40, force=True), "a" * 40)
        validate.assert_called_once_with()


if __name__ == "__main__":
    unittest.main()
