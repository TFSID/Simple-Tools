#!/usr/bin/env python3
"""
Remote Python Executor - Fetch and execute Python code from a URL without saving to disk.
Usage: python main.py <url> [-- script_arg1 script_arg2 ...]
"""

import sys
import argparse
import urllib.request
import urllib.error


def fetch_code(url: str) -> str:
    try:
        with urllib.request.urlopen(url, timeout=15) as response:
            return response.read().decode("utf-8")
    except urllib.error.HTTPError as e:
        print(f"[error] HTTP {e.code}: {e.reason} — {url}", file=sys.stderr)
        sys.exit(1)
    except urllib.error.URLError as e:
        print(f"[error] Failed to reach URL: {e.reason}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"[error] {e}", file=sys.stderr)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Fetch and execute a Python script from a URL.",
        epilog="Arguments after '--' are forwarded to the remote script as sys.argv.",
    )
    parser.add_argument("url", help="URL of the Python script to execute")
    parser.add_argument(
        "script_args",
        nargs=argparse.REMAINDER,
        help="Arguments forwarded to the remote script (use -- to separate)",
    )

    args = parser.parse_args()

    # Strip leading '--' separator if present
    script_args = args.script_args
    if script_args and script_args[0] == "--":
        script_args = script_args[1:]

    code = fetch_code(args.url)

    # Override sys.argv so the remote script sees its own arguments
    sys.argv = [args.url] + script_args

    exec_globals = {"__name__": "__main__", "__file__": args.url}
    try:
        exec(compile(code, args.url, "exec"), exec_globals)
    except SystemExit:
        raise
    except Exception as e:
        print(f"[error] Script raised an exception: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
