---
layout: post
title: MyBatis：一级缓存不等于全局实时数据
subtitle: 同一个查询在一个会话中重复执行，可能没有再次访问数据库。
date: 2015-08-05 08:00:00 +0800
author: edyang
header-style: text
catalog: true
tags:
- MyBatis
- SQL
tech_note: true
note_id: mybatis-cache-invalidation
permalink: /tech/2015/08/05/mybatis-cache-invalidation/
excerpt: 同一个查询在一个会话中重复执行，可能没有再次访问数据库。
privacy_reviewed: true
content_revision: 3
images:
- /img/tech-notes/mybatis-cache-invalidation.svg
technology_since: '2015-01-01'
---

同一个查询在一个会话中重复执行，可能没有再次访问数据库。缓存范围要与事务边界一起理解。

本文使用MyBatis 3.2 系列、Java 7 与 JDBC 数据源，XML 为 Mapper 片段。MyBatis（SQL 映射框架）让查询显式可见，也要求开发者对参数、结果结构和执行成本负责。映射成功不代表查询满足权限与业务约束。

## 1. 从现象推到机制

一级缓存通常属于 SqlSession，其命中与语句、参数、会话及清理时机相关。二级缓存是另一套命名空间层面的配置。跨会话更新和外部写入可能改变缓存适用条件，不能默认所有读取都实时。

![MyBatis：一级缓存不等于全局实时数据的处理、反馈与观察关系](/img/tech-notes/mybatis-cache-invalidation.svg)

图中的四个节点分别表示会话查询、另一事务、重复读取、失效策略。顺着实线检查输入如何变成输出，再沿虚线核对反馈条件。图示表达的是本文讨论的关系，不是实测曲线或现场截图。

## 2. 最小实现与输入条件

用两个会话分别读写演示行，比较同一会话重复查询与新会话查询。记录实际 SQL 次数，不用对象值恰好相同来推断命中。

```text
session A: select id=1
session B: update id=1 -> commit
session A: select id=1
new session: select id=1
```

先准备两三条能区分边界的数据，输出参数化 SQL 与映射结果。会话与事务由明确的管理方式维护；使用 Spring 集成时，不再手工提交同一受管事务。

## 3. 用对照区分原因

下表列出需要主动改变的条件。预期行为来自机制分析，复现时还需记录运行环境和原始输出，不能将预期当作已经测得的结果。

| 改变的条件 | 需要验证的行为 |
| --- | --- |
| 同会话重复同参数查询 | 可能复用本地缓存 |
| 外部会话提交更新 | 旧会话结果还受缓存与隔离影响 |
| 跨命名空间关联数据变化 | 需审查二级缓存失效范围 |

### 对照 1：同会话重复同参数查询

可能复用本地缓存。观察时记录实际是否再次发出 SQL。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 2：外部会话提交更新

旧会话结果还受缓存与隔离影响。观察时记录缓存清理和事务快照。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 3：跨命名空间关联数据变化

需审查二级缓存失效范围。观察时记录更新所属空间与查询依赖。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。

## 4. 适用条件与取舍

高一致性场景先明确读语义，再决定缓存。缓存配置应服务已测得的瓶颈，不能仅为了少几条 SQL 就牺牲不允许陈旧的业务结果。

一次正常运行只覆盖了这组输入。继续扩展前，应把上面的异常对照保留下来，尤其关注“跨命名空间关联数据变化”这一分支。后续方案若改变了图中任意一处依赖，原来的判断就要重新验证，不能仅凭界面相似或返回值相同沿用结论。

## 同月延伸

- [MyBatis：批处理执行、刷新和事务提交](/tech/2015/08/15/mybatis-batch-insert-flush/)
- [MyBatis：分页不只是给 SQL 加 limit](/tech/2015/08/25/mybatis-pagination-stable-order/)

## 参考资料

1. [MyBatis 3 SQL 映射文档](https://mybatis.org/mybatis-3/sqlmap-xml.html)
2. [MyBatis 3.2.8 源码](https://github.com/mybatis/mybatis-3/tree/mybatis-3.2.8)
