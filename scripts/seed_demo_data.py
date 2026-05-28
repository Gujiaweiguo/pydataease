#!/usr/bin/env python3
"""
Seed official demo data for PyDataEase.

Creates:
  - MySQL `demo` database with demo_tea_material (30 rows) and demo_tea_order (60 rows)
  - PostgreSQL metadata: datasource, dataset groups/tables/fields, dashboard, 15 chart views

Usage:
  python scripts/seed_demo_data.py

Requires: docker containers `postgres16` and `mysql8` running.
"""

import base64
import json
import os
import subprocess
import sys
import time

# ── IDs (matching Java V2.6 migration) ──────────────────────────────
DS_ID = 985188400292302848            # datasource
DS_TABLE_MAT = 7193457660727922688   # dataset_table demo_tea_material
DS_TABLE_ORDER = 7193537020143079424 # dataset_table demo_tea_order
DG_FOLDER = 985189269226262528       # dataset_group 【官方示例】 folder
DG_MAT = 985189703189925888          # dataset_group 茶饮原料费用
DG_ORDER = 985189053949415424        # dataset_group 茶饮订单明细
VIS_FOLDER = 985247460244983808      # data_visualization_info folder
VIS_DASH = 985192741891870720        # data_visualization_info dashboard
# Chart view IDs
CHART_IDS = [
    985192540087128064, 985192540103905280, 985192540116488192,
    985192540124876800, 985192540141654016, 985192540154236928,
    985192540166819840, 985192540175208448, 985192540183597056,
    985192540191985664, 985192540208762880, 985192540217151488,
    985192540225540096, 985192540242317312, 985192540246511616,
    985192540267483136, 985192540288454656, 985192540313620480,
]

# ── Connection / mode config ───────────────────────────────────────
PG_HOST = os.getenv("SEED_PG_HOST")
PG_PORT = os.getenv("SEED_PG_PORT", "5432")
PG_USER = os.getenv("SEED_PG_USER", "dataease")
PG_PASS = os.getenv("SEED_PG_PASS", "dataease")
PG_DB = os.getenv("SEED_PG_DB", "dataease")

MYSQL_HOST = os.getenv("SEED_MYSQL_HOST", "127.0.0.1")
MYSQL_PORT = os.getenv("SEED_MYSQL_PORT", "3306")
MYSQL_USER = os.getenv("SEED_MYSQL_USER", "root")
MYSQL_PASS = os.getenv("SEED_MYSQL_PASS", "Admin168")

USE_DIRECT_TCP = bool(PG_HOST)

# ── Helpers ─────────────────────────────────────────────────────────

def docker_exec(container: str, cmd: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["docker", "exec", container, *cmd],
        capture_output=True, text=True, timeout=60
    )

def psql(sql: str) -> subprocess.CompletedProcess[str]:
    if USE_DIRECT_TCP:
        return subprocess.run(
            ["psql", f"-h{PG_HOST}", f"-p{PG_PORT}", f"-U{PG_USER}", "-d", PG_DB, "-c", sql],
            capture_output=True,
            text=True,
            timeout=60,
            env={**os.environ, "PGPASSWORD": PG_PASS},
        )
    return docker_exec("postgres16", [
        "psql", "-U", "dataease", "-d", "dataease", "-c", sql
    ])

def psql_file(sql: str) -> subprocess.CompletedProcess[str]:
    if USE_DIRECT_TCP:
        return subprocess.run(
            ["psql", f"-h{PG_HOST}", f"-p{PG_PORT}", f"-U{PG_USER}", "-d", PG_DB, "-v", "ON_ERROR_STOP=1"],
            input=sql,
            capture_output=True,
            text=True,
            timeout=120,
            env={**os.environ, "PGPASSWORD": PG_PASS},
        )
    return subprocess.run(
        ["docker", "exec", "-i", "postgres16",
         "psql", "-U", "dataease", "-d", "dataease", "-v", "ON_ERROR_STOP=1"],
        input=sql, capture_output=True, text=True, timeout=120
    )

def mysql_exec(sql: str) -> subprocess.CompletedProcess[str]:
    if USE_DIRECT_TCP:
        return subprocess.run(
            ["mysql", f"-h{MYSQL_HOST}", f"-P{MYSQL_PORT}", f"-u{MYSQL_USER}", f"-p{MYSQL_PASS}",
             "--default-character-set=utf8mb4", "-e", sql],
            capture_output=True,
            text=True,
            timeout=60,
        )
    return docker_exec("mysql8", [
        "mysql", f"-h{MYSQL_HOST}", f"-P{MYSQL_PORT}",
        f"-u{MYSQL_USER}", f"-p{MYSQL_PASS}",
        "--default-character-set=utf8mb4", "-e", sql
    ])

def mysql_file(sql: str) -> subprocess.CompletedProcess[str]:
    if USE_DIRECT_TCP:
        return subprocess.run(
            ["mysql", f"-h{MYSQL_HOST}", f"-P{MYSQL_PORT}", f"-u{MYSQL_USER}", f"-p{MYSQL_PASS}",
             "--default-character-set=utf8mb4"],
            input=sql,
            capture_output=True,
            text=True,
            timeout=60,
        )
    return subprocess.run(
        ["docker", "exec", "-i", "mysql8",
         "mysql", f"-u{MYSQL_USER}", f"-p{MYSQL_PASS}",
         "--default-character-set=utf8mb4"],
        input=sql, capture_output=True, text=True, timeout=60
    )

def check_ok(result: subprocess.CompletedProcess[str], label: str):
    if result.returncode != 0:
        print(f"FAIL [{label}]: {result.stderr[:500]}", file=sys.stderr)
        sys.exit(1)
    if result.stderr and "ERROR" in result.stderr:
        # Filter out collation warnings
        errors = [line for line in result.stderr.splitlines()
                  if "ERROR" in line and "collation" not in line.lower()]
        if errors:
            print(f"FAIL [{label}]: {'; '.join(errors)}", file=sys.stderr)
            sys.exit(1)

# ── Step 1: MySQL demo data ────────────────────────────────────────

