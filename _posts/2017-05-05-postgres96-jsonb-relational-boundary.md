---
layout: post
title: 深入 PostgreSQL：JSONB 与关系字段各放什么
subtitle: 把所有字段塞进 JSONB 很灵活，也可能让约束、统计和查询变得难以管理。
date: 2017-05-05 08:00:00 +0800
author: edyang
header-style: text
catalog: true
tags:
- PostgreSQL
- 数据库
tech_note: true
note_id: postgres96-jsonb-relational-boundary
permalink: /tech/2017/05/05/postgres96-jsonb-relational-boundary/
excerpt: 把所有字段塞进 JSONB 很灵活，也可能让约束、统计和查询变得难以管理。
privacy_reviewed: true
content_revision: 3
images:
- /img/tech-notes/postgres96-jsonb-relational-boundary.svg
technology_since: '2016-09-29'
---

把所有字段塞进 JSONB 很灵活，也可能让约束、统计和查询变得难以管理。

本文使用PostgreSQL 9.6 与独立演示库。PostgreSQL（关系数据库）的类型、事务和执行计划需要按版本理解。本文使用九点六时期已经存在的能力，不把后续大版本的 SQL 语法提前放入示例。

## 1. 从现象推到机制

稳定身份、关联与关键约束适合显式列，变化较多的扩展属性可以放 JSONB。JSONB 不保留原始文本的全部格式与重复键，不能作为需要字节级原文留存的替代。GIN 能支持部分包含查询，但仍要匹配操作符。

![深入 PostgreSQL：JSONB 与关系字段各放什么的处理、反馈与观察关系](/img/tech-notes/postgres96-jsonb-relational-boundary.svg)

图中的四个节点分别表示业务字段、类型约束、检索条件、存档要求。顺着实线检查输入如何变成输出，再沿虚线核对反馈条件。图示表达的是本文讨论的关系，不是实测曲线或现场截图。

## 2. 最小实现与输入条件

用设备扩展参数作演示，设备编号独立成列，型号属性放 JSONB。先验证缺字段、数字与字符串类型差异。

```sql
SELECT id FROM demo.devices
WHERE attrs @> '{"kind":"sensor"}'::jsonb;
CREATE INDEX ix_device_attrs ON demo.devices USING gin(attrs);
```

先确认服务器版本、连接身份和 schema（模式），再在演示表中执行。涉及并发时使用两个独立会话；执行计划可能真正运行语句，写操作应在可回滚的测试事务内观察。

## 3. 用对照区分原因

下表列出需要主动改变的条件。预期行为来自机制分析，复现时还需记录运行环境和原始输出，不能将预期当作已经测得的结果。

| 改变的条件 | 需要验证的行为 |
| --- | --- |
| 关键关联字段藏在任意 JSON 中 | 会增加约束和连接难度 |
| 同字段有数字和字符串 | 查询语义可能不同 |
| 要求保留原始文档字节 | JSONB 不是原文存档 |

### 对照 1：关键关联字段藏在任意 JSON 中

会增加约束和连接难度。观察时记录业务主键与关系定义。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 2：同字段有数字和字符串

查询语义可能不同。观察时记录JSON 值的实际类型。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 3：要求保留原始文档字节

JSONB 不是原文存档。观察时记录原始文本与结构化解析结果。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。

## 4. 适用条件与取舍

灵活字段也需要版本和校验规则。长期任意写入会把模式治理推迟到每个查询里，不能因为数据库接受 JSON 就省略数据设计。

一次正常运行只覆盖了这组输入。继续扩展前，应把上面的异常对照保留下来，尤其关注“要求保留原始文档字节”这一分支。后续方案若改变了图中任意一处依赖，原来的判断就要重新验证，不能仅凭界面相似或返回值相同沿用结论。

## 同月延伸

- [深入 PostgreSQL：递归 CTE 查询组织树](/tech/2017/05/15/postgres96-recursive-cte-tree/)
- [深入 PostgreSQL：窗口函数保留明细又计算排名](/tech/2017/05/25/postgres96-window-functions/)

## 参考资料

1. [PostgreSQL 9.6 文档](https://www.postgresql.org/docs/9.6/)
2. [PostgreSQL 9.6 发布记录](https://www.postgresql.org/about/news/postgresql-96-released-1703/)
