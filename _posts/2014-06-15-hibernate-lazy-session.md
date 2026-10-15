---
layout: post
title: Hibernate：懒加载异常为什么发生在页面渲染时
subtitle: 服务层已经查到订单，模板访问明细时却抛错，往往因为懒加载发生在会话关闭之后。
date: 2014-06-15 08:00:00 +0800
author: edyang
header-style: text
catalog: true
tags:
- Hibernate
- 数据库
tech_note: true
note_id: hibernate-lazy-session
permalink: /tech/2014/06/15/hibernate-lazy-session/
excerpt: 服务层已经查到订单，模板访问明细时却抛错，往往因为懒加载发生在会话关闭之后。
privacy_reviewed: true
content_revision: 3
images:
- /img/tech-notes/hibernate-lazy-session.svg
technology_since: '2013-12-01'
---

服务层已经查到订单，模板访问明细时却抛错，往往因为懒加载发生在会话关闭之后。

本文使用Hibernate ORM 4.3、JDK 7 与独立关系数据库，代码为映射或调用片段。ORM（对象关系映射）连接对象生命周期与数据库行，但不会取消事务、索引和并发约束。观察对象属性的同时，也需要查看真正发出的 SQL 与提交边界。

## 1. 从现象推到机制

懒加载代理推迟关联读取，访问未初始化属性时需要有效会话。把会话一直延长到页面可以隐藏某些异常，却可能让模板悄悄发 SQL。更清楚的做法是按用例准备需要的数据视图。

![Hibernate：懒加载异常为什么发生在页面渲染时的处理、反馈与观察关系](/img/tech-notes/hibernate-lazy-session.svg)

图中的四个节点分别表示服务查询、关联加载、展示对象、模板渲染。顺着实线检查输入如何变成输出，再沿虚线核对反馈条件。图示表达的是本文讨论的关系，不是实测曲线或现场截图。

## 2. 最小实现与输入条件

在事务内读取本页真正需要的字段，组装只读展示对象；需要关联时使用明确查询策略。不要为了消除一个异常把所有关联都设为立即加载。

```java
Order order = repository.find(id);
OrderView view = new OrderView();
view.setNumber(order.getNumber());
view.setLineCount(order.getLines().size());
return view;
```

先建立只有订单与明细的演示模型，启用 SQL 日志并准备少量固定数据。会话、事务和连接分别关闭；读取结果正确之外，还要观察语句数量和异常发生阶段。

## 3. 用对照区分原因

下表列出需要主动改变的条件。预期行为来自机制分析，复现时还需记录运行环境和原始输出，不能将预期当作已经测得的结果。

| 改变的条件 | 需要验证的行为 |
| --- | --- |
| 会话关闭后访问未初始化集合 | 可能发生懒加载异常 |
| 关联已经在事务内读取 | 展示阶段不再需要补查 |
| 所有关联改立即加载 | 可能带来大量不必要数据 |

### 对照 1：会话关闭后访问未初始化集合

可能发生懒加载异常。观察时记录访问时会话与代理状态。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 2：关联已经在事务内读取

展示阶段不再需要补查。观察时记录查询发生的位置。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 3：所有关联改立即加载

可能带来大量不必要数据。观察时记录SQL 数量与实际页面字段。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。

## 4. 适用条件与取舍

数据视图也有成本，需要按页面用途设计。若接口返回整棵实体图，容易产生循环序列化、越权字段和不可控查询。

一次正常运行只覆盖了这组输入。继续扩展前，应把上面的异常对照保留下来，尤其关注“所有关联改立即加载”这一分支。后续方案若改变了图中任意一处依赖，原来的判断就要重新验证，不能仅凭界面相似或返回值相同沿用结论。

## 同月延伸

- [Hibernate：瞬时、持久与游离对象的区别](/tech/2014/06/05/hibernate-entity-state/)
- [Hibernate：一对多映射中谁维护外键](/tech/2014/06/25/hibernate-one-to-many-owner/)

## 参考资料

1. [Hibernate ORM 4.3 手册](https://docs.hibernate.org/orm/4.3/manual/en-US/html_single/)
2. [Java Persistence 2.1 规范](https://jcp.org/en/jsr/detail?id=338)
