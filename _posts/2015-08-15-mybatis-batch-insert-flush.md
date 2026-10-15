---
layout: post
title: MyBatis：批处理执行、刷新和事务提交
subtitle: 批量接口返回了控制流，不代表每一行都已被数据库成功写入。
date: 2015-08-15 08:00:00 +0800
author: edyang
header-style: text
catalog: true
tags:
- MyBatis
- SQL
tech_note: true
note_id: mybatis-batch-insert-flush
permalink: /tech/2015/08/15/mybatis-batch-insert-flush/
excerpt: 批量接口返回了控制流，不代表每一行都已被数据库成功写入。
privacy_reviewed: true
content_revision: 3
images:
- /img/tech-notes/mybatis-batch-insert-flush.svg
technology_since: '2015-01-01'
---

批量接口返回了控制流，不代表每一行都已被数据库成功写入。批执行需要检查真正刷新时的结果。

本文使用MyBatis 3.2 系列、Java 7 与 JDBC 数据源，XML 为 Mapper 片段。MyBatis（SQL 映射框架）让查询显式可见，也要求开发者对参数、结果结构和执行成本负责。映射成功不代表查询满足权限与业务约束。

## 1. 从现象推到机制

批处理执行器可能延后发送或汇集语句，错误在刷新时才出现。flushStatements 处理批结果，不等于事务 commit。批大小影响内存、锁持有和网络次数，过大批次也可能延长失败恢复。

![MyBatis：批处理执行、刷新和事务提交的处理、反馈与观察关系](/img/tech-notes/mybatis-batch-insert-flush.svg)

图中的四个节点分别表示输入批次、执行队列、批刷新、事务结束。顺着实线检查输入如何变成输出，再沿虚线核对反馈条件。图示表达的是本文讨论的关系，不是实测曲线或现场截图。

## 2. 最小实现与输入条件

在独立数据集里设置小批量，故意让中间一条违反约束。检查异常发生位置、事务最终状态和重复执行的幂等性。

```text
open batch session
for each row:
    mapper.insert(row)
flush statements and inspect results
commit transaction
# 失败路径 rollback 并关闭会话
```

先准备两三条能区分边界的数据，输出参数化 SQL 与映射结果。会话与事务由明确的管理方式维护；使用 Spring 集成时，不再手工提交同一受管事务。

## 3. 用对照区分原因

下表列出需要主动改变的条件。预期行为来自机制分析，复现时还需记录运行环境和原始输出，不能将预期当作已经测得的结果。

| 改变的条件 | 需要验证的行为 |
| --- | --- |
| 中间一行违反唯一约束 | 错误可能在批刷新时暴露 |
| 刷新后主动回滚 | 不能把已发送当成已提交 |
| 失败后重放整批 | 需要避免已确认部分重复写入 |

### 对照 1：中间一行违反唯一约束

错误可能在批刷新时暴露。观察时记录批结果与异常链。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 2：刷新后主动回滚

不能把已发送当成已提交。观察时记录独立连接看到的最终数据。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 3：失败后重放整批

需要避免已确认部分重复写入。观察时记录业务唯一键与事务边界。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。

## 4. 适用条件与取舍

不同 JDBC 驱动的批结果和失败行为可能不同，必须固定驱动版本验证。不要仅靠框架层循环次数推算数据库已写行数。

一次正常运行只覆盖了这组输入。继续扩展前，应把上面的异常对照保留下来，尤其关注“失败后重放整批”这一分支。后续方案若改变了图中任意一处依赖，原来的判断就要重新验证，不能仅凭界面相似或返回值相同沿用结论。

## 同月延伸

- [MyBatis：一级缓存不等于全局实时数据](/tech/2015/08/05/mybatis-cache-invalidation/)
- [MyBatis：分页不只是给 SQL 加 limit](/tech/2015/08/25/mybatis-pagination-stable-order/)

## 参考资料

1. [MyBatis 3 SQL 映射文档](https://mybatis.org/mybatis-3/sqlmap-xml.html)
2. [MyBatis 3.2.8 源码](https://github.com/mybatis/mybatis-3/tree/mybatis-3.2.8)