MYSQL_SQL = """\
DROP DATABASE IF EXISTS demo;
CREATE DATABASE demo;
USE demo;

DROP TABLE IF EXISTS demo_tea_material;
CREATE TABLE demo_tea_material (
  `日期` datetime DEFAULT NULL,
  `店铺` longtext,
  `用途` longtext,
  `金额` bigint DEFAULT NULL
);

INSERT INTO demo_tea_material (`日期`, `店铺`, `用途`, `金额`) VALUES
('2024-03-10 17:00:18', '欢果店', '原料购进', 162),
('2024-03-25 01:07:42', '蓝墨店', '原料购进', 141),
('2024-03-28 05:35:18', '果元店', '原料购进', 802),
('2024-03-03 15:26:33', '蓝墨店', '原料购进', 646),
('2024-03-26 18:36:21', '南都店', '原料购进', 680),
('2024-03-04 19:55:07', '香橙店', '原料购进', 190),
('2024-03-21 09:57:12', '乐园店', '原料购进', 183),
('2024-03-18 01:25:25', '欢果店', '原料购进', 568),
('2024-03-10 23:20:21', '红叶店', '原料购进', 145),
('2024-03-01 07:55:58', '蓝墨店', '原料购进', 571),
('2024-03-16 16:51:17', '乐园店', '原料购进', 563),
('2024-03-21 09:33:37', '果元店', '原料购进', 337),
('2024-03-23 13:17:04', '果元店', '原料购进', 743),
('2024-03-10 22:30:29', '水围店', '原料购进', 208),
('2024-03-25 08:59:12', '水围店', '原料购进', 357),
('2024-03-19 06:08:16', '果元店', '原料购进', 579),
('2024-03-05 23:41:43', '香橙店', '原料购进', 278),
('2024-03-20 07:53:58', '南都店', '原料购进', 604),
('2024-03-21 11:39:25', '果元店', '原料购进', 155),
('2024-03-25 00:44:09', '果元店', '原料购进', 211),
('2024-03-13 10:30:44', '水围店', '原料购进', 576),
('2024-03-09 20:07:20', '蓝墨店', '原料购进', 243),
('2024-03-04 02:07:47', '香橙店', '原料购进', 277),
('2024-03-13 00:45:00', '南都店', '原料购进', 101),
('2024-03-07 16:39:38', '果元店', '原料购进', 546),
('2024-03-30 00:16:49', '欢果店', '原料购进', 581),
('2024-03-21 09:28:40', '南都店', '原料购进', 123),
('2024-03-11 11:05:26', '欢果店', '原料购进', 628),
('2024-03-09 02:22:10', '乐园店', '原料购进', 194),
('2024-03-10 01:43:49', '水围店', '原料购进', 122);

DROP TABLE IF EXISTS demo_tea_order;
CREATE TABLE demo_tea_order (
  `店铺` longtext,
  `品线` longtext,
  `菜品名称` longtext,
  `冷/热` longtext,
  `规格` longtext,
  `销售数量` bigint DEFAULT NULL,
  `单价` bigint DEFAULT NULL,
  `账单流水号` longtext,
  `销售日期` datetime DEFAULT NULL
);

INSERT INTO demo_tea_order (`店铺`, `品线`, `菜品名称`, `冷/热`, `规格`, `销售数量`, `单价`, `账单流水号`, `销售日期`) VALUES
('香橙店', '浓郁椰奶', '超大酷柠', '冷', '50塑', 165, 16, '131696143796', '2024-03-13 01:39:25'),
('果元店', '果粒果汁', '爆粒鲜橙', '热', '40塑', 228, 10, '600033642270', '2024-03-20 16:43:33'),
('蓝墨店', '浓郁椰奶', '爆粒鲜橙', '冷', '1000ml', 154, 16, '884244813757', '2024-03-17 20:13:47'),
('水围店', '暖饮果汁', '酷乐鲜柠', '热', '纸大', 149, 10, '264979363423', '2024-03-06 00:50:16'),
('南都店', '暖饮果汁', '布丁珍珠奶茶', '冷', '50塑', 101, 10, '385870702878', '2024-03-14 17:18:29'),
('乐园店', '软糯芋泥', '爆粒鲜橙', '冷', '纸大', 234, 6, '791454535962', '2024-03-13 14:06:58'),
('香橙店', '浓郁椰奶', '超大酷柠', '冷', '50塑', 121, 10, '413995522699', '2024-03-02 04:33:00'),
('水围店', '浓郁椰奶', '生榨纯椰', '冷', '40塑', 243, 6, '414209828587', '2024-03-14 20:08:33'),
('蓝墨店', '果粒果汁', '布丁珍珠奶茶', '热', '50塑', 299, 10, '958393980949', '2024-03-12 19:10:48'),
('香橙店', '浓郁椰奶', '超大酷柠', '冷', '纸大', 192, 23, '520552711676', '2024-03-11 09:08:44'),
('果元店', '超大果茶', '爆粒鲜橙', '热', '塑大', 247, 6, '498009486160', '2024-03-19 14:19:11'),
('乐园店', '滋味果昔', '爆粒鲜橙', '热', '磨砂', 211, 6, '767676599378', '2024-03-07 19:16:15'),
('南都店', '暖饮果汁', '生榨纯椰', '冷', '塑大', 232, 16, '760679036005', '2024-03-18 14:09:09'),
('蓝墨店', '滋味果昔', '珍珠奶茶', '冷', '纸大', 246, 6, '343759610725', '2024-03-23 08:59:58'),
('果元店', '超大果茶', '杨枝甘露', '冷', '50塑', 192, 13, '667202430558', '2024-03-30 00:50:34'),
('红叶店', '暖饮果汁', '芋泥芋圆', '热', '塑大', 130, 29, '973738448731', '2024-03-19 15:22:34'),
('南都店', '浓郁椰奶', '超大酷柠', '热', '50塑', 220, 29, '611315260914', '2024-03-15 17:03:38'),
('果元店', '爆料果汁', '珍珠奶茶', '冷', '塑大', 106, 9, '032924534896', '2024-03-10 19:59:28'),
('果元店', '暖饮果汁', '生榨纯椰', '冷', '塑大', 129, 23, '138461315351', '2024-03-26 17:59:54'),
('果元店', '醇香奶茶', '超大桃桃', '冷', '纸大', 271, 10, '840668169759', '2024-03-26 04:11:48'),
('乐园店', '暖饮果汁', '杨枝甘露', '冷', '纸', 257, 10, '328888056905', '2024-03-28 05:42:51'),
('南都店', '浓郁椰奶', '超大酷柠', '热', '1000ml', 131, 23, '549500625936', '2024-03-26 05:17:30'),
('蓝墨店', '暖饮果汁', '珍珠奶茶', '冷', '塑大', 155, 6, '413132617712', '2024-03-28 09:04:21'),
('香橙店', '爆料果汁', '爆粒鲜橙', '冷', '磨砂', 135, 6, '439234733151', '2024-03-10 15:17:50'),
('南都店', '软糯芋泥', '超大酷柠', '冷', '纸', 203, 13, '562586243741', '2024-03-08 23:07:55'),
('红叶店', '暖饮果汁', '爆粒鲜橙', '热', '50塑', 281, 9, '172802630686', '2024-03-15 11:54:14'),
('果元店', '超大果茶', '芒果西番莲', '冷', '50塑', 258, 13, '309515944911', '2024-03-07 08:11:46'),
('南都店', '超大果茶', '超大酷柠', '冷', '磨砂', 246, 9, '376472713531', '2024-03-28 02:24:12'),
('红叶店', '爆料果汁', '爆粒鲜橙', '冷', '1000ml', 267, 29, '142753377390', '2024-03-17 04:05:34'),
('乐园店', '滋味果昔', '超大酷柠', '冷', '塑大', 144, 6, '845083976435', '2024-03-29 20:55:30'),
('红叶店', '暖饮果汁', '酷乐鲜柠', '冷', '50塑', 226, 16, '886773485680', '2024-03-01 07:27:56'),
('南都店', '爆料果汁', '爆粒鲜橙', '冷', '40塑', 144, 6, '349492386865', '2024-03-11 06:56:47'),
('香橙店', '浓郁椰奶', '杨枝甘露', '热', '40塑', 284, 10, '408801195648', '2024-03-29 15:20:29'),
('果元店', '超大果茶', '杨枝甘露', '冷', '40塑', 137, 29, '819668467639', '2024-03-05 18:39:59'),
('水围店', '浓郁椰奶', '芋泥芋圆', '热', '40塑', 283, 16, '682199136858', '2024-03-09 02:59:53'),
('欢果店', '爆料果汁', '爆粒鲜橙', '热', '50塑', 232, 23, '227621563468', '2024-03-02 16:12:58'),
('蓝墨店', '醇香奶茶', '杨枝甘露', '冷', '纸', 202, 29, '092256992336', '2024-03-22 10:59:10'),
('红叶店', '果粒果汁', '原味奶茶', '冷', '50塑', 280, 10, '432615585424', '2024-03-21 06:48:10'),
('水围店', '超大果茶', '超大桃桃', '冷', '纸', 290, 29, '033917157071', '2024-03-31 22:01:04'),
('红叶店', '暖饮果汁', '爆粒鲜橙', '冷', '塑大', 145, 9, '026608724006', '2024-03-15 04:55:43'),
('南都店', '醇香奶茶', '杨枝甘露', '热', '40塑', 273, 10, '849584185483', '2024-03-25 05:18:32'),
('欢果店', '爆料果汁', '芒果西番莲', '冷', '纸大', 261, 16, '877168481742', '2024-03-08 16:12:33'),
('欢果店', '浓郁椰奶', '爆粒鲜橙', '冷', '塑大', 269, 10, '522723708126', '2024-03-01 07:02:45'),
('果元店', '软糯芋泥', '生榨纯椰', '冷', '1000ml', 132, 16, '234741396784', '2024-03-01 05:20:32'),
('香橙店', '醇香奶茶', '超大酷柠', '冷', '1000ml', 121, 10, '169346306025', '2024-03-07 07:48:10'),
('乐园店', '醇香奶茶', '生榨纯椰', '冷', '纸大', 174, 6, '033478969174', '2024-03-24 07:56:50'),
('果元店', '爆料果汁', '杨枝甘露', '冷', '塑大', 190, 13, '308866895780', '2024-03-11 07:45:56'),
('红叶店', '暖饮果汁', '杨枝甘露', '冷', '40塑', 203, 16, '977260171260', '2024-03-15 07:51:31'),
('香橙店', '爆料果汁', '爆粒鲜橙', '冷', '纸', 194, 6, '026538512943', '2024-03-21 16:27:13'),
('香橙店', '超大果茶', '原味奶茶', '冷', '40塑', 160, 13, '722177202483', '2024-03-24 02:12:10'),
('南都店', '软糯芋泥', '超大酷柠', '冷', '磨砂', 161, 16, '978077236096', '2024-03-06 04:28:39'),
('香橙店', '软糯芋泥', '杨枝甘露', '冷', '40塑', 119, 16, '571583846849', '2024-03-31 13:56:23'),
('红叶店', '暖饮果汁', '芋泥芋圆', '热', '20纸大', 146, 16, '153942260550', '2024-03-06 19:26:24'),
('水围店', '超大果茶', '杨枝甘露', '热', '塑大', 167, 23, '533436086428', '2024-03-08 22:13:39'),
('蓝墨店', '浓郁椰奶', '爆粒鲜橙', '冷', '50塑', 165, 29, '899072569391', '2024-03-07 19:29:55'),
('红叶店', '果粒果汁', '杨枝甘露', '冷', '磨砂', 124, 13, '064192214887', '2024-03-17 05:43:45'),
('南都店', '爆料果汁', '超大酷柠', '冷', '纸大', 117, 9, '952241530599', '2024-03-31 00:11:47'),
('果元店', '醇香奶茶', '布丁珍珠奶茶', '冷', '磨砂', 236, 16, '361733375659', '2024-03-28 19:11:00'),
('红叶店', '滋味果昔', '爆粒鲜橙', '冷', '纸', 244, 16, '456681384664', '2024-03-06 18:06:27'),
('果元店', '超大果茶', '超大桃桃', '热', '塑大', 271, 23, '239545648049', '2024-03-01 14:42:10');
"""


