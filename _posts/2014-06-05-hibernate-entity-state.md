---
layout: post
title: Hibernate：瞬时、持久与游离对象的区别
subtitle: 对象里有一个数据库编号，不代表它当前正在被会话管理。
date: 2014-06-05 08:00:00 +0800
author: edyang
header-style: text
catalog: true
tags:
- Hibernate
- 数据库
tech_note: true
note_id: hibernate-entity-state
permalink: /tech/2014/06/05/hibernate-entity-state/
excerpt: 对象里有一个数据库编号，不代表它当前正在被会话管理。
privacy_reviewed: true
content_revision: 3
images:
- /img/tech-notes/hibernate-entity-state.svg
technology_since: '2013-12-01'
---

对象里有一个数据库编号，不代表它当前正在被会话管理。实体状态决定了修改如何进入数据库。

本文使用Hibernate ORM 4.3、JDK 7 与独立关系数据库，代码为映射或调用片段。ORM（对象关系映射）连接对象生命周期与数据库行，但不会取消事务、索引和并发约束。观察对象属性的同时，也需要查看真正发出的 SQL 与提交边界。

## 1. 从现象推到机制

新建对象尚未与持久化上下文关联，持久态对象被当前会话追踪，游离态对象保留数据但已离开原上下文。merge 返回的是合并后的受管理实例，不应继续假定传入对象就是当前持久对象。

![Hibernate：瞬时、持久与游离对象的区别的处理、反馈与观察关系](/img/tech-notes/hibernate-entity-state.svg)

图中的四个节点分别表示新建对象、当前会话、会话关闭、再次合并。顺着实线检查输入如何变成输出，再沿虚线核对反馈条件。图示表达的是本文讨论的关系，不是实测曲线或现场截图。

## 2. 最小实现与输入条件

先保存一条演示订单并关闭会话，再修改游离对象。开启新事务执行 merge，比较传入对象与返回对象的身份和数据库值。

```java
Order detached = loadThenCloseSession(id);
detached.setRemark("demo");
Order managed = (Order) session.merge(detached);
// 后续在当前事务中使用 managed
```

先建立只有订单与明细的演示模型，启用 SQL 日志并准备少量固定数据。会话、事务和连接分别关闭；读取结果正确之外，还要观察语句数量和异常发生阶段。

## 3. 用对照区分原因

下表列出需要主动改变的条件。预期行为来自机制分析，复现时还需记录运行环境和原始输出，不能将预期当作已经测得的结果。

| 改变的条件 | 需要验证的行为 |
| --- | --- |
| 会话关闭后修改对象 | 不会凭修改本身自动落库 |
| 调用 merge 后忽略返回值 | 可能继续操作游离实例 |
| 事务提交前触发 flush | SQL 发出不等于事务已提交 |

### 对照 1：会话关闭后修改对象

不会凭修改本身自动落库。观察时记录对象是否仍被当前上下文追踪。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 2：调用 merge 后忽略返回值

可能继续操作游离实例。观察时记录返回对象与传入对象身份。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 3：事务提交前触发 flush

SQL 发出不等于事务已提交。观察时记录刷新时刻与最终提交结果。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。

## 4. 适用条件与取舍

实体状态与业务状态不要混用。订单“已支付”属于业务语义，而游离或持久只是 ORM 管理关系，两者需要不同字段和判断。

一次正常运行只覆盖了这组输入。继续扩展前，应把上面的异常对照保留下来，尤其关注“事务提交前触发 flush”这一分支。后续方案若改变了图中任意一处依赖，原来的判断就要重新验证，不能仅凭界面相似或返回值相同沿用结论。

## 同月延伸

- [Hibernate：懒加载异常为什么发生在页面渲染时](/tech/2014/06/15/hibernate-lazy-session/)
- [Hibernate：一对多映射中谁维护外键](/tech/2014/06/25/hibernate-one-to-many-owner/)

## 参考资料

1. [Hibernate ORM 4.3 手册](https://docs.hibernate.org/orm/4.3/manual/en-US/html_single/)
2. [Java Persistence 2.1 规范](https://jcp.org/en/jsr/detail?id=338)
