#!/usr/bin/env python3
"""
Cross-check db/full-dump.sql vs docker/db-migrations/sql/*.
Reports which migration-defined tables already exist in the dump (CREATE TABLE public.<name>).
"""
from __future__ import annotations

import re
import sys
from pathlib import Path
from collections import defaultdict

ROOT = Path(__file__).resolve().parents[1]
DUMP = ROOT / "db" / "full-dump.sql"
MIGRATIONS = ROOT / "docker" / "db-migrations" / "sql"

# pg_dump style: CREATE TABLE public.foo (
CREATE_DUMP = re.compile(
    r"^CREATE TABLE (?:public\.)?\"?([a-zA-Z0-9_]+)\"?\s*\(",
    re.IGNORECASE | re.MULTILINE,
)

# Migration files: CREATE TABLE [IF NOT EXISTS] [[schema].]name
CREATE_MIG = re.compile(
    r"CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?(?:([a-zA-Z0-9_]+)\.)?\"?([a-zA-Z0-9_]+)\"?\s*\(",
    re.IGNORECASE,
)


def tables_in_dump(text: str) -> set[str]:
    found: set[str] = set()
    for m in CREATE_DUMP.finditer(text):
        name = m.group(1)
        if name:
            found.add(name.lower())
    return found


def scan_migration_sql(service_dir: Path) -> dict[str, set[str]]:
    """Return rel_path -> set of table names (lowercase, unqualified)."""
    out: dict[str, set[str]] = defaultdict(set)
    for path in sorted(service_dir.rglob("*.sql")):
        body = path.read_text(encoding="utf-8", errors="replace")
        for m in CREATE_MIG.finditer(body):
            schema, name = m.group(1), m.group(2)
            if schema and schema.lower() != "public":
                continue
            out[str(path.relative_to(service_dir))].add(name.lower())
    return dict(out)


def main() -> int:
    if not DUMP.is_file():
        print(f"Missing dump: {DUMP}", file=sys.stderr)
        return 1
    if not MIGRATIONS.is_dir():
        print(f"Missing migrations dir: {MIGRATIONS}", file=sys.stderr)
        return 1

    dump_tables = tables_in_dump(DUMP.read_text(encoding="utf-8", errors="replace"))
    print(f"Dump: {DUMP}  ({len(dump_tables)} CREATE TABLE names in public / unquoted)\n")

    for svc in sorted(p.name for p in MIGRATIONS.iterdir() if p.is_dir()):
        svc_path = MIGRATIONS / svc
        by_file = scan_migration_sql(svc_path)
        all_names: set[str] = set()
        for names in by_file.values():
            all_names |= names

        in_dump = sorted(n for n in all_names if n in dump_tables)
        not_in_dump = sorted(n for n in all_names if n not in dump_tables)

        print(f"=== {svc} ===")
        if not all_names:
            print("  (no CREATE TABLE patterns found)\n")
            continue
        print(f"  tables from migrations: {len(all_names)}")
        if in_dump:
            print(f"  also in full-dump.sql: {', '.join(in_dump)}")
        if not_in_dump:
            print(f"  not in full-dump.sql: {', '.join(not_in_dump)}")
        print()

    # Explicit collision note for public.service
    if "service" in dump_tables:
        print(
            "NOTE: dump defines public.service (access-control / module registry shape). "
            "public-service migrations also target unqualified `service`; "
            "CREATE TABLE IF NOT EXISTS service will no-op if that name is already taken — "
            "verify column/FK compatibility with studio public-service."
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
