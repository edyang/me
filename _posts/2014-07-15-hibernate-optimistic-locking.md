---
layout: post
title: Hibernate：版本字段怎样避免覆盖别人的修改
subtitle: 两个人先后打开同一订单，各自保存，后保存者可能把前一个人的修改覆盖掉。
date: 2014-07-15 08:00:00 +0800
author: edyang
header-style: text
catalog: true
tags:
- Hibernate
- 数据库
tech_note: true
note_id: hibernate-optimistic-locking
permalink: /tech/2014/07/15/hibernate-optimistic-locking/
excerpt: 两个人先后打开同一订单，各自保存，后保存者可能把前一个人的修改覆盖掉。
privacy_reviewed: true
content_revision: 3
images:
- /img/tech-notes/hibernate-optimistic-locking.svg
technology_since: '2013-12-01'
---

两个人先后打开同一订单，各自保存，后保存者可能把前一个人的修改覆盖掉。版本字段用于发现这种竞争。

本文使用Hibernate ORM 4.3、JDK 7 与独立关系数据库，代码为映射或调用片段。ORM（对象关系映射）连接对象生命周期与数据库行，但不会取消事务、索引和并发约束。观察对象属性的同时，也需要查看真正发出的 SQL 与提交边界。

## 1. 从现象推到机制

乐观锁把读取时版本带到更新条件中，只有版本仍匹配才更新并增加版本号。更新行数为零意味着内容已经变化或记录不存在，需要重新读取并决定如何处理，不应盲目用旧值再覆盖一次。

![Hibernate：版本字段怎样避免覆盖别人的修改的处理、反馈与观察关系](/img/tech-notes/hibernate-optimistic-locking.svg)

图中的四个节点分别表示读取版本、本地修改、条件更新、冲突处理。顺着实线检查输入如何变成输出，再沿虚线核对反馈条件。图示表达的是本文讨论的关系，不是实测曲线或现场截图。

## 2. 最小实现与输入条件

给演示实体加入 @Version，两个独立会话读取同一行，分别修改后依次提交。保留冲突时的业务提示与重载路径。

```java
@Version
private long version;
// 概念 SQL：
// UPDATE orders SET remark=?, version=version+1
// WHERE id=? AND version=?
```

先建立只有订单与明细的演示模型，启用 SQL 日志并准备少量固定数据。会话、事务和连接分别关闭；读取结果正确之外，还要观察语句数量和异常发生阶段。

## 3. 用对照区分原因

下表列出需要主动改变的条件。预期行为来自机制分析，复现时还需记录运行环境和原始输出，不能将预期当作已经测得的结果。

| 改变的条件 | 需要验证的行为 |
| --- | --- |
| 两个会话读取相同版本 | 第二次冲突写入应被发现 |
| 冲突后直接重试旧实体 | 仍可能违背用户原意 |
| 批量 SQL 绕开实体更新 | 需自行维护版本约束 |

### 对照 1：两个会话读取相同版本

第二次冲突写入应被发现。观察时记录更新条件中的旧版本号。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 2：冲突后直接重试旧实体

仍可能违背用户原意。观察时记录哪些字段基于旧数据判断。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 3：批量 SQL 绕开实体更新

需自行维护版本约束。观察时记录实际 SQL 是否包含版本条件。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。

## 4. 适用条件与取舍

乐观锁减少静默覆盖，不替代业务唯一约束。对库存扣减等操作，仍应在数据库条件中表达数量不能为负的规则。

一次正常运行只覆盖了这组输入。继续扩展前，应把上面的异常对照保留下来，尤其关注“批量 SQL 绕开实体更新”这一分支。后续方案若改变了图中任意一处依赖，原来的判断就要重新验证，不能仅凭界面相似或返回值相同沿用结论。

## 同月延伸

- [Hibernate：flush 与 commit 为什么不是同一个动作](/tech/2014/07/05/hibernate-transaction-flush/)
- [Hibernate：分页查询与 N+1 不能只改 fetch](/tech/2014/07/25/hibernate-pagination-n-plus-one/)

## 参考资料

1. [Hibernate ORM 4.3 手册](https://docs.hibernate.org/orm/4.3/manual/en-US/html_single/)
2. [Java Persistence 2.1 规范](https://jcp.org/en/jsr/detail?id=338)
