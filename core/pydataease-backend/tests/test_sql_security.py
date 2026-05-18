from __future__ import annotations

import pytest
from fastapi import HTTPException  # pyright: ignore[reportMissingImports]

from app.services.sql_executor import (  # pyright: ignore[reportImplicitRelativeImport]
    _sanitize_sql,
    apply_limit,
    validate_readonly_sql,
)


class TestValidateReadonlySql:
    def test_accepts_simple_select_query(self) -> None:
        assert validate_readonly_sql("SELECT * FROM metrics") == "SELECT * FROM metrics"

    def test_accepts_select_query_with_whitespace(self) -> None:
        assert validate_readonly_sql("  SELECT 1  ") == "SELECT 1"

    def test_accepts_with_cte_query(self) -> None:
        sql = "WITH recent AS (SELECT 1 AS id) SELECT id FROM recent"
        assert validate_readonly_sql(sql) == sql

    def test_accepts_complex_select_with_join(self) -> None:
        sql = "SELECT a.id FROM accounts a JOIN orgs o ON o.id = a.org_id"
        assert validate_readonly_sql(sql) == sql

    def test_accepts_complex_select_with_subquery(self) -> None:
        sql = "SELECT * FROM (SELECT id FROM metrics) t"
        assert validate_readonly_sql(sql) == sql

    def test_accepts_complex_select_with_union(self) -> None:
        sql = "SELECT id FROM a UNION SELECT id FROM b"
        assert validate_readonly_sql(sql) == sql

    def test_accepts_trailing_semicolon(self) -> None:
        assert validate_readonly_sql("SELECT 1;") == "SELECT 1"

    def test_accepts_multiple_trailing_semicolons(self) -> None:
        assert validate_readonly_sql("SELECT 1;;;  ") == "SELECT 1"

    def test_rejects_empty_sql(self) -> None:
        with pytest.raises(HTTPException, match="SQL must not be empty"):
            validate_readonly_sql("  ;  ")

    def test_rejects_insert(self) -> None:
        with pytest.raises(HTTPException, match="Only SELECT queries are allowed"):
            validate_readonly_sql("INSERT INTO t VALUES (1)")

    def test_rejects_update(self) -> None:
        with pytest.raises(HTTPException, match="Only SELECT queries are allowed"):
            validate_readonly_sql("UPDATE t SET a = 1")

    def test_rejects_delete(self) -> None:
        with pytest.raises(HTTPException, match="Only SELECT queries are allowed"):
            validate_readonly_sql("DELETE FROM t")

    def test_rejects_drop(self) -> None:
        with pytest.raises(HTTPException, match="Only SELECT queries are allowed"):
            validate_readonly_sql("DROP TABLE t")

    def test_rejects_alter(self) -> None:
        with pytest.raises(HTTPException, match="Only SELECT queries are allowed"):
            validate_readonly_sql("ALTER TABLE t ADD COLUMN x INT")

    def test_rejects_create(self) -> None:
        with pytest.raises(HTTPException, match="Only SELECT queries are allowed"):
            validate_readonly_sql("CREATE TABLE t(id INT)")

    def test_rejects_truncate(self) -> None:
        with pytest.raises(HTTPException, match="Only SELECT queries are allowed"):
            validate_readonly_sql("TRUNCATE TABLE t")

    def test_rejects_grant(self) -> None:
        with pytest.raises(HTTPException, match="Only SELECT queries are allowed"):
            validate_readonly_sql("GRANT SELECT ON t TO user_a")

    def test_rejects_revoke(self) -> None:
        with pytest.raises(HTTPException, match="Only SELECT queries are allowed"):
            validate_readonly_sql("REVOKE SELECT ON t FROM user_a")

    def test_rejects_merge(self) -> None:
        with pytest.raises(HTTPException, match="Only SELECT queries are allowed"):
            validate_readonly_sql("MERGE INTO t USING s ON t.id = s.id")

    def test_rejects_call(self) -> None:
        with pytest.raises(HTTPException, match="Only SELECT queries are allowed"):
            validate_readonly_sql("CALL dangerous_proc()")

    def test_rejects_copy(self) -> None:
        with pytest.raises(HTTPException, match="Only SELECT queries are allowed"):
            validate_readonly_sql("COPY users TO '/tmp/users.csv'")

    def test_rejects_vacuum(self) -> None:
        with pytest.raises(HTTPException, match="Only SELECT queries are allowed"):
            validate_readonly_sql("VACUUM")

    def test_rejects_analyze(self) -> None:
        with pytest.raises(HTTPException, match="Only SELECT queries are allowed"):
            validate_readonly_sql("ANALYZE users")

    def test_rejects_comment_keyword_statement(self) -> None:
        with pytest.raises(HTTPException, match="Only SELECT queries are allowed"):
            validate_readonly_sql("COMMENT ON TABLE users IS 'x'")

    def test_rejects_execute(self) -> None:
        with pytest.raises(HTTPException, match="Only SELECT queries are allowed"):
            validate_readonly_sql("EXECUTE dangerous_plan")

    def test_rejects_multi_statement_injection(self) -> None:
        with pytest.raises(HTTPException, match="Only a single SELECT query is allowed"):
            validate_readonly_sql("SELECT 1; DROP TABLE users")

    def test_rejects_comment_based_injection(self) -> None:
        with pytest.raises(HTTPException, match="Only SELECT queries are allowed"):
            validate_readonly_sql("SELECT 1 -- harmless\nDROP TABLE users")

    def test_rejects_block_comment_injection(self) -> None:
        with pytest.raises(HTTPException, match="Only SELECT queries are allowed"):
            validate_readonly_sql("SELECT 1 /* noop */ DROP TABLE users")

    def test_rejects_case_insensitive_forbidden_keyword(self) -> None:
        with pytest.raises(HTTPException, match="Only SELECT queries are allowed"):
            validate_readonly_sql("SeLeCt 1 DrOp TABLE users")

    def test_rejects_non_select_leading_keyword(self) -> None:
        with pytest.raises(HTTPException, match="Only SELECT queries are allowed"):
            validate_readonly_sql("SHOW TABLES")


