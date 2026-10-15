---
layout: post
title: 深入 PostgreSQL：B-tree、GIN 与 BRIN 怎样选择
subtitle: 数据库支持多种索引，并不表示新类型就更适合当前查询。
date: 2017-04-25 08:00:00 +0800
author: edyang
header-style: text
catalog: true
tags:
- PostgreSQL
- 数据库
tech_note: true
note_id: postgres96-index-types
permalink: /tech/2017/04/25/postgres96-index-types/
excerpt: 数据库支持多种索引，并不表示新类型就更适合当前查询。
privacy_reviewed: true
content_revision: 3
images:
- /img/tech-notes/postgres96-index-types.svg
technology_since: '2016-09-29'
---

数据库支持多种索引，并不表示新类型就更适合当前查询。要从操作符和数据分布开始。

本文使用PostgreSQL 9.6 与独立演示库。PostgreSQL（关系数据库）的类型、事务和执行计划需要按版本理解。本文使用九点六时期已经存在的能力，不把后续大版本的 SQL 语法提前放入示例。

## 1. 从现象推到机制

B-tree 常用于等值、范围与排序，GIN 适合某些多值包含检索，BRIN 利用块范围摘要，适合数据与物理顺序有较强相关的场景。索引支持的操作符决定能服务哪些条件，体积小也不代表过滤精确。

![深入 PostgreSQL：B-tree、GIN 与 BRIN 怎样选择的处理、反馈与观察关系](/img/tech-notes/postgres96-index-types.svg)

图中的四个节点分别表示查询操作符、数据分布、索引机制、实际计划。顺着实线检查输入如何变成输出，再沿虚线核对反馈条件。图示表达的是本文讨论的关系，不是实测曲线或现场截图。

## 2. 最小实现与输入条件

为独立时间序列表比较 B-tree 与 BRIN，再为 jsonb 条件单独研究 GIN。每次只评估一类查询与数据分布。

```sql
CREATE INDEX ix_event_time ON demo.events USING brin(event_time);
EXPLAIN SELECT id FROM demo.events
WHERE event_time >= '2017-01-01'::timestamp;
```

先确认服务器版本、连接身份和 schema（模式），再在演示表中执行。涉及并发时使用两个独立会话；执行计划可能真正运行语句，写操作应在可回滚的测试事务内观察。

## 3. 用对照区分原因

下表列出需要主动改变的条件。预期行为来自机制分析，复现时还需记录运行环境和原始输出，不能将预期当作已经测得的结果。

| 改变的条件 | 需要验证的行为 |
| --- | --- |
| 时间与物理写入顺序相关 | BRIN 可能有效跳过块范围 |
| 数据顺序高度混乱 | 范围摘要过滤能力可能下降 |
| 查询使用不匹配操作符 | 索引未必能参与定位 |

### 对照 1：时间与物理写入顺序相关

BRIN 可能有效跳过块范围。观察时记录相关性与重新检查行数。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 2：数据顺序高度混乱

范围摘要过滤能力可能下降。观察时记录同一区块时间分布。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 3：查询使用不匹配操作符

索引未必能参与定位。观察时记录操作符类与执行计划。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。

## 4. 适用条件与取舍

建索引有写入与维护成本。比较时包含构建、更新和存储开销，不能只比较一条查询的耗时。

一次正常运行只覆盖了这组输入。继续扩展前，应把上面的异常对照保留下来，尤其关注“查询使用不匹配操作符”这一分支。后续方案若改变了图中任意一处依赖，原来的判断就要重新验证，不能仅凭界面相似或返回值相同沿用结论。

## 同月延伸

- [深入 PostgreSQL：更新为什么会留下旧版本](/tech/2017/04/05/postgres96-mvcc-vacuum/)
- [深入 PostgreSQL：EXPLAIN ANALYZE 会真正执行语句](/tech/2017/04/15/postgres96-explain-analyze/)

## 参考资料

1. [PostgreSQL 9.6 文档](https://www.postgresql.org/docs/9.6/)
2. [PostgreSQL 9.6 发布记录](https://www.postgresql.org/about/news/postgresql-96-released-1703/)
