#!/usr/bin/env python3
"""Reference guide for MySQL -> PostgreSQL migration rehearsal.

This script is intentionally non-destructive. It prints the recommended
migration sequence, type mappings, and sample SQL snippets for the Java ->
Python backend cutover. It is not a production migration utility.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from textwrap import dedent


@dataclass(frozen=True)
class TypeMapping:
    mysql_type: str
    postgres_type: str
    notes: str


TYPE_MAPPINGS = [
    TypeMapping("BIGINT / BigInteger id", "BIGINT", "Preserve Java identifiers exactly; do not re-sequence existing IDs."),
    TypeMapping("TEXT with JSON payload", "JSONB", "Validate JSON before load; convert invalid legacy text to a documented exception list."),
    TypeMapping("DATETIME / TIMESTAMP", "BIGINT epoch millis or TIMESTAMPTZ", "Current Python compatibility layer stores time values as epoch millis in API-facing records where applicable."),
    TypeMapping("TINYINT(1)", "BOOLEAN", "Normalize 0/1 flags during load."),
    TypeMapping("VARCHAR / TEXT", "VARCHAR / TEXT", "Preserve UTF-8 and trim unexpected NUL bytes before insert."),
]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Print the reference migration plan for MySQL -> PostgreSQL cutover rehearsal.")
    parser.add_argument("--table", action="append", default=[], help="Limit printed sample SQL to the specified table name(s).")
    parser.add_argument("--mysql-dsn", help="Optional MySQL DSN for operator notes only. No live connection is attempted.")
    parser.add_argument("--postgres-dsn", help="Optional PostgreSQL DSN for operator notes only. No live connection is attempted.")
    parser.add_argument("--dry-run", action="store_true", help="Print the plan and sample statements without executing anything.")
    parser.add_argument("--json", action="store_true", help="Render the guide in JSON for automation wrappers.")
    return parser


def build_sample_sql(table: str) -> dict[str, str]:
    return {
        "extract_mysql": dedent(
            f"""
            SELECT *
            FROM {table}
            ORDER BY id;
            """
        ).strip(),
        "transform_notes": dedent(
            """
            - keep BIGINT ids unchanged
            - cast JSON text columns with json.loads(...) before INSERT
            - convert datetime columns to int(dt.timestamp() * 1000)
            - coerce tinyint flags to bool
            """
        ).strip(),
        "load_postgres": dedent(
            f"""
            INSERT INTO {table} (...)
            VALUES (...)
            ON CONFLICT (id) DO UPDATE SET ...;
            """
        ).strip(),
        "verify_counts": dedent(
            f"""
            SELECT COUNT(*) AS mysql_count FROM {table};
            SELECT COUNT(*) AS postgres_count FROM {table};
            """
        ).strip(),
    }


def render_text(args: argparse.Namespace) -> str:
    tables = args.table or [
        "core_datasource",
        "core_dataset_group",
        "core_chart_view",
        "core_visualization_info",
        "core_share_info",
        "core_export_task",
    ]
    mappings = "\n".join(
        f"- {item.mysql_type} -> {item.postgres_type}: {item.notes}" for item in TYPE_MAPPINGS
    )
    samples = "\n\n".join(
        dedent(
            f"""
            ## Table: {table}
            MySQL extract:
            {build_sample_sql(table)['extract_mysql']}

            Transform notes:
            {build_sample_sql(table)['transform_notes']}

            PostgreSQL upsert sketch:
            {build_sample_sql(table)['load_postgres']}

            Verification:
            {build_sample_sql(table)['verify_counts']}
            """
        ).strip()
        for table in tables
    )
    return dedent(
        f"""
        PyDataEase data migration reference
        ==================================

        Dry run: {args.dry_run or True}
        MySQL DSN provided: {'yes' if args.mysql_dsn else 'no'}
        PostgreSQL DSN provided: {'yes' if args.postgres_dsn else 'no'}

        Recommended sequence
        1. Freeze writes on Java/MySQL.
        2. Capture final backup/snapshot timestamps.
        3. Run Alembic migrations on PostgreSQL.
        4. Export source rows in deterministic id order.
        5. Transform types using the mappings below.
        6. Load into PostgreSQL with id-preserving upserts.
        7. Compare row counts and spot-check critical entities.
        8. Keep the run in dry-run/rehearsal mode unless a separately approved loader is used.

        Type mappings
        {mappings}

        Important notes
        - This script does not connect to MySQL because no MySQL driver is bundled in the repo.
        - If live extraction is required, use an approved external export tool or MySQL dump pipeline.
        - Store any table-specific exceptions in the cutover evidence log.

        Sample SQL and transform checklist
        {samples}
        """
    ).strip()


def render_json(args: argparse.Namespace) -> str:
    tables = args.table or ["core_datasource", "core_dataset_group", "core_chart_view", "core_visualization_info"]
    payload = {
        "dry_run": True,
        "notes": [
            "reference-only helper",
            "preserve BIGINT ids",
            "convert JSON text to JSONB",
            "convert datetimes to epoch millis where the compatibility layer expects numeric timestamps",
        ],
        "type_mappings": [item.__dict__ for item in TYPE_MAPPINGS],
        "tables": {table: build_sample_sql(table) for table in tables},
    }
    return json.dumps(payload, indent=2, ensure_ascii=False)


def main() -> None:
    args = build_parser().parse_args()
    output = render_json(args) if args.json else render_text(args)
    print(output)


if __name__ == "__main__":
    main()