def seed_mysql():
    print("==> Step 1: Seeding MySQL demo data ...")
    r = mysql_file(MYSQL_SQL)
    check_ok(r, "mysql seed")
    # Verify
    r = mysql_exec("SELECT COUNT(*) FROM demo.demo_tea_material;")
    print(f"    demo_tea_material: {r.stdout.strip().splitlines()[-1].strip()} rows")
    r = mysql_exec("SELECT COUNT(*) FROM demo.demo_tea_order;")
    print(f"    demo_tea_order:    {r.stdout.strip().splitlines()[-1].strip()} rows")


# ── Step 2: PostgreSQL metadata ─────────────────────────────────────

def build_pg_sql() -> str:
    now_ms = int(time.time() * 1000)

    lines = []
    lines.append("-- Demo data seed for PyDataEase")
    lines.append("-- Idempotent: delete existing demo data first")
    lines.append("BEGIN;")

    # ── Cleanup (reverse dependency order) ──
    lines.append("-- Cleanup existing demo data")
    lines.append(f"DELETE FROM core_chart_view WHERE scene_id = {VIS_DASH};")
    lines.append(f"DELETE FROM data_visualization_info WHERE id IN ({VIS_FOLDER}, {VIS_DASH});")
    lines.append(f"DELETE FROM core_dataset_table_field WHERE dataset_group_id IN ({DG_MAT}, {DG_ORDER});")
    lines.append(f"DELETE FROM core_dataset_table WHERE id IN ({DS_TABLE_MAT}, {DS_TABLE_ORDER});")
    lines.append(f"DELETE FROM core_dataset_group WHERE id IN ({DG_FOLDER}, {DG_MAT}, {DG_ORDER});")
    lines.append(f"DELETE FROM core_datasource WHERE id = {DS_ID};")

    # ── Datasource ──
    lines.append("-- Datasource")
    ds_config = json.dumps({
        "dataBase": "demo",
        "connectionType": "jdbc",
        "extraParams": "characterEncoding=UTF-8&connectTimeout=5000&useSSL=false",
        "host": MYSQL_HOST,
        "password": MYSQL_PASS,
        "port": MYSQL_PORT,
        "username": MYSQL_USER
    }, ensure_ascii=False)
    lines.append(
        f"INSERT INTO core_datasource (id, name, description, type, pid, edit_type, "
        f"configuration, create_time, update_time, update_by, create_by, status, "
        f"task_status, enable_data_fill) VALUES ("
        f"{DS_ID}, 'demo', NULL, 'mysql', 0, NULL, "
        f"'{ds_config}'::jsonb, {now_ms}, {now_ms}, NULL, '1', 'Success', NULL, false);"
    )

    # ── Dataset Groups ──
    # Folder 【官方示例】
    lines.append("-- Dataset group folder")
    lines.append(
        f"INSERT INTO core_dataset_group (id, name, pid, level, node_type, type, mode, "
        f"info, create_by, create_time, qrtz_instance, sync_status, update_by, "
        f"last_update_time, union_sql, is_cross) VALUES ("
        f"{DG_FOLDER}, '【官方示例】', 0, 0, 'folder', NULL, 0, NULL, "
        f"'1', {now_ms}, NULL, NULL, '1', {now_ms}, NULL, false);"
    )

    # Dataset group: 茶饮原料费用
    mat_info = json.dumps([{
        "currentDs": {
            "id": str(DS_TABLE_MAT),
            "tableName": "demo_tea_material",
            "datasourceId": str(DS_ID),
            "type": "db",
            "info": json.dumps({"table": "demo_tea_material", "sql": ""})
        },
        "currentDsFields": [
            {"id": "1715053944934", "originName": "店铺", "name": "店铺",
             "dataeaseName": "f_4a4cd188441bb10a", "groupType": "d",
             "type": "LONGTEXT", "deType": 0, "extField": 0, "checked": True},
            {"id": "1715053944935", "originName": "日期", "name": "日期",
             "dataeaseName": "f_7fedb6b454fd0ddb", "groupType": "d",
             "type": "DATETIME", "deType": 1, "extField": 0, "checked": True},
            {"id": "1715053944936", "originName": "用途", "name": "用途",
             "dataeaseName": "f_703aac67af8ea53d", "groupType": "d",
             "type": "LONGTEXT", "deType": 0, "extField": 0, "checked": True},
            {"id": "1715053944937", "originName": "金额", "name": "金额",
             "dataeaseName": "f_8cc276e515d2de6d", "groupType": "q",
             "type": "BIGINT", "deType": 2, "extField": 0, "checked": True},
        ]
    }], ensure_ascii=False)

    lines.append(
        f"INSERT INTO core_dataset_group (id, name, pid, level, node_type, type, mode, "
        f"info, create_by, create_time, qrtz_instance, sync_status, update_by, "
        f"last_update_time, union_sql, is_cross) VALUES ("
        f"{DG_MAT}, '茶饮原料费用', {DG_FOLDER}, 0, 'dataset', NULL, 0, "
        f"'{mat_info}'::jsonb, '1', {now_ms}, NULL, NULL, '1', {now_ms}, NULL, false);"
    )

    # Dataset group: 茶饮订单明细
    order_info = json.dumps([{
        "currentDs": {
            "id": str(DS_TABLE_ORDER),
            "tableName": "demo_tea_order",
            "datasourceId": str(DS_ID),
            "type": "db",
            "info": json.dumps({"table": "demo_tea_order", "sql": ""})
        },
        "currentDsFields": [
            {"id": "1715072798360", "originName": "冷/热", "name": "冷/热",
             "dataeaseName": "f_68bd7361c951941a", "groupType": "d",
             "type": "LONGTEXT", "deType": 0, "extField": 0, "checked": True},
            {"id": "1715072798361", "originName": "单价", "name": "单价",
             "dataeaseName": "f_878cf3320c82724f", "groupType": "q",
             "type": "BIGINT", "deType": 2, "extField": 0, "checked": True},
            {"id": "1715072798362", "originName": "品线", "name": "品线",
             "dataeaseName": "f_f8fc4f728f1e6fa2", "groupType": "d",
             "type": "LONGTEXT", "deType": 0, "extField": 0, "checked": True},
            {"id": "1715072798363", "originName": "店铺", "name": "店铺",
             "dataeaseName": "f_4a4cd188441bb10a", "groupType": "d",
             "type": "LONGTEXT", "deType": 0, "extField": 0, "checked": True},
            {"id": "1715072798364", "originName": "菜品名称", "name": "菜品名称",
             "dataeaseName": "f_7c7894e776e3b8ec", "groupType": "d",
             "type": "LONGTEXT", "deType": 0, "extField": 0, "checked": True},
            {"id": "1715072798365", "originName": "规格", "name": "规格",
             "dataeaseName": "f_5c1a43f6150f3a56", "groupType": "d",
             "type": "LONGTEXT", "deType": 0, "extField": 0, "checked": True},
            {"id": "1715072798366", "originName": "账单流水号", "name": "账单流水号",
             "dataeaseName": "f_252845fa1a250405", "groupType": "d",
             "type": "LONGTEXT", "deType": 0, "extField": 0, "checked": True},
            {"id": "1715072798367", "originName": "销售数量", "name": "销售数量",
             "dataeaseName": "f_59fcc2c2b0f47cde", "groupType": "q",
             "type": "BIGINT", "deType": 2, "extField": 0, "checked": True},
            {"id": "1715072798368", "originName": "销售日期", "name": "销售日期",
             "dataeaseName": "f_852cde987322fd1d", "groupType": "d",
             "type": "DATETIME", "deType": 1, "extField": 0, "checked": True},
        ]
    }], ensure_ascii=False)

    lines.append(
        f"INSERT INTO core_dataset_group (id, name, pid, level, node_type, type, mode, "
        f"info, create_by, create_time, qrtz_instance, sync_status, update_by, "
        f"last_update_time, union_sql, is_cross) VALUES ("
        f"{DG_ORDER}, '茶饮订单明细', {DG_FOLDER}, 0, 'dataset', NULL, 0, "
        f"'{order_info}'::jsonb, '1', {now_ms}, NULL, NULL, '1', {now_ms}, NULL, false);"
    )

    # ── Dataset Tables ──
    lines.append("-- Dataset tables")
    lines.append(
        f"INSERT INTO core_dataset_table (id, name, table_name, datasource_id, "
        f"dataset_group_id, type, info, sql_variable_details) VALUES ("
        f"{DS_TABLE_MAT}, NULL, 'demo_tea_material', {DS_ID}, {DG_MAT}, 'db', "
        f"'{{\"table\":\"demo_tea_material\",\"sql\":\"\"}}', NULL);"
    )
    lines.append(
        f"INSERT INTO core_dataset_table (id, name, table_name, datasource_id, "
        f"dataset_group_id, type, info, sql_variable_details) VALUES ("
        f"{DS_TABLE_ORDER}, NULL, 'demo_tea_order', {DS_ID}, {DG_ORDER}, 'db', "
        f"'{{\"table\":\"demo_tea_order\",\"sql\":\"\"}}', NULL);"
    )

    # ── Dataset Table Fields ──
    lines.append("-- Dataset table fields")
    fields = [
        # demo_tea_material fields
        (1715053944934, DS_ID, DS_TABLE_MAT, DG_MAT, "NULL", "店铺", "店铺", "NULL",
         "f_4a4cd188441bb10a", "f_4a4cd188441bb10a", "d", "LONGTEXT", "NULL", 0, 0, 0, True),
        (1715053944935, DS_ID, DS_TABLE_MAT, DG_MAT, "NULL", "日期", "日期", "NULL",
         "f_7fedb6b454fd0ddb", "f_7fedb6b454fd0ddb", "d", "DATETIME", "NULL", 1, 1, 0, True),
        (1715053944936, DS_ID, DS_TABLE_MAT, DG_MAT, "NULL", "用途", "用途", "NULL",
         "f_703aac67af8ea53d", "f_703aac67af8ea53d", "d", "LONGTEXT", "NULL", 0, 0, 0, True),
        (1715053944937, DS_ID, DS_TABLE_MAT, DG_MAT, "NULL", "金额", "金额", "NULL",
         "f_8cc276e515d2de6d", "f_8cc276e515d2de6d", "q", "BIGINT", "NULL", 2, 2, 0, True),
        # demo_tea_order fields
        (1715072798360, DS_ID, DS_TABLE_ORDER, DG_ORDER, "NULL", "冷/热", "冷/热", "NULL",
         "f_68bd7361c951941a", "f_68bd7361c951941a", "d", "LONGTEXT", "NULL", 0, 0, 0, True),
        (1715072798361, DS_ID, DS_TABLE_ORDER, DG_ORDER, "NULL", "单价", "单价", "NULL",
         "f_878cf3320c82724f", "f_878cf3320c82724f", "q", "BIGINT", "NULL", 2, 2, 0, True),
        (1715072798362, DS_ID, DS_TABLE_ORDER, DG_ORDER, "NULL", "品线", "品线", "NULL",
         "f_f8fc4f728f1e6fa2", "f_f8fc4f728f1e6fa2", "d", "LONGTEXT", "NULL", 0, 0, 0, True),
        (1715072798363, DS_ID, DS_TABLE_ORDER, DG_ORDER, "NULL", "店铺", "店铺", "NULL",
         "f_4a4cd188441bb10a", "f_4a4cd188441bb10a", "d", "LONGTEXT", "NULL", 0, 0, 0, True),
        (1715072798364, DS_ID, DS_TABLE_ORDER, DG_ORDER, "NULL", "菜品名称", "菜品名称", "NULL",
         "f_7c7894e776e3b8ec", "f_7c7894e776e3b8ec", "d", "LONGTEXT", "NULL", 0, 0, 0, True),
        (1715072798365, DS_ID, DS_TABLE_ORDER, DG_ORDER, "NULL", "规格", "规格", "NULL",
         "f_5c1a43f6150f3a56", "f_5c1a43f6150f3a56", "d", "LONGTEXT", "NULL", 0, 0, 0, True),
        (1715072798366, DS_ID, DS_TABLE_ORDER, DG_ORDER, "NULL", "账单流水号", "账单流水号", "NULL",
         "f_252845fa1a250405", "f_252845fa1a250405", "d", "LONGTEXT", "NULL", 0, 0, 0, True),
        (1715072798367, DS_ID, DS_TABLE_ORDER, DG_ORDER, "NULL", "销售数量", "销售数量", "NULL",
         "f_59fcc2c2b0f47cde", "f_59fcc2c2b0f47cde", "q", "BIGINT", "NULL", 2, 2, 0, True),
        (1715072798368, DS_ID, DS_TABLE_ORDER, DG_ORDER, "NULL", "销售日期", "销售日期", "NULL",
         "f_852cde987322fd1d", "f_852cde987322fd1d", "d", "DATETIME", "NULL", 1, 1, 0, True),
        # Computed fields for 订单
        (7193537137675866112, "NULL", "NULL", DG_ORDER, "NULL",
         "[1715072798361]*[1715072798367]", "销售金额", "NULL",
         "f_ebd405e534ce8c6c", "f_ebd405e534ce8c6c", "q", "VARCHAR", "NULL", 3, 3, 2, True),
        (7193537244429291520, "NULL", "NULL", DG_ORDER, "NULL",
         "round(sum([7193537137675866112])/count([1715072798366])/100,2)", "客单价", "NULL",
         "f_39fd4542efb6a572", "f_39fd4542efb6a572", "q", "VARCHAR", "NULL", 3, 3, 2, True),
        (7193537490169368576, "NULL", "NULL", DG_ORDER, "NULL",
         "round(sum([7193537137675866112])/sum([1715072798367]),2)", "杯均价", "NULL",
         "f_47f238401ac173f1", "f_47f238401ac173f1", "q", "VARCHAR", "NULL", 3, 3, 2, True),
    ]

    for f in fields:
        (fid, ds_id, dt_id, dg_id, chart_id, origin, name, desc,
         da_name, fs_name, gtype, ftype, size, de_type, de_ext,
         ext_field, checked) = f
        # Frontend expects base64-encoded originName for computed fields (extField=2)
        # See CalculateFields.ts: originNameHandleBack() decodes with Base64.decode()
        if ext_field == 2:
            origin = base64.b64encode(origin.encode("utf-8")).decode("utf-8")
        checked_str = "true" if checked else "false"
        lines.append(
            f"INSERT INTO core_dataset_table_field "
            f"(id, datasource_id, dataset_table_id, dataset_group_id, chart_id, "
            f"origin_name, name, description, dataease_name, field_short_name, "
            f"group_type, type, size, de_type, de_extract_type, ext_field, checked, "
            f"column_index, last_sync_time, accuracy, date_format, date_format_type) VALUES ("
            f"{fid}, {ds_id}, {dt_id}, {dg_id}, {chart_id}, "
            f"'{origin}', '{name}', {desc}, '{da_name}', '{fs_name}', "
            f"'{gtype}', '{ftype}', {size}, {de_type}, {de_ext}, {ext_field}, {checked_str}, "
            f"NULL, NULL, 0, NULL, NULL);"
        )

    # ── Visualization Info ──
    lines.append("-- Visualization: folder")
    lines.append(
        f"INSERT INTO data_visualization_info (id, name, pid, org_id, level, node_type, "
        f"type, canvas_style_data, component_data, mobile_layout, status, "
        f"self_watermark_status, sort, create_time, create_by, update_time, update_by, "
        f"remark, source, delete_flag, delete_time, delete_by, version) VALUES ("
        f"{VIS_FOLDER}, '【官方示例】', NULL, 1720255172903497728, NULL, 'folder', "
        f"'dashboard', NULL, NULL, false, 1, 0, 0, {now_ms}, '1', {now_ms}, '1', "
        f"NULL, NULL, false, NULL, NULL, 3);"
    )

    # Dashboard with minimal component_data — charts will be linked via core_chart_view.scene_id
    # The component_data JSON defines the layout/position of each chart on the dashboard.
    # We'll build a simple grid layout.
    lines.append("-- Visualization: dashboard")
    dashboard_style = json.dumps({
        "width": 1920, "height": 1080,
        "refreshViewEnable": False, "refreshViewLoading": False,
        "refreshUnit": "minute", "refreshTime": 5,
        "scale": 60, "scaleWidth": 100, "scaleHeight": 100,
        "backgroundColorSelect": False, "backgroundImageEnable": True,
        "backgroundType": "backgroundColor",
        "openCommonStyle": True, "opacity": 1, "fontSize": 14,
        "themeId": "10001", "color": "#000000",
        "backgroundColor": "rgba(245, 246, 247, 1)",
    }, ensure_ascii=False)

    # Build component_data with chart positions
    components = _build_dashboard_components()
    component_data = json.dumps(components, ensure_ascii=False)

    lines.append(
        f"INSERT INTO data_visualization_info (id, name, pid, org_id, level, node_type, "
        f"type, canvas_style_data, component_data, mobile_layout, status, "
        f"self_watermark_status, sort, create_time, create_by, update_time, update_by, "
        f"remark, source, delete_flag, delete_time, delete_by, version) VALUES ("
        f"{VIS_DASH}, '连锁茶饮销售看板', {VIS_FOLDER}, 1720255172903497728, NULL, 'leaf', "
        f"'dashboard', "
        f"'{dashboard_style}'::jsonb, "
        f"'{component_data}'::jsonb, "
        f"false, 1, 0, 0, {now_ms}, '1', {now_ms}, '1', "
        f"NULL, NULL, false, NULL, NULL, 3);"
    )

    # ── Chart Views ──
    lines.append("-- Chart views (minimal — will be populated by frontend)")
    # We insert chart view stubs — the frontend will fill in detailed chart config
    # when the user edits them. The key fields are: id, title, scene_id, table_id, type
    chart_stubs = [
        (985192540087128064, "总销量", DG_ORDER, "rich-text"),
        (985192540154236928, "总销量", DG_ORDER, "rich-text"),
        (985192540166819840, "总支出", DG_MAT, "rich-text"),
        (985192540175208448, "客单价", DG_ORDER, "rich-text"),
        (985192540183597056, "热销品", DG_ORDER, "rich-text"),
        (985192540191985664, "规格销量", DG_ORDER, "rich-text"),
        (985192540225540096, "品线销量", DG_ORDER, "rich-text"),
        (985192540242317312, "杯均价", DG_ORDER, "rich-text"),
        (985192540208762880, "销售额走势", DG_ORDER, "area"),
        (985192540267483136, "销量走势", DG_ORDER, "area"),
        (985192540124876800, "原料支出趋势", DG_MAT, "area"),
        (985192540141654016, "冷热占比", DG_ORDER, "pie-donut"),
        (985192540103905280, "店铺销售额排名", DG_ORDER, "table-normal"),
        (985192540116488192, "菜品销量排名", DG_ORDER, "bar-horizontal"),
        (985192540217151488, "品线销量排名", DG_ORDER, "bar-horizontal"),
        (985192540246511616, "规格销量排名", DG_ORDER, "bar-horizontal"),
        (985192540288454656, "店铺销量排名", DG_ORDER, "rich-text"),
        (985192540313620480, "总销售额", DG_ORDER, "rich-text"),
    ]

    for cid, title, table_id, ctype in chart_stubs:
        lines.append(
            f"INSERT INTO core_chart_view "
            f"(id, title, scene_id, table_id, type, render, result_count, result_mode, "
            f"x_axis, x_axis_ext, y_axis, y_axis_ext, ext_stack, ext_bubble, "
            f"ext_label, ext_tooltip, custom_attr, custom_style, custom_filter, "
            f"drill_fields, senior, create_by, create_time, update_time, snapshot, "
            f"style_priority, chart_type, is_plugin, data_from, view_fields, "
            f"refresh_view_enable, refresh_unit, refresh_time, linkage_active, jump_active, "
            f"copy_from, copy_id) VALUES ("
            f"{cid}, '{title}', {VIS_DASH}, {table_id}, '{ctype}', "
            f"CASE WHEN '{ctype}' = 'rich-text' THEN 'custom' ELSE 'antv' END, "
            f"1000, 'all', '[]'::jsonb, '[]'::jsonb, '[]'::jsonb, '[]'::jsonb, "
            f"'[]'::jsonb, '[]'::jsonb, '[]'::jsonb, '[]'::jsonb, "
            f"'{{}}'::jsonb, '{{}}'::jsonb, '{{}}'::jsonb, "
            f"'[]'::jsonb, '{{}}'::jsonb, '1', {now_ms}, {now_ms}, NULL, "
            f"'panel', 'private', false, 'dataset', '[]'::jsonb, "
            f"false, 'minute', 5, false, false, NULL, NULL);"
        )

    # ── Update sequences to be above max inserted ID ──
    max_id = max(DS_ID, DS_TABLE_MAT, DS_TABLE_ORDER, DG_FOLDER, DG_MAT, DG_ORDER,
                 VIS_FOLDER, VIS_DASH, 7193537490169368576, max(CHART_IDS))
    lines.append("-- Update sequences")
    for seq, table in [
        ("core_datasource_id_seq", "core_datasource"),
        ("core_dataset_table_id_seq", "core_dataset_table"),
        ("core_dataset_group_id_seq", "core_dataset_group"),
        ("core_dataset_table_field_id_seq", "core_dataset_table_field"),
        ("data_visualization_info_id_seq", "data_visualization_info"),
        ("core_chart_view_id_seq", "core_chart_view"),
    ]:
        lines.append(
            f"SELECT setval('{seq}', GREATEST((SELECT COALESCE(MAX(id), 0) FROM {table}) + 1, {max_id} + 1));"
        )

    lines.append("COMMIT;")
    return "\n".join(lines)


