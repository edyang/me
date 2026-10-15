---
layout: post
title: Hibernate：一对多映射中谁维护外键
subtitle: 集合里加入了明细，数据库外键却没有按预期变化，需要检查关联维护方而不是只看对象结构。
date: 2014-06-25 08:00:00 +0800
author: edyang
header-style: text
catalog: true
tags:
- Hibernate
- 数据库
tech_note: true
note_id: hibernate-one-to-many-owner
permalink: /tech/2014/06/25/hibernate-one-to-many-owner/
excerpt: 集合里加入了明细，数据库外键却没有按预期变化，需要检查关联维护方而不是只看对象结构。
privacy_reviewed: true
content_revision: 3
images:
- /img/tech-notes/hibernate-one-to-many-owner.svg
technology_since: '2013-12-01'
---

集合里加入了明细，数据库外键却没有按预期变化，需要检查关联维护方而不是只看对象结构。

本文使用Hibernate ORM 4.3、JDK 7 与独立关系数据库，代码为映射或调用片段。ORM（对象关系映射）连接对象生命周期与数据库行，但不会取消事务、索引和并发约束。观察对象属性的同时，也需要查看真正发出的 SQL 与提交边界。

## 1. 从现象推到机制

双向关联有两边的对象引用，但数据库外键通常只有一份。mappedBy 指出由另一侧负责关系写入，逆向集合修改并不总能单独产生需要的外键更新。级联决定操作传播，不等于关联归属。

![Hibernate：一对多映射中谁维护外键的处理、反馈与观察关系](/img/tech-notes/hibernate-one-to-many-owner.svg)

图中的四个节点分别表示业务关联、对象两侧、外键拥有方、生命周期。顺着实线检查输入如何变成输出，再沿虚线核对反馈条件。图示表达的是本文讨论的关系，不是实测曲线或现场截图。

## 2. 最小实现与输入条件

在业务方法里同时维护两侧引用，使内存模型一致。下面为结构示例，具体注解、级联和删除策略需要按业务选择。

```java
public void addLine(OrderLine line) {
    lines.add(line);
    line.setOrder(this);
}
// Order.lines: @OneToMany(mappedBy="order")
// OrderLine.order: @ManyToOne
```

先建立只有订单与明细的演示模型，启用 SQL 日志并准备少量固定数据。会话、事务和连接分别关闭；读取结果正确之外，还要观察语句数量和异常发生阶段。

## 3. 用对照区分原因

下表列出需要主动改变的条件。预期行为来自机制分析，复现时还需记录运行环境和原始输出，不能将预期当作已经测得的结果。

| 改变的条件 | 需要验证的行为 |
| --- | --- |
| 只修改逆向集合 | 可能没有期望的外键写入 |
| 只设置明细的订单引用 | 数据库可正确但内存两侧不一致 |
| 删除集合元素 | 是否删行取决于映射和业务规则 |

### 对照 1：只修改逆向集合

可能没有期望的外键写入。观察时记录实际拥有方字段是否更新。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 2：只设置明细的订单引用

数据库可正确但内存两侧不一致。观察时记录当前集合是否包含该明细。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 3：删除集合元素

是否删行取决于映射和业务规则。观察时记录级联与 orphan removal 配置。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。

## 4. 适用条件与取舍

不要为了省一次显式操作启用所有级联删除。订单历史、商品主数据和附件有不同生命周期，映射需要反映真实所有权。

一次正常运行只覆盖了这组输入。继续扩展前，应把上面的异常对照保留下来，尤其关注“删除集合元素”这一分支。后续方案若改变了图中任意一处依赖，原来的判断就要重新验证，不能仅凭界面相似或返回值相同沿用结论。

## 同月延伸

- [Hibernate：瞬时、持久与游离对象的区别](/tech/2014/06/05/hibernate-entity-state/)
- [Hibernate：懒加载异常为什么发生在页面渲染时](/tech/2014/06/15/hibernate-lazy-session/)

## 参考资料

1. [Hibernate ORM 4.3 手册](https://docs.hibernate.org/orm/4.3/manual/en-US/html_single/)
2. [Java Persistence 2.1 规范](https://jcp.org/en/jsr/detail?id=338)
