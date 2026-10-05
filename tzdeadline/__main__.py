"""tzdeadline.__main__ — command-line interface.

Usage:
    tzdeadline <datetime> <source_tz> <target_tz>
"""

from __future__ import annotations

import argparse
import sys

from tzdeadline.core.converter import ConversionError, convert
from tzdeadline.core.formatter import format_countdown, format_iso
from tzdeadline.core.parser import ParseError, parse_datetime


def build_parser() -> argparse.ArgumentParser:
    """Return the argument parser for the CLI."""
    parser = argparse.ArgumentParser(
        prog="tzdeadline",
        description="Convert a date-time from one IANA timezone to another.",
    )
    parser.add_argument("datetime", help="Date-time, e.g. '2025-12-31T23:59:00'")
    parser.add_argument("source_tz", help="Source IANA timezone, e.g. 'UTC'")
    parser.add_argument("target_tz", help="Target IANA timezone, e.g. 'Europe/Madrid'")
    return parser


def main(argv: list[str] | None = None) -> None:
    """Parse args, convert, print ISO 8601 + countdown to stdout."""
    args = build_parser().parse_args(argv)

    try:
        dt = parse_datetime(args.datetime)
    except ParseError as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)

    try:
        result = convert(dt, args.source_tz, args.target_tz)
    except ConversionError as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)
    except Exception as exc:  # defensive: never leak a traceback for bad input
        print(f"error: unexpected failure: {exc}", file=sys.stderr)
        sys.exit(1)

    print(format_iso(result.converted_dt))
    print(format_countdown(result.converted_dt))


if __name__ == "__main__":
    main()
