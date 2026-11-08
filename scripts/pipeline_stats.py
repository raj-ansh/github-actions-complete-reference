"""Summarize recent workflow runs for a repository.

Usage: python scripts/pipeline_stats.py OWNER/REPO [WORKFLOW_FILE]

Set GITHUB_TOKEN to read private repositories or to raise rate limits.
"""

import json
import os
import statistics
import sys
import urllib.request
from collections import Counter
from datetime import datetime

API = "https://api.github.com"
STALLED_MINUTES = 24 * 60


def fetch_runs(repository: str, workflow: str | None) -> list[dict[str, str]]:
    path = f"/repos/{repository}/actions"
    path += f"/workflows/{workflow}/runs" if workflow else "/runs"
    request = urllib.request.Request(  # noqa: S310 - fixed https host
        f"{API}{path}?per_page=100&status=completed",
        headers={"Accept": "application/vnd.github+json"},
    )
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        request.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(request, timeout=30) as response:  # noqa: S310
        runs: list[dict[str, str]] = json.load(response)["workflow_runs"]
    return runs


def minutes(run: dict[str, str]) -> float:
    started = datetime.fromisoformat(run["run_started_at"])
    finished = datetime.fromisoformat(run["updated_at"])
    return (finished - started).total_seconds() / 60


def summarize(runs: list[dict[str, str]]) -> str:
    # Runs that never really ran would distort every number, so count them
    # separately: some wait for approval, and some sit until they expire.
    stalled = [
        run
        for run in runs
        if run["conclusion"] == "action_required" or minutes(run) > STALLED_MINUTES
    ]
    timed = [run for run in runs if run not in stalled]
    if not timed:
        return "No completed runs found."
    conclusions = Counter(run["conclusion"] for run in timed)
    durations = sorted(minutes(run) for run in timed)
    p95 = durations[min(int(len(durations) * 0.95), len(durations) - 1)]
    success = conclusions["success"] / len(timed)
    lines = [
        f"Runs analyzed:   {len(timed)}",
        f"Stalled, left out: {len(stalled)}",
        f"Success rate:    {success:.0%}",
        f"Median duration: {statistics.median(durations):.1f} min",
        f"95th percentile: {p95:.1f} min",
        "Conclusions:     "
        + ", ".join(f"{name}={n}" for name, n in conclusions.most_common()),
    ]
    return "\n".join(lines)


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    workflow = sys.argv[2] if len(sys.argv) > 2 else None
    print(summarize(fetch_runs(sys.argv[1], workflow)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