def _build_dashboard_components() -> list[dict[str, object]]:
    # Grid layout: 4 columns x 5 rows
    # Each cell ~460x190 px with 10px gaps
    positions = [
        # Row 1: KPI cards
        (10,  10,  460, 180),   # 总销量
        (480, 10,  460, 180),   # 总销量
        (950, 10,  460, 180),   # 总支出
        (1420, 10, 490, 180),   # 客单价
        # Row 2: KPI cards
        (10,  200, 460, 180),   # 热销品
        (480, 200, 460, 180),   # 规格销量
        (950, 200, 460, 180),   # 品线销量
        (1420, 200, 490, 180),  # 杯均价
        # Row 3: Trends
        (10,  390, 940, 300),   # 销售额走势
        (960, 390, 950, 300),   # 销量走势
        # Row 4: More charts
        (10,  700, 460, 360),   # 原料支出趋势
        (480, 700, 460, 360),   # 冷热占比
        (960, 700, 460, 360),   # 店铺销售额排名
        (1430, 700, 480, 360),  # 菜品销量排名
    ]

    chart_ids_for_layout = [
        985192540087128064, 985192540154236928, 985192540166819840,
        985192540175208448, 985192540183597056, 985192540191985664,
        985192540225540096, 985192540242317312,
        985192540208762880, 985192540267483136,
        985192540124876800, 985192540141654016,
        985192540103905280, 985192540116488192,
    ]

    components = []
    for i, (x, y, w, h) in enumerate(positions):
        if i >= len(chart_ids_for_layout):
            break
        cid = chart_ids_for_layout[i]
        components.append({
            "component": "UserView",
            "id": str(cid),
            "propValue": {"textValue": ""},
            "style": {
                "x": x, "y": y, "width": w, "height": h,
                "borderWidth": 1, "borderRadius": 4,
                "borderColor": "#dcdfe6",
            },
            "chart": str(cid),
            "commonBackground": {
                "innerPadding": 8,
                "borderRadius": 4,
                "backgroundColorSelect": True,
                "backgroundColor": "#ffffff",
                "borderWidth": 1,
                "borderStyle": "solid",
                "borderColor": "#dcdfe6",
            },
        })
    return components


