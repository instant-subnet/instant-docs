#!/usr/bin/env python3
"""Run the Instant Docs five-minute Git updater."""

from __future__ import annotations

import argparse
import logging
import subprocess
import sys
import time
from datetime import timedelta
from pathlib import Path


log = logging.getLogger(__name__)
UPDATES_CHECK_TIME = timedelta(minutes=5)
PROJECT_ROOT = Path(__file__).resolve().parent.parent


def get_version() -> str:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        check=True,
        capture_output=True,
        cwd=PROJECT_ROOT,
        text=True,
    )
    commit = result.stdout.strip()
    if len(commit) != 40:
        raise RuntimeError(f"invalid Git commit: {commit}")
    return commit


def pull_latest_version() -> None:
    try:
        subprocess.run(
            ["git", "pull", "--rebase", "--autostash"],
            check=True,
            cwd=PROJECT_ROOT,
        )
    except subprocess.CalledProcessError as error:
        log.error("Failed to pull, reverting: %s", error)
        subprocess.run(
            ["git", "rebase", "--abort"],
            check=False,
            cwd=PROJECT_ROOT,
        )


def validate_site() -> None:
    subprocess.run(
        [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"],
        check=True,
        cwd=PROJECT_ROOT,
    )


def update_once(current_version: str, *, force: bool = False) -> str:
    pull_latest_version()
    latest_version = get_version()
    if not force and latest_version == current_version:
        log.debug("No update, current: %s", current_version[:8])
        return current_version
    log.info("Docs update: %s -> %s", current_version[:8], latest_version[:8])
    try:
        validate_site()
    except subprocess.CalledProcessError as error:
        log.error("Docs validation failed: %s", error)
        return current_version
    log.info("Docs validated at version: %s", latest_version[:8])
    return latest_version


def main(*, once: bool = False) -> None:
    current_version = get_version()
    log.info("Docs updater started, version: %s", current_version[:8])
    if once:
        updated = update_once(current_version, force=True)
        if updated != get_version():
            raise SystemExit(1)
        return
    while True:
        time.sleep(UPDATES_CHECK_TIME.total_seconds())
        current_version = update_once(current_version)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )
    parser = argparse.ArgumentParser(description="Instant Docs auto-updater")
    parser.add_argument(
        "--once",
        action="store_true",
        help="run one pull-and-validation cycle, then exit",
    )
    main(once=parser.parse_args().once)
