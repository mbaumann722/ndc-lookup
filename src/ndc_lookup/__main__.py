"""CLI entry point: `python -m ndc_lookup <command> ...`"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .client import OpenFDAError
from .validate import read_ndc_column, validate_batch, validate_one, write_report


def cmd_check(args: argparse.Namespace) -> int:
    result = validate_one(args.ndc)
    print(f"{result.ndc}: {result.status}")
    if result.brand_name:
        print(f"  brand: {result.brand_name}  labeler: {result.labeler_name}")
    if result.note:
        print(f"  note: {result.note}")
    return 0


def cmd_batch(args: argparse.Namespace) -> int:
    codes = read_ndc_column(Path(args.csv_path), column=args.column)
    print(f"Validating {len(codes)} codes from {args.csv_path} ...")
    results = list(validate_batch(codes))

    out_path = Path(args.out) if args.out else Path(args.csv_path).with_suffix(".report.csv")
    write_report(results, out_path)

    counts: dict[str, int] = {}
    for r in results:
        counts[r.status] = counts.get(r.status, 0) + 1
    print("Summary:", counts)
    print(f"Full report written to {out_path}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="ndc-lookup")
    sub = parser.add_subparsers(dest="command", required=True)

    p_check = sub.add_parser("check", help="Look up a single NDC code")
    p_check.add_argument("ndc", help="e.g. 0069-3060-04")
    p_check.set_defaults(func=cmd_check)

    p_batch = sub.add_parser("batch", help="Validate a CSV column of NDC codes")
    p_batch.add_argument("csv_path")
    p_batch.add_argument("--column", default="ndc")
    p_batch.add_argument("--out", default=None)
    p_batch.set_defaults(func=cmd_batch)

    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except OpenFDAError as e:
        print(f"openFDA error: {e}", file=sys.stderr)
        return 1
    except (ValueError, FileNotFoundError) as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