V26_FILE = "/opt/code/pydataease/core/core-backend/target/classes/db/migration/V2.6__ddl.sql"


def _import_v26_chart_views_and_dashboard():
    """Read Java V2.6 migration and import full chart views + dashboard data."""
    import pathlib
    v26_path = pathlib.Path(V26_FILE)
    if not v26_path.exists():
        print(f"    WARNING: {V26_FILE} not found, skipping full chart import")
        return

    content = v26_path.read_text()
    lines = content.split('\n')
    chart_lines = [line for line in lines if line.strip().startswith("INSERT INTO `core_chart_view`")]
    if not chart_lines:
        print("    WARNING: No chart view INSERTs found in V2.6")
        return

    import re
    transformed = []
    for line in chart_lines:
        pg = line.replace('`', '')
        pg = pg.replace('\\"', '"')
        pg = pg.replace('\\\\', '\\')
        pg = re.sub(
            r", (NULL|[01]), '((?:calc|dataset))', '\[\]', ([01]), '(minute)', (\d+), ([01]), ([01]), (NULL|\d+), (NULL|\d+)\);",
            lambda m: (
                f", {'true' if m.group(1)=='1' else ('NULL' if m.group(1)=='NULL' else 'false')}"
                f", '{m.group(2)}', '[]'::jsonb"
                f", {'true' if m.group(3)=='1' else 'false'}"
                f", '{m.group(4)}', {m.group(5)}"
                f", {'true' if m.group(6)=='1' else 'false'}"
                f", {'true' if m.group(7)=='1' else 'false'}"
                f", {m.group(8)}, {m.group(9)});"
            ),
            pg
        )
        transformed.append(pg)

    sql_parts = ["BEGIN;\n"]
    sql_parts.append(f"DELETE FROM core_chart_view WHERE scene_id = {VIS_DASH};\n")
    for line in transformed:
        sql_parts.append(line + '\n')
    sql_parts.append("SELECT setval('core_chart_view_id_seq', (SELECT MAX(id) FROM core_chart_view) + 1);\n")
    sql_parts.append("COMMIT;\n")
    chart_sql = ''.join(sql_parts)

    r = psql_file(chart_sql)
    check_ok(r, "pg chart views import")
    print(f"    Imported {len(transformed)} chart views from V2.6")

    # ── Import dashboard component_data + canvas_style_data ──
    dash_line = None
    for line in lines:
        if 'INSERT INTO `data_visualization_info`' in line and str(VIS_DASH) in line:
            dash_line = line
            break
    if not dash_line:
        print("    WARNING: Dashboard INSERT not found in V2.6")
        return

    dash_line = dash_line.replace('`', '').replace('\\"', '"').replace('\\\\', '\\')
    values_match = re.search(r"VALUES \((.+)\);?$", dash_line)
    if not values_match:
        print("    WARNING: Cannot parse dashboard VALUES")
        return
    values_str = values_match.group(1)

    # Extract canvas_style_data (first JSON object)
    cs_start = values_str.find("'{")
    if cs_start == -1:
        print("    WARNING: canvas_style_data not found")
        return
    pos = cs_start + 1
    brace_count, in_str, escape = 0, False, False
    cs_end = None
    for i in range(pos, len(values_str)):
        c = values_str[i]
        if escape:
            escape = False
            continue
        if c == '\\':
            escape = True
            continue
        if c == '"':
            in_str = not in_str
            continue
        if not in_str:
            if c == '{':
                brace_count += 1
            elif c == '}':
                brace_count -= 1
                if brace_count == 0:
                    cs_end = i
                    break
    if cs_end is None:
        print("    WARNING: canvas_style_data parse failed")
        return
    canvas_style_data = values_str[pos:cs_end + 1]

    # Extract component_data (JSON array after canvas_style_data)
    cd_start = values_str.find("'[{", cs_end)
    if cd_start == -1:
        print("    WARNING: component_data not found")
        return
    pos = cd_start + 1
    bracket_count, in_str, escape = 0, False, False
    cd_end = None
    for i in range(pos, len(values_str)):
        c = values_str[i]
        if escape:
            escape = False
            continue
        if c == '\\':
            escape = True
            continue
        if c == '"':
            in_str = not in_str
            continue
        if not in_str:
            if c == '[':
                bracket_count += 1
            elif c == ']':
                bracket_count -= 1
                if bracket_count == 0:
                    cd_end = i
                    break
    if cd_end is None:
        print("    WARNING: component_data parse failed")
        return
    component_data = values_str[pos:cd_end + 1]

    update_sql = (
        "BEGIN;\n"
        "UPDATE data_visualization_info\n"
        f"SET canvas_style_data = $DEMO_CSD${canvas_style_data}$DEMO_CSD$::jsonb,\n"
        f"    component_data = $DEMO_CD${component_data}$DEMO_CD$::jsonb\n"
        f"WHERE id = {VIS_DASH};\n"
        "COMMIT;\n"
    )
    r = psql_file(update_sql)
    check_ok(r, "pg dashboard update")
    print(f"    Updated dashboard component_data ({len(component_data)} chars)")


