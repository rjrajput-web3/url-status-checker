#!/usr/bin/env python3
"""url-status-checker — check HTTP status codes for a list of URLs.

Dependency-free Python 3 CLI. Accepts URLs as command-line arguments or from
a text file (one URL per line), fetches each with a configurable timeout,
and prints a per-URL status line plus a summary grouped by status.

Usage:
    python url_status_checker.py https://example.com https://google.com
    python url_status_checker.py --file urls.txt --timeout 10
    python url_status_checker.py --file urls.txt --only-errors

Output example:
    [200] https://example.com (0.34s)
    [404] https://example.com/nope (0.41s)
    [ERR] https://no-such-host.invalid (dns/connection failed)
    ---
    200: 1   404: 1   ERR: 1   total: 3 in 1.20s
"""

import argparse
import concurrent.futures
import sys
import time
import urllib.request
import urllib.error
from collections import Counter


def check_one(url, timeout):
    """Return (status_label, elapsed_seconds) for a single URL."""
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    req = urllib.request.Request(url, headers={"User-Agent": "url-status-checker/1.0"})
    start = time.monotonic()
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            code = resp.status
        return url, str(code), time.monotonic() - start
    except urllib.error.HTTPError as exc:  # server answered with 4xx/5xx
        return url, str(exc.code), time.monotonic() - start
    except Exception:  # DNS failure, timeout, refused, SSL error...
        return url, "ERR", time.monotonic() - start


def load_urls(args):
    urls = list(args.urls)
    if args.file:
        with open(args.file, encoding="utf-8") as fh:
            urls += [line.strip() for line in fh if line.strip() and not line.startswith("#")]
    # de-dupe while preserving order
    seen, unique = set(), []
    for u in urls:
        if u not in seen:
            seen.add(u)
            unique.append(u)
    return unique


def main():
    ap = argparse.ArgumentParser(description="Check HTTP status codes for URLs.")
    ap.add_argument("urls", nargs="*", help="URLs to check")
    ap.add_argument("--file", "-f", help="Text file with one URL per line")
    ap.add_argument("--timeout", "-t", type=float, default=8, help="Per-request timeout in seconds (default 8)")
    ap.add_argument("--workers", "-w", type=int, default=8, help="Parallel workers (default 8)")
    ap.add_argument("--only-errors", action="store_true", help="Only print non-2xx results")
    args = ap.parse_args()

    urls = load_urls(args)
    if not urls:
        ap.error("no URLs given — pass some on the command line or with --file")

    overall_start = time.monotonic()
    counts = Counter()
    with concurrent.futures.ThreadPoolExecutor(max_workers=max(1, args.workers)) as pool:
        futures = {pool.submit(check_one, u, args.timeout): u for u in urls}
        for fut in concurrent.futures.as_completed(futures):
            url, status, elapsed = fut.result()
            counts[status] += 1
            if args.only_errors and status.startswith("2"):
                continue
            print(f"[{status}] {url} ({elapsed:.2f}s)")

    total = time.monotonic() - overall_start
    summary = "   ".join(f"{k}: {v}" for k, v in sorted(counts.items()))
    print("---")
    print(f"{summary}   total: {len(urls)} in {total:.2f}s")


if __name__ == "__main__":
    main()
