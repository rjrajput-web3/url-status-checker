# url-status-checker

A dependency-free Python 3 CLI that checks HTTP status codes for a list of URLs — handy for broken-link audits, uptime spot-checks, and sitemap verification. Standard library only: no pip installs.

## What it does

- Takes URLs from the command line or a text file (one per line)
- Fetches each URL in parallel with a configurable timeout
- Prints a status line per URL, then a summary grouped by status code
- Counts connection/DNS/timeout failures as `ERR` instead of crashing

## How to run

```bash
# Check a few URLs
python url_status_checker.py https://example.com https://google.com

# Check every URL in a file
python url_status_checker.py --file urls.txt

# Longer timeout, more parallelism, only show failures
python url_status_checker.py --file urls.txt --timeout 15 --workers 12 --only-errors
```

Lines starting with `#` in the input file are ignored. URLs without a scheme get `https://` added.

## Example output

```
[200] https://example.com (0.34s)
[404] https://example.com/nope (0.41s)
[ERR] https://no-such-host.invalid (0.12s)
---
200: 1   404: 1   ERR: 1   total: 3 in 0.95s
```

## Options

| Flag | Default | Meaning |
|---|---|---|
| `--file`, `-f` | — | File with one URL per line |
| `--timeout`, `-t` | 8 | Per-request timeout (seconds) |
| `--workers`, `-w` | 8 | Parallel workers |
| `--only-errors` | off | Only print non-2xx results |

## Requirements

Python 3.8+. Nothing else.

## License

MIT.