def seed_postgresql():
    print("==> Step 2: Seeding PostgreSQL demo metadata ...")
    pg_sql = build_pg_sql()
    r = psql_file(pg_sql)
    check_ok(r, "pg seed")

    print("==> Step 3: Importing full chart views from Java V2.6 ...")
    _import_v26_chart_views_and_dashboard()

    # Count inserted rows
    queries = {
        "core_datasource": f"id = {DS_ID}",
        "core_dataset_group": f"id IN ({DG_FOLDER},{DG_MAT},{DG_ORDER})",
        "core_dataset_table": f"id IN ({DS_TABLE_MAT},{DS_TABLE_ORDER})",
        "core_dataset_table_field": f"dataset_group_id IN ({DG_MAT},{DG_ORDER})",
        "data_visualization_info": f"id IN ({VIS_FOLDER},{VIS_DASH})",
        "core_chart_view": f"scene_id = {VIS_DASH}",
    }
    for table, where in queries.items():
        r = psql(f"SELECT count(*) FROM {table} WHERE {where};")
        out_lines = [ln.strip() for ln in r.stdout.strip().splitlines() if ln.strip() and ln.strip().isdigit()]
        count = out_lines[-1] if out_lines else "?"
        print(f"    {table}: {count} demo rows")

    print("\n==> Done! Demo data seeded successfully.")


if __name__ == "__main__":
    print("=" * 60)
    print("PyDataEase Official Demo Data Seeder")
    print("=" * 60)

    if USE_DIRECT_TCP:
        print(f"Mode: direct TCP (PostgreSQL {PG_HOST}:{PG_PORT}, MySQL {MYSQL_HOST}:{MYSQL_PORT})")
    else:
        print("Mode: docker exec (postgres16/mysql8)")
        # Check containers are running
        for container in ["postgres16", "mysql8"]:
            r = subprocess.run(["docker", "inspect", "-f", "{{.State.Running}}", container],
                              capture_output=True, text=True)
            if r.stdout.strip() != "true":
                print(f"ERROR: Container '{container}' is not running!", file=sys.stderr)
                sys.exit(1)

    seed_mysql()
    seed_postgresql()
