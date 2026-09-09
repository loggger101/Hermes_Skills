"""Verify the sqlite-queries skill's documented workflow against real SQLite behavior.

Every test asserts a claim SKILL.md makes (workflow steps, quick-reference
commands, or pitfall notes) — so if SQLite semantics ever shift under us, this
suite goes red instead of the skill silently teaching wrong commands.

Stdlib only: no new CI dependencies needed. The sqlite3 CLI is exercised via
subprocess where a claim is about the CLI itself; those tests skip cleanly on
hosts without it (CI runs ubuntu-latest, which ships it).
"""
import csv
import json
import shutil
import sqlite3
import subprocess

import pytest

HAS_CLI = shutil.which("sqlite3") is not None


def q(db_path, sql):
    con = sqlite3.connect(str(db_path))
    try:
        return con.execute(sql).fetchall()
    finally:
        con.close()


# --- Step 1: locate & verify -------------------------------------------------

def test_integrity_check_returns_ok(db_path):
    """SKILL.md step 1: PRAGMA integrity_check returns 'ok' on healthy DBs."""
    assert q(db_path, "PRAGMA integrity_check;") == [("ok",)]


# --- Step 2: discover the schema ---------------------------------------------

def test_schema_discovery_lists_both_tables(db_path):
    rows = q(
        db_path,
        "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;",
    )
    assert [r[0] for r in rows] == ["orders", "users"]


def test_foreign_key_list_reports_orders_user_fk(db_path):
    """SKILL.md step 2: PRAGMA foreign_key_list(t) surfaces FKs on a table."""
    fks = q(db_path, "PRAGMA foreign_key_list(orders);")
    # (id, seq, table, from, to, on_update, on_delete, match)
    assert len(fks) == 1 and fks[0][2] == "users" and fks[0][3] == "user_id"


def test_index_list_reports_created_index(db_path):
    idx = q(db_path, "PRAGMA index_list(orders);")
    names = {r[1] for r in idx}
    assert "idx_orders_user" in names


# --- Step 3: run the query ----------------------------------------------------

def test_row_counts_per_table_via_union_pattern(db_path):
    """SKILL.md step 3 / Pitfall #1: count rows per table with UNION ALL of real tables."""
    rows = q(
        db_path,
        "SELECT 'users', COUNT(*) FROM users UNION ALL SELECT 'orders', COUNT(*) FROM orders;",
    )
    assert dict(rows) == {"users": 3, "orders": 4}


def test_sqlite_master_is_schema_not_rows(db_path):
    """Pitfall #1: sqlite_master lists schema objects — counting it is the documented mistake."""
    n_objects = q(
        db_path, "SELECT COUNT(*) FROM sqlite_master WHERE type='table';"
    )[0][0]
    assert n_objects == 2  # two tables; NOT a row count of anything


def test_query_plan_uses_index(db_path):
    """SKILL.md quick ref: EXPLAIN QUERY PLAN — the created index must actually be used."""
    plan = " ".join(
        r[-1] for r in q(db_path, "EXPLAIN QUERY PLAN SELECT * FROM orders WHERE user_id=2;")
    )
    assert "idx_orders_user" in plan


# --- Step 4: export ------------------------------------------------------------

