---
layout: post
title: 深入 PostgreSQL：递归 CTE 查询组织树
subtitle: 查询一个部门及其所有下级，固定写几层 join 无法覆盖不确定深度。
date: 2017-05-15 08:00:00 +0800
author: edyang
header-style: text
catalog: true
tags:
- PostgreSQL
- 数据库
tech_note: true
note_id: postgres96-recursive-cte-tree
permalink: /tech/2017/05/15/postgres96-recursive-cte-tree/
excerpt: 查询一个部门及其所有下级，固定写几层 join 无法覆盖不确定深度。
privacy_reviewed: true
content_revision: 3
images:
- /img/tech-notes/postgres96-recursive-cte-tree.svg
technology_since: '2016-09-29'
---

查询一个部门及其所有下级，固定写几层 join 无法覆盖不确定深度。递归查询可以表达层级扩展。

本文使用PostgreSQL 9.6 与独立演示库。PostgreSQL（关系数据库）的类型、事务和执行计划需要按版本理解。本文使用九点六时期已经存在的能力，不把后续大版本的 SQL 语法提前放入示例。

## 1. 从现象推到机制

递归 CTE（公共表表达式）先提供起始集合，再反复从上一轮结果扩展。树数据如果存在环，递归可能无法自然结束，因此需要路径记录或业务约束。输出顺序也要显式指定，不凭递归执行顺序猜测。

![深入 PostgreSQL：递归 CTE 查询组织树的处理、反馈与观察关系](/img/tech-notes/postgres96-recursive-cte-tree.svg)

图中的四个节点分别表示起始节点、递归扩展、路径约束、结果排序。顺着实线检查输入如何变成输出，再沿虚线核对反馈条件。图示表达的是本文讨论的关系，不是实测曲线或现场截图。

## 2. 最小实现与输入条件

使用匿名部门表，路径数组记录已经经过的编号。九点六没有后续版本的 SEARCH/CYCLE 语法，环检测在查询中显式表达。

```sql
WITH RECURSIVE tree AS (
 SELECT id,parent_id,ARRAY[id] AS path FROM demo.dept WHERE id=1
 UNION ALL
 SELECT d.id,d.parent_id,t.path||d.id
 FROM demo.dept d JOIN tree t ON d.parent_id=t.id
 WHERE NOT d.id=ANY(t.path)
) SELECT * FROM tree ORDER BY path;
```

先确认服务器版本、连接身份和 schema（模式），再在演示表中执行。涉及并发时使用两个独立会话；执行计划可能真正运行语句，写操作应在可回滚的测试事务内观察。

## 3. 用对照区分原因

下表列出需要主动改变的条件。预期行为来自机制分析，复现时还需记录运行环境和原始输出，不能将预期当作已经测得的结果。

| 改变的条件 | 需要验证的行为 |
| --- | --- |
| 部门层级超过预期 | 递归可继续扩展而非固定层数 |
| 数据意外形成环 | 路径条件应防止重复进入 |
| 希望按树顺序展示 | 需要明确排序规则 |

### 对照 1：部门层级超过预期

递归可继续扩展而非固定层数。观察时记录每轮新增节点与路径。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 2：数据意外形成环

路径条件应防止重复进入。观察时记录当前编号是否已在路径中。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 3：希望按树顺序展示

需要明确排序规则。观察时记录最终 ORDER BY 而非执行偶然顺序。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。

## 4. 适用条件与取舍

递归查询不能替代写入时的数据治理。修改父节点前也要防止建立环，深树和宽树还需评估返回规模。

一次正常运行只覆盖了这组输入。继续扩展前，应把上面的异常对照保留下来，尤其关注“希望按树顺序展示”这一分支。后续方案若改变了图中任意一处依赖，原来的判断就要重新验证，不能仅凭界面相似或返回值相同沿用结论。

## 同月延伸

- [深入 PostgreSQL：JSONB 与关系字段各放什么](/tech/2017/05/05/postgres96-jsonb-relational-boundary/)
- [深入 PostgreSQL：窗口函数保留明细又计算排名](/tech/2017/05/25/postgres96-window-functions/)

## 参考资料

1. [PostgreSQL 9.6 文档](https://www.postgresql.org/docs/9.6/)
2. [PostgreSQL 9.6 发布记录](https://www.postgresql.org/about/news/postgresql-96-released-1703/)
