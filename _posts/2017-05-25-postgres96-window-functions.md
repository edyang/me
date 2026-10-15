---
layout: post
title: 深入 PostgreSQL：窗口函数保留明细又计算排名
subtitle: 既想显示每条订单，又想看到该客户最近一单，普通聚合会把明细折叠掉。
date: 2017-05-25 08:00:00 +0800
author: edyang
header-style: text
catalog: true
tags:
- PostgreSQL
- 数据库
tech_note: true
note_id: postgres96-window-functions
permalink: /tech/2017/05/25/postgres96-window-functions/
excerpt: 既想显示每条订单，又想看到该客户最近一单，普通聚合会把明细折叠掉。
privacy_reviewed: true
content_revision: 3
images:
- /img/tech-notes/postgres96-window-functions.svg
technology_since: '2016-09-29'
---

既想显示每条订单，又想看到该客户最近一单，普通聚合会把明细折叠掉。窗口函数提供另一种表达。

本文使用PostgreSQL 9.6 与独立演示库。PostgreSQL（关系数据库）的类型、事务和执行计划需要按版本理解。本文使用九点六时期已经存在的能力，不把后续大版本的 SQL 语法提前放入示例。

## 1. 从现象推到机制

窗口函数在分区内计算，同时保留每行。row_number 与 rank 对并列的处理不同，窗口排序也不等于最终结果排序。累计计算还需理解 frame（窗口帧）默认范围，同值排序字段可能改变直觉。

![深入 PostgreSQL：窗口函数保留明细又计算排名的处理、反馈与观察关系](/img/tech-notes/postgres96-window-functions.svg)

图中的四个节点分别表示明细输入、窗口分区、窗口顺序、外层筛选。顺着实线检查输入如何变成输出，再沿虚线核对反馈条件。图示表达的是本文讨论的关系，不是实测曲线或现场截图。

## 2. 最小实现与输入条件

以客户分区，按创建时间和编号倒序编号，再在外层筛选第一行。唯一次级键让最近一单的选择可重复。

```sql
SELECT * FROM (
 SELECT id,owner_id,
 row_number() OVER (PARTITION BY owner_id
   ORDER BY created_at DESC,id DESC) AS rn
 FROM demo.orders
) x WHERE rn=1;
```

先确认服务器版本、连接身份和 schema（模式），再在演示表中执行。涉及并发时使用两个独立会话；执行计划可能真正运行语句，写操作应在可回滚的测试事务内观察。

## 3. 用对照区分原因

下表列出需要主动改变的条件。预期行为来自机制分析，复现时还需记录运行环境和原始输出，不能将预期当作已经测得的结果。

| 改变的条件 | 需要验证的行为 |
| --- | --- |
| 两单创建时间相同 | 仍由编号确定唯一顺序 |
| 改用 rank 处理并列 | 可能返回多个相同名次 |
| 窗口有排序但外层没有 | 最终展示顺序仍不保证 |

### 对照 1：两单创建时间相同

仍由编号确定唯一顺序。观察时记录完整窗口 ORDER BY。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 2：改用 rank 处理并列

可能返回多个相同名次。观察时记录排名函数的并列规则。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 3：窗口有排序但外层没有

最终展示顺序仍不保证。观察时记录最终查询的 ORDER BY。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。

## 4. 适用条件与取舍

窗口计算可能需要排序和额外内存，数据量大时查看执行计划。不要因为 SQL 更短就忽略中间结果规模。

一次正常运行只覆盖了这组输入。继续扩展前，应把上面的异常对照保留下来，尤其关注“窗口有排序但外层没有”这一分支。后续方案若改变了图中任意一处依赖，原来的判断就要重新验证，不能仅凭界面相似或返回值相同沿用结论。

## 同月延伸

- [深入 PostgreSQL：JSONB 与关系字段各放什么](/tech/2017/05/05/postgres96-jsonb-relational-boundary/)
- [深入 PostgreSQL：递归 CTE 查询组织树](/tech/2017/05/15/postgres96-recursive-cte-tree/)

## 参考资料

1. [PostgreSQL 9.6 文档](https://www.postgresql.org/docs/9.6/)
2. [PostgreSQL 9.6 发布记录](https://www.postgresql.org/about/news/postgresql-96-released-1703/)
