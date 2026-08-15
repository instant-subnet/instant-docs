"""Check public content and the tracked text-line ceiling."""

from __future__ import annotations

import re
import subprocess
from ipaddress import ip_address
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LINE_LIMIT = 10_000
TEXT_MIME_TYPES = {
    "application/javascript",
    "application/json",
    "application/x-empty",
    "image/svg+xml",
}
FORBIDDEN = {
    "internal planning language": re.compile(
        r"\b(?:closeout|cutover|go-live|goal(?:s)?|handoff|milestone(?:s)?|mvp|"
        r"phase(?:s)?|progress|roadmap)\b",
        re.I,
    ),
    "localnet": re.compile(r"\blocalnet\b", re.I),
    "private hostname": re.compile(
        r"(?:https?|wss?)://[^\s/]+\.(?:internal|lan|local)(?::\d+)?(?:[/\s]|$)", re.I
    ),
}
IPV4 = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")


def tracked_files() -> list[Path]:
    output = subprocess.check_output(
        ["git", "ls-files", "-c", "-o", "--exclude-standard", "-z"], cwd=ROOT
    ).decode()
    return [Path(item) for item in output.split("\0") if item and (ROOT / item).is_file()]


def is_text(path: Path) -> bool:
    mime = subprocess.check_output(["file", "-b", "--mime-type", path], text=True).strip()
    return mime.startswith("text/") or mime in TEXT_MIME_TYPES


def main() -> int:
    failures: list[str] = []
    line_count = 0
    for relative in tracked_files():
        path = ROOT / relative
        if not is_text(path):
            continue
        data = path.read_bytes()
        line_count += data.count(b"\n") + int(bool(data) and not data.endswith(b"\n"))
        if relative == Path("scripts/check_repository.py"):
            continue
        text = data.decode("utf-8")
        for label, pattern in FORBIDDEN.items():
            if pattern.search(text):
                failures.append(f"{label}: {relative}")
        for match in IPV4.finditer(text):
            try:
                address = ip_address(match.group())
            except ValueError:
                continue
            if not address.is_loopback:
                failures.append(f"non-loopback IP address: {relative}")
                break
    if line_count > LINE_LIMIT:
        failures.append(f"tracked line count {line_count} exceeds {LINE_LIMIT}")
    if failures:
        print("repository guard failed:")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print(f"repository guard passed: {line_count} tracked lines (<= {LINE_LIMIT})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
