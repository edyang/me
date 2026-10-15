---
layout: post
title: 深入 PostgreSQL：更新为什么会留下旧版本
subtitle: 表频繁更新后体积增长，不一定是数据行数增加。
date: 2017-04-05 08:00:00 +0800
author: edyang
header-style: text
catalog: true
tags:
- PostgreSQL
- 数据库
tech_note: true
note_id: postgres96-mvcc-vacuum
permalink: /tech/2017/04/05/postgres96-mvcc-vacuum/
excerpt: 表频繁更新后体积增长，不一定是数据行数增加。
privacy_reviewed: true
content_revision: 3
images:
- /img/tech-notes/postgres96-mvcc-vacuum.svg
technology_since: '2016-09-29'
---

表频繁更新后体积增长，不一定是数据行数增加。MVCC 需要保留对其他事务仍可见的旧版本。

本文使用PostgreSQL 9.6 与独立演示库。PostgreSQL（关系数据库）的类型、事务和执行计划需要按版本理解。本文使用九点六时期已经存在的能力，不把后续大版本的 SQL 语法提前放入示例。

## 1. 从现象推到机制

MVCC（多版本并发控制）通过行版本支持并发可见性，旧版本在不再需要后才能清理。VACUUM 回收可复用空间并维护可见性相关信息，普通 vacuum 不等于把文件立即缩小。长事务会阻碍部分清理进度。

![深入 PostgreSQL：更新为什么会留下旧版本的处理、反馈与观察关系](/img/tech-notes/postgres96-mvcc-vacuum.svg)

图中的四个节点分别表示并发事务、行版本更新、清理条件、空间复用。顺着实线检查输入如何变成输出，再沿虚线核对反馈条件。图示表达的是本文讨论的关系，不是实测曲线或现场截图。

## 2. 最小实现与输入条件

用演示表进行多次更新，观察统计视图和活动事务。先找长事务来源，再考虑是否需要更重的维护操作。

```sql
SELECT relname, n_live_tup, n_dead_tup
FROM pg_stat_user_tables WHERE relname='demo_rows';
SELECT pid, xact_start, state FROM pg_stat_activity;
```

先确认服务器版本、连接身份和 schema（模式），再在演示表中执行。涉及并发时使用两个独立会话；执行计划可能真正运行语句，写操作应在可回滚的测试事务内观察。

## 3. 用对照区分原因

下表列出需要主动改变的条件。预期行为来自机制分析，复现时还需记录运行环境和原始输出，不能将预期当作已经测得的结果。

| 改变的条件 | 需要验证的行为 |
| --- | --- |
| 持续更新同一批行 | 可能产生大量死元组 |
| 长事务一直不结束 | 旧版本可能继续被保留 |
| 运行普通 VACUUM | 空间可复用但文件不必缩小 |

### 对照 1：持续更新同一批行

可能产生大量死元组。观察时记录存活与死元组统计。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 2：长事务一直不结束

旧版本可能继续被保留。观察时记录最老事务开始时刻。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 3：运行普通 VACUUM

空间可复用但文件不必缩小。观察时记录表文件大小与后续复用情况。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。

## 4. 适用条件与取舍

统计视图包含估计值，不能作为逐行精确计数。维护方式还需考虑锁、I/O 与业务窗口，不应直接在繁忙实例尝试重写表。

一次正常运行只覆盖了这组输入。继续扩展前，应把上面的异常对照保留下来，尤其关注“运行普通 VACUUM”这一分支。后续方案若改变了图中任意一处依赖，原来的判断就要重新验证，不能仅凭界面相似或返回值相同沿用结论。

## 同月延伸

- [深入 PostgreSQL：EXPLAIN ANALYZE 会真正执行语句](/tech/2017/04/15/postgres96-explain-analyze/)
- [深入 PostgreSQL：B-tree、GIN 与 BRIN 怎样选择](/tech/2017/04/25/postgres96-index-types/)

## 参考资料

1. [PostgreSQL 9.6 文档](https://www.postgresql.org/docs/9.6/)
2. [PostgreSQL 9.6 发布记录](https://www.postgresql.org/about/news/postgresql-96-released-1703/)
