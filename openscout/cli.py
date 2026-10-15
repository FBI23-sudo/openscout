"""Command-line interface for OpenScout."""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests

from openscout.profiles import DEFAULT_PLATFORMS, check_profile, validate_username


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="openscout",
        description="Check a username against a curated set of public profile URLs.",
    )
    parser.add_argument("username", help="Username to check (not a real name or email).")
    parser.add_argument(
        "--platforms",
        nargs="+",
        choices=sorted(DEFAULT_PLATFORMS),
        help="Platforms to check. Defaults to all configured platforms.",
    )
    parser.add_argument("--output-dir", default="reports", help="Directory for JSON and CSV reports.")
    parser.add_argument("--delay", type=float, default=1.5, help="Minimum delay between requests in seconds (default: 1.5).")
    parser.add_argument("--timeout", type=float, default=8.0, help="Request timeout in seconds (default: 8).")
    parser.add_argument("--user-agent", default="OpenScout/0.1 (+https://github.com/yourname/openscout; public-profile-checker)",
                        help="Descriptive User-Agent. Replace the example repository URL before publishing.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        username = validate_username(args.username)
    except ValueError as exc:
        parser.error(str(exc))

    if args.delay < 1.0:
        parser.error("--delay must be at least 1.0 seconds to reduce load.")
    if not 1 <= args.timeout <= 30:
        parser.error("--timeout must be between 1 and 30 seconds.")

    selected = args.platforms or list(DEFAULT_PLATFORMS)
    session = requests.Session()
    session.headers.update({"User-Agent": args.user_agent})
    results: list[dict[str, Any]] = []

    print(f"OpenScout: checking {len(selected)} public profile URL(s) for {username!r}")
    print("This checks URL responses only; it does not prove account ownership or identity.")

    for index, platform in enumerate(selected):
        if index:
            import time
            time.sleep(args.delay)
        result = check_profile(
            username=username,
            platform=platform,
            session=session,
            timeout=args.timeout,
        )
        results.append(result)
        print(f"- {platform}: {result['status']} ({result['url']})")

    report = {
        "tool": "OpenScout",
        "version": "0.1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "username": username,
        "note": "HTTP status is an indicator only, not proof that a profile exists or belongs to a particular person.",
        "results": results,
    }

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    stem = f"openscout_{username}_{stamp}"
    json_path = output_dir / f"{stem}.json"
    csv_path = output_dir / f"{stem}.csv"

    json_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    fields = ["platform", "url", "status", "http_status", "final_url", "error"]
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(results)

    print(f"\nJSON report: {json_path}")
    print(f"CSV report:  {csv_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
