---
layout: post
title: 深入 PostgreSQL：编码、时区与时间字段语义
subtitle: 同一时刻在两台机器显示不同，可能是时区呈现差异；乱码则需要沿字符编码链路分析。
date: 2017-03-15 08:00:00 +0800
author: edyang
header-style: text
catalog: true
tags:
- PostgreSQL
- 数据库
tech_note: true
note_id: postgres96-encoding-timezone
permalink: /tech/2017/03/15/postgres96-encoding-timezone/
excerpt: 同一时刻在两台机器显示不同，可能是时区呈现差异；乱码则需要沿字符编码链路分析。
privacy_reviewed: true
content_revision: 3
images:
- /img/tech-notes/postgres96-encoding-timezone.svg
technology_since: '2016-09-29'
---

同一时刻在两台机器显示不同，可能是时区呈现差异；乱码则需要沿字符编码链路分析。

本文使用PostgreSQL 9.6 与独立演示库。PostgreSQL（关系数据库）的类型、事务和执行计划需要按版本理解。本文使用九点六时期已经存在的能力，不把后续大版本的 SQL 语法提前放入示例。

## 1. 从现象推到机制

timestamptz 表达绝对时刻并按会话时区展示，timestamp without time zone 不携带相同的时区语义。字符集编码和时区是两套配置。把本地墙上时间当绝对时刻保存，会让跨时区与夏令时处理复杂。

![深入 PostgreSQL：编码、时区与时间字段语义的处理、反馈与观察关系](/img/tech-notes/postgres96-encoding-timezone.svg)

图中的四个节点分别表示业务含义、字段类型、会话设置、接口交换。顺着实线检查输入如何变成输出，再沿虚线核对反馈条件。图示表达的是本文讨论的关系，不是实测曲线或现场截图。

## 2. 最小实现与输入条件

查询服务器与客户端编码、会话时区，再切换演示会话时区读取同一时刻。业务日期字段与事件时刻分别设计。

```sql
SHOW server_encoding;
SHOW client_encoding;
SHOW TimeZone;
SELECT now(), now() AT TIME ZONE 'UTC';
```

先确认服务器版本、连接身份和 schema（模式），再在演示表中执行。涉及并发时使用两个独立会话；执行计划可能真正运行语句，写操作应在可回滚的测试事务内观察。

## 3. 用对照区分原因

下表列出需要主动改变的条件。预期行为来自机制分析，复现时还需记录运行环境和原始输出，不能将预期当作已经测得的结果。

| 改变的条件 | 需要验证的行为 |
| --- | --- |
| 切换会话时区显示同一时刻 | 显示值可变但绝对时刻不变 |
| 无时区字符串写入时间字段 | 解释依赖具体类型和上下文 |
| 中文显示异常 | 需要核对编码而非调整时区 |

### 对照 1：切换会话时区显示同一时刻

显示值可变但绝对时刻不变。观察时记录字段类型和会话配置。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 2：无时区字符串写入时间字段

解释依赖具体类型和上下文。观察时记录输入约定与目标列类型。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 3：中文显示异常

需要核对编码而非调整时区。观察时记录原始字节和客户端编码。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。

## 4. 适用条件与取舍

报表按日汇总时要明确业务时区，不能默认数据库会话时区就是业务规则。交换接口也要带清楚的时间表示。

一次正常运行只覆盖了这组输入。继续扩展前，应把上面的异常对照保留下来，尤其关注“中文显示异常”这一分支。后续方案若改变了图中任意一处依赖，原来的判断就要重新验证，不能仅凭界面相似或返回值相同沿用结论。

## 同月延伸

- [深入 PostgreSQL：先确认连到哪台库和哪个 schema](/tech/2017/03/05/postgres96-connection-schema/)
- [深入 PostgreSQL：pg_dump 成功后还要验证恢复](/tech/2017/03/25/postgres96-backup-restore/)

## 参考资料

1. [PostgreSQL 9.6 文档](https://www.postgresql.org/docs/9.6/)
2. [PostgreSQL 9.6 发布记录](https://www.postgresql.org/about/news/postgresql-96-released-1703/)
