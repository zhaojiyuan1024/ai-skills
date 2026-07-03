---
name: mysql-executor
description: 直接执行 SQL 语句（SELECT/INSERT/UPDATE/DELETE/CREATE/ALTER/DROP），不需要写 Python 代码。当用户说"执行 SQL"、"跑个 SQL"、"查一下表"、"建表"、"改表结构"、"导入 SQL 文件"、"查数据库"、"查询数据库"、"帮我查下"、"run SQL"、"execute query"时触发。当用户通过 @ 引用文件方式提供数据库连接信息并表达查询意图时也必须触发。在任何需要连接 MySQL 数据库验证数据、查看表结构或执行语句的场景下，优先使用本 skill 而非写 Python 脚本。
---

# MySQL Executor

直接执行 SQL，不生成代码。脚本自动检查并安装 pymysql。

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

1. 根据用户给的连接信息和 SQL，拼好命令
2. 直接执行脚本，展示结果
