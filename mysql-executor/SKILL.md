---
name: mysql-executor
description: 直接执行 SQL 语句（SELECT/INSERT/UPDATE/DELETE/CREATE/ALTER/DROP）。当用户说"执行 SQL"、"跑个 SQL"、"查一下表"、"建表"、"改表结构"、"导入 SQL 文件"、"查数据库"、"查询数据库"、"帮我查下"、"run SQL"、"execute query"时触发。当用户通过 @ 引用文件方式提供数据库连接信息并表达查询意图时也必须触发。当你准备写 Python 脚本连接数据库执行 SQL 时，优先使用本 skill。仅适用于 MySQL，其他数据库不适用。
---

# MySQL Executor

通过调用脚本直接执行 SQL，不要手写 Python 代码连接 MySQL。脚本自动检查并安装 pymysql。

## 适用范围

- 仅适用于 **MySQL** 数据库，其他数据库（PostgreSQL、SQLite、SQL Server 等）不适用。
- 当你准备写 Python 脚本（pymysql/mysql-connector 等）来执行 SQL 时，优先使用本 skill 而非手写代码。

## 脚本路径

```
~/.claude/skills/mysql-executor/scripts/mysql_exec.py
```

## 调用方式

### 命令行传参

```bash
python ~/.claude/skills/mysql-executor/scripts/mysql_exec.py -H localhost -u root -p mypassword -d mydb -e "SELECT * FROM users"
```

### DSN 连接字符串

```bash
python ~/.claude/skills/mysql-executor/scripts/mysql_exec.py --dsn "mysql://root:password@localhost:3306/mydb" -e "CREATE TABLE ..."
```

### 执行 SQL 文件

```bash
python ~/.claude/skills/mysql-executor/scripts/mysql_exec.py -H localhost -u root -p mypassword -d mydb -f schema.sql
```

### 交互式（不传参）

```bash
python ~/.claude/skills/mysql-executor/scripts/mysql_exec.py
```

## 参数说明

| 参数 | 说明 |
|------|------|
| `-H` / `--host` | MySQL 主机 |
| `-P` / `--port` | 端口 |
| `-u` / `--user` | 用户名 |
| `-p` / `--password` | 密码 |
| `-d` / `--database` | 数据库名 |
| `-e` / `--execute` | SQL 语句 |
| `-f` / `--file` | SQL 文件路径 |
| `--dsn` | 连接字符串 |

## Skill 触发后

1. 从用户消息或 @ 引用的文件中提取数据库连接信息（host、port、database、user、password）
2. 密码含特殊字符（如 `-`、`!`、`@`）时优先使用 `--dsn` 方式，避免 shell 解析错误
3. 拼好命令，直接执行脚本，展示结果
4. 如果是只读查询，不得执行 INSERT/UPDATE/DELETE/DROP/ALTER 等写操作，除非用户明确要求
