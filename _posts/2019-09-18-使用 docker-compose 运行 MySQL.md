---
title: 使用 docker-compose 运行 MySQL
date: 2019-09-18 11:45 +0800
categories: [Docker]
tags: [Docker, MySQL]
seo:
  date_modified: 2019-09-18 11:55:52 +0800
---

## 目录结构

```shell
.
│  .env
│  docker-compose.yml
│
└─mysql
    ├─config
    │      my.cnf
    │
    └─data
```

mysql 目录下的 data 为数据目录，mysql 的数据表、二进制日志文件就在这里。.env 文件包含了一些变量，这些变量可以在 docker-compose.yml 文件中通过 ${variable_name} 来引用。

> 当然也可以把 mysql 的目录放到其它地方，这里图个方便，直接放在 yml 文件同级目录了。

## .env 文件

```text
MYSQL_ROOT_PASSWORD=root
MYSQL_ROOT_HOST=%

MYSQL_DIR=./mysql
```

## MySQL 配置文件 my.cnf

```text
[mysqld]
character-set-server=utf8mb4
default-time-zone='+8:00'
innodb_rollback_on_timeout='ON'
max_connections=500
innodb_lock_wait_timeout=500
```

如果使用默认配置，这个文件可以省略。

## docker-compose.yml

```yaml
version: '3'

services:

  mysql-db:
    container_name: mysql-docker        # 指定容器的名称
    image: mysql:8.0                   # 指定镜像和版本
    ports:
      - "3306:3306"
    environment:
      MYSQL_ROOT_PASSWORD: ${MYSQL_ROOT_PASSWORD}
      MYSQL_ROOT_HOST: ${MYSQL_ROOT_HOST}
    volumes:
      - "${MYSQL_DIR}/data:/var/lib/mysql"           # 挂载数据目录
      - "${MYSQL_DIR}/config:/etc/mysql/conf.d"      # 挂载配置文件目录
```

### Environment 变量

- `MYSQL_ROOT_PASSWORD` ：这个不用解释，root 用户的密码。
- `MYSQL_USER`，`MYSQL_PASSWORD` ：这两个变量为可选，创建一个新用户，这个用户在 `MYSQL_DATABASE` 变量指定的数据库上拥有超级用户权限。
- `MYSQL_DATABASE` ：指定一个数据库，在容器启动时创建。
- `MYSQL_ALLOW_EMPTY_PASSWORD` ：设置为 yes 允许 root 用户的密码为空。（不推荐）
- `MYSQL_RANDOM_ROOT_PASSWORD` ：设置为 yes 将在容器启动时为 root 用户生成一个随机的密码，密码会显示到标准输出流（`GENERATED ROOT PASSWORD:......`）。
- `MYSQL_ONETIME_PASSWORD` ：字面意思就是一次性密码，为 root 用户设置，第一次登录后必须修改密码（仅支持 5.6 以上的版本）。

## 运行容器

在 docker-compose.yml 目录下执行：

```shell
> docker-compose up
```

如果要在后台运行，使用 `docker-compose up -d` 。

停止容器：

```shell
> docker-compose down
```

如果是前台运行的，使用：<kbd>Ctrl</kbd> + <kbd>C</kbd> 停止。这两种方式在停止后都会删除容器，下次启动必须使用 up 命令。

停止但不删除容器：

```shell
> docker-compose stop
```

使用 stop 停止后，再次启动使用 start 命令即可。

