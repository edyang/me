---
layout: post
title: Hibernate：flush 与 commit 为什么不是同一个动作
subtitle: SQL 日志已经出现 UPDATE，另一个连接却还看不到变化，这是事务可见性而非日志矛盾。
date: 2014-07-05 08:00:00 +0800
author: edyang
header-style: text
catalog: true
tags:
- Hibernate
- 数据库
tech_note: true
note_id: hibernate-transaction-flush
permalink: /tech/2014/07/05/hibernate-transaction-flush/
excerpt: SQL 日志已经出现 UPDATE，另一个连接却还看不到变化，这是事务可见性而非日志矛盾。
privacy_reviewed: true
content_revision: 3
images:
- /img/tech-notes/hibernate-transaction-flush.svg
technology_since: '2013-12-01'
---

SQL 日志已经出现 UPDATE，另一个连接却还看不到变化，这是事务可见性而非日志矛盾。

本文使用Hibernate ORM 4.3、JDK 7 与独立关系数据库，代码为映射或调用片段。ORM（对象关系映射）连接对象生命周期与数据库行，但不会取消事务、索引和并发约束。观察对象属性的同时，也需要查看真正发出的 SQL 与提交边界。

## 1. 从现象推到机制

flush 将持久化上下文的变更同步成数据库语句，commit 才尝试提交事务。刷新可能在查询前或提交前发生，约束异常也可能延迟到这个阶段。执行了 SQL 的事务仍可以回滚。

![Hibernate：flush 与 commit 为什么不是同一个动作的处理、反馈与观察关系](/img/tech-notes/hibernate-transaction-flush.svg)

图中的四个节点分别表示实体修改、刷新动作、事务提交、独立观察。顺着实线检查输入如何变成输出，再沿虚线核对反馈条件。图示表达的是本文讨论的关系，不是实测曲线或现场截图。

## 2. 最小实现与输入条件

用两个数据库连接分别观察事务内与事务外的值，显式 flush 后暂不提交。实验必须明确隔离级别，不能跨环境混用结论。

```java
Transaction tx = session.beginTransaction();
order.setRemark("new");
session.flush();
// 此时尚未提交
tx.rollback();
```

先建立只有订单与明细的演示模型，启用 SQL 日志并准备少量固定数据。会话、事务和连接分别关闭；读取结果正确之外，还要观察语句数量和异常发生阶段。

## 3. 用对照区分原因

下表列出需要主动改变的条件。预期行为来自机制分析，复现时还需记录运行环境和原始输出，不能将预期当作已经测得的结果。

| 改变的条件 | 需要验证的行为 |
| --- | --- |
| 刷新后回滚 | 已发出的更新不应作为提交结果保留 |
| 查询触发自动刷新 | 异常可能出现在查询语句附近 |
| 唯一约束冲突延后暴露 | 应处理刷新或提交阶段异常 |

### 对照 1：刷新后回滚

已发出的更新不应作为提交结果保留。观察时记录独立连接在事务结束后的值。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 2：查询触发自动刷新

异常可能出现在查询语句附近。观察时记录此前待写入实体与实际 SQL。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 3：唯一约束冲突延后暴露

应处理刷新或提交阶段异常。观察时记录数据库返回的约束名称。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。

## 4. 适用条件与取舍

数据库事务无法回滚已发送的邮件或外部支付。业务操作要区分本地持久化与外部副作用，不能因方法上有事务就认为整体原子。

一次正常运行只覆盖了这组输入。继续扩展前，应把上面的异常对照保留下来，尤其关注“唯一约束冲突延后暴露”这一分支。后续方案若改变了图中任意一处依赖，原来的判断就要重新验证，不能仅凭界面相似或返回值相同沿用结论。

## 同月延伸

- [Hibernate：版本字段怎样避免覆盖别人的修改](/tech/2014/07/15/hibernate-optimistic-locking/)
- [Hibernate：分页查询与 N+1 不能只改 fetch](/tech/2014/07/25/hibernate-pagination-n-plus-one/)

## 参考资料

1. [Hibernate ORM 4.3 手册](https://docs.hibernate.org/orm/4.3/manual/en-US/html_single/)
2. [Java Persistence 2.1 规范](https://jcp.org/en/jsr/detail?id=338)