class TestApplyLimit:
    def test_appends_default_limit(self) -> None:
        assert apply_limit("SELECT * FROM metrics") == "SELECT * FROM metrics LIMIT 1000"

    def test_does_not_add_limit_when_present(self) -> None:
        sql = "SELECT * FROM metrics LIMIT 5"
        assert apply_limit(sql) == sql

    def test_respects_custom_limit(self) -> None:
        assert apply_limit("SELECT * FROM metrics", 25) == "SELECT * FROM metrics LIMIT 25"

    def test_rejects_zero_limit(self) -> None:
        with pytest.raises(HTTPException, match="Limit must be greater than zero"):
            apply_limit("SELECT * FROM metrics", 0)

    def test_rejects_negative_limit(self) -> None:
        with pytest.raises(HTTPException, match="Limit must be greater than zero"):
            apply_limit("SELECT * FROM metrics", -1)

    def test_detects_existing_limit_case_insensitively(self) -> None:
        sql = "SELECT * FROM metrics liMiT 20"
        assert apply_limit(sql) == sql

    def test_ignores_limit_word_inside_comments(self) -> None:
        sql = "SELECT * FROM metrics -- limit 1\nWHERE id = 1"
        assert apply_limit(sql) == f"{sql} LIMIT 1000"

    def test_ignores_limit_word_inside_string_literals(self) -> None:
        sql = "SELECT 'limit' AS keyword"
        assert apply_limit(sql) == f"{sql} LIMIT 1000"


class TestSanitizeSql:
    def test_removes_line_comments(self) -> None:
        sanitized = _sanitize_sql("SELECT 1 -- comment\nFROM dual")
        assert "comment" not in sanitized
        assert "FROM dual" in sanitized

    def test_removes_block_comments(self) -> None:
        sanitized = _sanitize_sql("SELECT 1 /* hidden */ FROM dual")
        assert "hidden" not in sanitized
        assert "FROM dual" in sanitized

    def test_replaces_single_quoted_strings(self) -> None:
        assert _sanitize_sql("SELECT 'drop table users'") == "SELECT ''"

    def test_replaces_double_quoted_identifiers(self) -> None:
        assert _sanitize_sql('SELECT "DROP" FROM "users"') == 'SELECT "" FROM ""'
