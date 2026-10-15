---
layout: post
title: 深入 PostgreSQL：先确认连到哪台库和哪个 schema
subtitle: 表明明存在却提示找不到，或查到另一组数据，先别急着重建表。
date: 2017-03-05 08:00:00 +0800
author: edyang
header-style: text
catalog: true
tags:
- PostgreSQL
- 数据库
tech_note: true
note_id: postgres96-connection-schema
permalink: /tech/2017/03/05/postgres96-connection-schema/
excerpt: 表明明存在却提示找不到，或查到另一组数据，先别急着重建表。
privacy_reviewed: true
content_revision: 3
images:
- /img/tech-notes/postgres96-connection-schema.svg
technology_since: '2016-09-29'
---

表明明存在却提示找不到，或查到另一组数据，先别急着重建表。连接目标与搜索路径需要核对。

本文使用PostgreSQL 9.6 与独立演示库。PostgreSQL（关系数据库）的类型、事务和执行计划需要按版本理解。本文使用九点六时期已经存在的能力，不把后续大版本的 SQL 语法提前放入示例。

## 1. 从现象推到机制

服务器、数据库、用户和 schema 都参与对象定位。search_path 决定未限定名称按什么顺序解析，同名表可能存在于不同模式。连接池配置与手工终端不一致时，两边看到的对象自然不同。

![深入 PostgreSQL：先确认连到哪台库和哪个 schema的处理、反馈与观察关系](/img/tech-notes/postgres96-connection-schema.svg)

图中的四个节点分别表示连接身份、搜索路径、模式对象、权限范围。顺着实线检查输入如何变成输出，再沿虚线核对反馈条件。图示表达的是本文讨论的关系，不是实测曲线或现场截图。

## 2. 最小实现与输入条件

从实际出错连接执行只读身份查询，再用模式限定表名。避免只在另一终端连接里证明数据库正常。

```sql
SELECT version(), current_database(), current_user;
SHOW search_path;
SELECT current_schema();
SELECT count(*) FROM demo.orders;
```

先确认服务器版本、连接身份和 schema（模式），再在演示表中执行。涉及并发时使用两个独立会话；执行计划可能真正运行语句，写操作应在可回滚的测试事务内观察。

## 3. 用对照区分原因

下表列出需要主动改变的条件。预期行为来自机制分析，复现时还需记录运行环境和原始输出，不能将预期当作已经测得的结果。

| 改变的条件 | 需要验证的行为 |
| --- | --- |
| 两个模式都有 orders | 未限定名称可能定位不同对象 |
| 手工连接正常而应用失败 | 比较应用真实连接参数 |
| 角色没有模式使用权限 | 表存在也可能无法访问 |

### 对照 1：两个模式都有 orders

未限定名称可能定位不同对象。观察时记录search_path 与实际表模式。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 2：手工连接正常而应用失败

比较应用真实连接参数。观察时记录数据库用户和目标实例。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 3：角色没有模式使用权限

表存在也可能无法访问。观察时记录schema 与表的权限分别检查。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。

## 4. 适用条件与取舍

搜索路径还会影响安全边界。应用账号只应拥有所需模式和对象权限，不要通过提升为超级用户掩盖配置问题。

一次正常运行只覆盖了这组输入。继续扩展前，应把上面的异常对照保留下来，尤其关注“角色没有模式使用权限”这一分支。后续方案若改变了图中任意一处依赖，原来的判断就要重新验证，不能仅凭界面相似或返回值相同沿用结论。

## 同月延伸

- [深入 PostgreSQL：编码、时区与时间字段语义](/tech/2017/03/15/postgres96-encoding-timezone/)
- [深入 PostgreSQL：pg_dump 成功后还要验证恢复](/tech/2017/03/25/postgres96-backup-restore/)

## 参考资料

1. [PostgreSQL 9.6 文档](https://www.postgresql.org/docs/9.6/)
2. [PostgreSQL 9.6 发布记录](https://www.postgresql.org/about/news/postgresql-96-released-1703/)