def test_csv_export_roundtrip(tmp_path, db_path):
    """SKILL.md step 4: export to CSV (header + rows), then read it back."""
    out = tmp_path / "users.csv"
    con = sqlite3.connect(str(db_path))
    try:
        cur = con.execute("SELECT id, name, email FROM users ORDER BY id;")
        with open(out, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow([d[0] for d in cur.description])  # -header equivalent
            w.writerows(cur.fetchall())
    finally:
        con.close()
    with open(out, newline="", encoding="utf-8") as f:
        rows = list(csv.reader(f))
    assert rows[0] == ["id", "name", "email"]  # header present (Verification step)
    assert len(rows) == 4 and rows[1][2] == "ada@example.com"


def test_json_export_roundtrip(db_path):
    """SKILL.md step 4: JSON export — SQLite's json() is the stdlib equivalent of -json."""
    raw = q(
        db_path,
        "SELECT json_group_array(json_object('id', id, 'name', name)) FROM users ORDER BY id;",
    )[0][0]
    data = json.loads(raw)
    assert [d["id"] for d in data] == [1, 2, 3]


# --- Step 5: modify with transactions + backup ---------------------------------

def test_transaction_commit_persists(db_path):
    """SKILL.md step 5: BEGIN/COMMIT multi-statement change survives re-open."""
    con = sqlite3.connect(str(db_path))
    try:
        con.execute("BEGIN")
        con.execute("INSERT INTO users VALUES (4, 'Katherine', 'k@example.com')")
        con.execute("UPDATE orders SET amount=10.0 WHERE id=12;")
        con.commit()
    finally:
        con.close()
    assert q(db_path, "SELECT COUNT(*) FROM users;")[0][0] == 4
    assert q(db_path, "SELECT amount FROM orders WHERE id=12;")[0][0] == 10.0


def test_transaction_rollback_discards(tmp_path):
    """A failed multi-statement batch must be rollable — the reason transactions exist."""
    p = tmp_path / "tx.db"
    con = sqlite3.connect(str(p))
    try:
        con.execute("CREATE TABLE t (x INTEGER)")
        con.commit()
        con.execute("BEGIN")
        con.execute("INSERT INTO t VALUES (1)")
        con.rollback()  # simulate the failure path before COMMIT
        assert con.execute("SELECT COUNT(*) FROM t").fetchone()[0] == 0
    finally:
        con.close()


def test_backup_copy_is_independent(db_path, tmp_path):
    """SKILL.md step 5 / Pitfall #8: back up by copying the file; verify it works."""
    bak = str(tmp_path / "backup.db")
    shutil.copyfile(str(db_path), bak)
    con = sqlite3.connect(str(db_path))
    try:
        con.execute("DELETE FROM users WHERE id=1")  # destructive change on original
        con.commit()
    finally:
        con.close()
    assert q(bak, "SELECT COUNT(*) FROM users;")[0][0] == 3   # backup intact
    assert q(db_path, "SELECT COUNT(*) FROM users;")[0][0] == 2


# --- CSV import pitfall ---------------------------------------------------------

def test_csv_import_values_arrive_as_text_no_type_inference(sample_csv):
    """Pitfall #2: .import builds a missing table from the CSV header and loads values as text —
    non-numeric data ends up all TEXT, which is exactly why the skill says to check the schema
    after import (what you get depends on the source data, not on your intent)."""
    con = sqlite3.connect(":memory:")
    try:
        cur = con.cursor()
        rows = list(csv.reader(open(sample_csv, newline="", encoding="utf-8")))
        header, data = rows[0], rows[1:]
        # .import into a missing table declares the columns from the header — no types inferred
        cur.execute(f"CREATE TABLE imported ({', '.join(header)})")  # untyped -> NUMERIC affinity
        for r in data:  # values arrive as text, exactly like .import delivers them
            cur.execute(
                f"INSERT INTO imported VALUES ({', '.join('?' * len(r))})", [c.strip() for c in r]
            )
        con.commit()
        kinds = {r[0]: r[1] for r in cur.execute("SELECT code, typeof(code) FROM imported;")}
        assert set(kinds.values()) == {"text"}  # non-numeric data -> all TEXT (the gotcha)
    finally:
        con.close()


@pytest.mark.skipif(not HAS_CLI, reason="sqlite3 CLI not installed on this host")
def test_cli_import_creates_table_from_header(sample_csv):
    """Pitfall #2 (CLI-verified in CI): .import into a missing table creates it using the CSV
    header as column names and loads every row — then you must check what types came out."""
    db = sample_csv + ".db"  # fresh empty DB next to the fixture CSV
    subprocess.run(
        ["sqlite3", db, f".mode csv\n.import {sample_csv} imported"],
        capture_output=True, text=True, check=True,
    )
    cols = [r[1] for r in q(db, "PRAGMA table_info(imported);")]
    assert cols == ["code", "label"]  # header row became the column names
    assert q(db, "SELECT COUNT(*) FROM imported;")[0][0] == 3


# --- date handling pitfall --------------------------------------------------------

def test_iso8601_text_dates_compare_correctly(db_path):
    """Pitfall #3: dates as ISO-8601 TEXT compare correctly when format is consistent."""
    rows = q(
        db_path, "SELECT id FROM orders WHERE created_at >= '2026-02-01T00:00:00Z' ORDER BY id;"
    )
    assert [r[0] for r in rows] == [13]


# --- duplicate / missing-value checks (When to Use) --------------------------------

def test_duplicate_detection_query(db_path):
    """SKILL.md 'When to Use': find duplicates — the GROUP BY/HAVING pattern works."""
    dupes = q(
        db_path, "SELECT email FROM users GROUP BY email HAVING COUNT(*) > 1;"
    )
    assert dupes == []  # fixture has unique emails (UNIQUE constraint)


def test_missing_value_detection(db_path):
    rows = q(db_path, "SELECT COUNT(*) FROM orders WHERE amount IS NULL;")
    assert rows[0][0] == 0


# --- CLI-level claims (skip when sqlite3 binary absent) -------------------------------

@pytest.mark.skipif(not HAS_CLI, reason="sqlite3 CLI not installed on this host")
def test_cli_dot_commands_are_not_sql(db_path):
    """Pitfall #4: dot-commands go to the shell directly; SQL goes inside quotes."""
    out = subprocess.run(
        ["sqlite3", str(db_path), ".tables"], capture_output=True, text=True, check=True
    ).stdout
    assert "users" in out and "orders" in out


@pytest.mark.skipif(not HAS_CLI, reason="sqlite3 CLI not installed on this host")
def test_cli_header_csv_flag_shape(db_path):
    """Quick ref: `sqlite3 -header -csv db "SELECT ..."` emits header + CSV rows."""
    out = subprocess.run(
        ["sqlite3", "-header", "-csv", str(db_path), "SELECT id, name FROM users ORDER BY id;"],
        capture_output=True, text=True, check=True,
    ).stdout.strip().splitlines()
    assert out[0] == "id,name" and len(out) == 4


@pytest.mark.skipif(not HAS_CLI, reason="sqlite3 CLI not installed on this host")
def test_cli_json_flag_requires_338(db_path):
    """Pitfall #5: -json exists only in SQLite >= 3.38; CI's sqlite ships it."""
    out = subprocess.run(
        ["sqlite3", "-json", str(db_path), "SELECT id FROM users ORDER BY id LIMIT 2;"],
        capture_output=True, text=True, check=True,
    ).stdout
    assert [r["id"] for r in json.loads(out)] == [1, 2]
