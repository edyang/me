---
layout: post
title: 深入 PostgreSQL：EXPLAIN ANALYZE 会真正执行语句
subtitle: 执行计划能解释访问路径，但带 ANALYZE 的检查不是纯静态查看。
date: 2017-04-15 08:00:00 +0800
author: edyang
header-style: text
catalog: true
tags:
- PostgreSQL
- 数据库
tech_note: true
note_id: postgres96-explain-analyze
permalink: /tech/2017/04/15/postgres96-explain-analyze/
excerpt: 执行计划能解释访问路径，但带 ANALYZE 的检查不是纯静态查看。
privacy_reviewed: true
content_revision: 3
images:
- /img/tech-notes/postgres96-explain-analyze.svg
technology_since: '2016-09-29'
---

执行计划能解释访问路径，但带 ANALYZE 的检查不是纯静态查看。

本文使用PostgreSQL 9.6 与独立演示库。PostgreSQL（关系数据库）的类型、事务和执行计划需要按版本理解。本文使用九点六时期已经存在的能力，不把后续大版本的 SQL 语法提前放入示例。

## 1. 从现象推到机制

EXPLAIN 给出规划估计，ANALYZE 执行并收集实际行数和时间。循环次数需要与每次平均值一起看，节点时间也不宜简单相加。BUFFERS 有助观察缓存与读取，但不能单独证明磁盘物理 I/O 全部细节。

![深入 PostgreSQL：EXPLAIN ANALYZE 会真正执行语句的处理、反馈与观察关系](/img/tech-notes/postgres96-explain-analyze.svg)

图中的四个节点分别表示规划估计、真实执行、循环缓冲、优化判断。顺着实线检查输入如何变成输出，再沿虚线核对反馈条件。图示表达的是本文讨论的关系，不是实测曲线或现场截图。

## 2. 最小实现与输入条件

先对只读演示查询执行，比较估计与实际行数。涉及写语句时必须意识到副作用，必要测试也应在可回滚事务和隔离环境。

```sql
EXPLAIN (ANALYZE, BUFFERS)
SELECT id FROM demo.orders
WHERE owner_id=7 ORDER BY id LIMIT 20;
```

先确认服务器版本、连接身份和 schema（模式），再在演示表中执行。涉及并发时使用两个独立会话；执行计划可能真正运行语句，写操作应在可回滚的测试事务内观察。

## 3. 用对照区分原因

下表列出需要主动改变的条件。预期行为来自机制分析，复现时还需记录运行环境和原始输出，不能将预期当作已经测得的结果。

| 改变的条件 | 需要验证的行为 |
| --- | --- |
| 估计行数与实际相差较大 | 可能影响连接和扫描选择 |
| 内层节点 loops 很多 | 累计成本需结合循环次数 |
| 对 UPDATE 使用 ANALYZE | 更新会实际执行 |

### 对照 1：估计行数与实际相差较大

可能影响连接和扫描选择。观察时记录每节点 rows 与 actual rows。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 2：内层节点 loops 很多

累计成本需结合循环次数。观察时记录每次输出与调用次数。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 3：对 UPDATE 使用 ANALYZE

更新会实际执行。观察时记录事务边界与最终数据状态。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。

## 4. 适用条件与取舍

缓存和并发负载影响时间，不能只看一次最好结果。优先找数量级差异与不必要工作，再比较局部优化。

一次正常运行只覆盖了这组输入。继续扩展前，应把上面的异常对照保留下来，尤其关注“对 UPDATE 使用 ANALYZE”这一分支。后续方案若改变了图中任意一处依赖，原来的判断就要重新验证，不能仅凭界面相似或返回值相同沿用结论。

## 同月延伸

- [深入 PostgreSQL：更新为什么会留下旧版本](/tech/2017/04/05/postgres96-mvcc-vacuum/)
- [深入 PostgreSQL：B-tree、GIN 与 BRIN 怎样选择](/tech/2017/04/25/postgres96-index-types/)

## 参考资料

1. [PostgreSQL 9.6 文档](https://www.postgresql.org/docs/9.6/)
2. [PostgreSQL 9.6 发布记录](https://www.postgresql.org/about/news/postgresql-96-released-1703/)
