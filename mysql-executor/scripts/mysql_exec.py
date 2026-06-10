#!/usr/bin/env python3
"""MySQL DDL/DML 执行器 — 给连接信息和 SQL，直接跑"""

import subprocess
import sys
import io

# Windows 终端中文编码修复
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

# ============================================================
# 自动安装依赖
# ============================================================
def ensure_pymysql():
    try:
        import pymysql
        return pymysql
    except ImportError:
        print("pymysql 未安装，正在自动安装...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pymysql", "-q"])
        import pymysql
        return pymysql


pymysql = ensure_pymysql()

import argparse
import os
from getpass import getpass


# ============================================================
# 连接
# ============================================================
def get_connection(args):
    host = args.host or input("MySQL host [localhost]: ").strip() or "localhost"
    port = args.port or int(input("MySQL port [3306]: ").strip() or "3306")
    user = args.user or input("MySQL user [root]: ").strip() or "root"
    password = args.password or getpass("MySQL password: ")
    database = args.database or input("Database name: ").strip()

    return pymysql.connect(
        host=host,
        port=port,
        user=user,
        password=password,
        database=database,
        charset="utf8mb4",
    )


# ============================================================
# 执行 SQL
# ============================================================
def execute_sql(conn, sql):
    """执行单条或多条 SQL，自动区分 DDL/DML"""
    sql = sql.strip()
    if not sql:
        return

    # 多条语句用分号分割
    statements = [s.strip() for s in sql.split(";") if s.strip()]

    for stmt in statements:
        # 判断是否是 SELECT
        is_select = stmt.lstrip().upper().startswith("SELECT") or \
                    stmt.lstrip().upper().startswith("SHOW") or \
                    stmt.lstrip().upper().startswith("DESCRIBE") or \
                    stmt.lstrip().upper().startswith("EXPLAIN")

        try:
            with conn.cursor(pymysql.cursors.DictCursor) as cursor:
                if is_select:
                    cursor.execute(stmt)
                    rows = cursor.fetchall()
                    if rows:
                        # 打印表头
                        headers = list(rows[0].keys())
                        widths = [len(h) for h in headers]
                        for row in rows:
                            for i, h in enumerate(headers):
                                widths[i] = max(widths[i], len(str(row[h])))
                        # 打印
                        header_line = " | ".join(h.ljust(widths[i]) for i, h in enumerate(headers))
                        print(header_line)
                        print("-" * len(header_line))
                        for row in rows:
                            print(" | ".join(str(row[h]).ljust(widths[i]) for i, h in enumerate(headers)))
                        print(f"\n({len(rows)} rows)")
                    else:
                        print("Empty set")
                else:
                    # DDL/DML — 判断是否需要 autocommit
                    is_ddl = stmt.lstrip().upper().startswith(("CREATE", "ALTER", "DROP", "TRUNCATE", "RENAME"))
                    if is_ddl:
                        conn.autocommit(True)
                        cursor.execute(stmt)
                        conn.autocommit(False)
                    else:
                        cursor.execute(stmt)
                        conn.commit()
                    affected = cursor.rowcount
                    print(f"Query OK, {affected} row(s) affected")
        except Exception as e:
            if not is_select:
                try:
                    conn.rollback()
                except:
                    pass
            print(f"ERROR: {e}")
            raise


def execute_file(conn, filepath):
    """执行 SQL 文件"""
    if not os.path.exists(filepath):
        print(f"File not found: {filepath}")
        sys.exit(1)

    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    statements = [s.strip() for s in content.split(";") if s.strip()]
    print(f"Executing {len(statements)} statement(s) from {filepath}\n")

    for i, stmt in enumerate(statements, 1):
        print(f"-- Statement {i} --")
        execute_sql(conn, stmt + ";")
        print()


# ============================================================
# CLI
# ============================================================
def main():
    parser = argparse.ArgumentParser(description="MySQL DDL/DML Executor")
    parser.add_argument("-H", "--host", help="MySQL host")
    parser.add_argument("-P", "--port", type=int, help="MySQL port")
    parser.add_argument("-u", "--user", help="MySQL user")
    parser.add_argument("-p", "--password", help="MySQL password")
    parser.add_argument("-d", "--database", help="Database name")
    parser.add_argument("-e", "--execute", help="SQL statement to execute")
    parser.add_argument("-f", "--file", help="SQL file to execute")
    parser.add_argument("--dsn", help="Connection string: mysql://user:pass@host:port/db")

    args = parser.parse_args()

    # 解析 DSN
    if args.dsn:
        from urllib.parse import urlparse
        parsed = urlparse(args.dsn)
        args.host = args.host or parsed.hostname
        args.port = args.port or parsed.port
        args.user = args.user or parsed.username
        args.password = args.password or parsed.password
        args.database = args.database or parsed.path.lstrip("/")

    # 必须有 SQL 来源
    if not args.execute and not args.file:
        # 交互式输入 SQL
        print("Enter SQL (end with an empty line):")
        lines = []
        while True:
            line = input()
            if line.strip() == "":
                break
            lines.append(line)
        args.execute = "\n".join(lines)

    if not args.execute and not args.file:
        print("No SQL to execute.")
        sys.exit(1)

    conn = get_connection(args)
    try:
        if args.file:
            execute_file(conn, args.file)
        else:
            execute_sql(conn, args.execute)
    finally:
        conn.close()


if __name__ == "__main__":
    main()
