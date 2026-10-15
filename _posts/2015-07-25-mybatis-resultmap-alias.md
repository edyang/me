---
layout: post
title: MyBatis：联表结果的别名与 resultMap
subtitle: 两张表都有 id 和 name，联表后直接映射，容易让字段来源变得含糊。
date: 2015-07-25 08:00:00 +0800
author: edyang
header-style: text
catalog: true
tags:
- MyBatis
- SQL
tech_note: true
note_id: mybatis-resultmap-alias
permalink: /tech/2015/07/25/mybatis-resultmap-alias/
excerpt: 两张表都有 id 和 name，联表后直接映射，容易让字段来源变得含糊。
privacy_reviewed: true
content_revision: 3
images:
- /img/tech-notes/mybatis-resultmap-alias.svg
technology_since: '2015-01-01'
---

两张表都有 id 和 name，联表后直接映射，容易让字段来源变得含糊。

本文使用MyBatis 3.2 系列、Java 7 与 JDBC 数据源，XML 为 Mapper 片段。MyBatis（SQL 映射框架）让查询显式可见，也要求开发者对参数、结果结构和执行成本负责。映射成功不代表查询满足权限与业务约束。

## 1. 从现象推到机制

结果列名是映射的输入接口。显式别名可以让订单编号与客户编号分开，再通过 resultMap 声明属性。嵌套集合还需要正确的身份列帮助合并行，不能把连接行简单当成独立订单。

![MyBatis：联表结果的别名与 resultMap的处理、反馈与观察关系](/img/tech-notes/mybatis-resultmap-alias.svg)

图中的四个节点分别表示联表数据、结果别名、映射规则、业务视图。顺着实线检查输入如何变成输出，再沿虚线核对反馈条件。图示表达的是本文讨论的关系，不是实测曲线或现场截图。

## 2. 最小实现与输入条件

先只查两个实体的少量字段，明确每个别名归属。避免 SELECT *，让表结构增加字段时不悄悄改变接口形状。

```sql
SELECT o.id AS order_id,
       c.id AS customer_id, c.name AS customer_name
FROM orders o
JOIN customer c ON c.id = o.customer_id;
```

先准备两三条能区分边界的数据，输出参数化 SQL 与映射结果。会话与事务由明确的管理方式维护；使用 Spring 集成时，不再手工提交同一受管事务。

## 3. 用对照区分原因

下表列出需要主动改变的条件。预期行为来自机制分析，复现时还需记录运行环境和原始输出，不能将预期当作已经测得的结果。

| 改变的条件 | 需要验证的行为 |
| --- | --- |
| 两表列名相同 | 应使用不同别名表达来源 |
| 一张订单对应多个明细行 | 映射后根对象应按身份归并 |
| 新增表字段 | 显式列清单不受无关字段影响 |

### 对照 1：两表列名相同

应使用不同别名表达来源。观察时记录结果集列标签。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 2：一张订单对应多个明细行

映射后根对象应按身份归并。观察时记录resultMap 的 id 定义。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 3：新增表字段

显式列清单不受无关字段影响。观察时记录查询输出列是否稳定。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。

## 4. 适用条件与取舍

映射结构与查询成本要一起评估。嵌套查询写起来方便，却可能产生 N+1；嵌套结果映射也可能放大返回行数。

一次正常运行只覆盖了这组输入。继续扩展前，应把上面的异常对照保留下来，尤其关注“新增表字段”这一分支。后续方案若改变了图中任意一处依赖，原来的判断就要重新验证，不能仅凭界面相似或返回值相同沿用结论。

## 同月延伸

- [MyBatis：占位参数与字符串替换的边界](/tech/2015/07/05/mybatis-parameter-binding/)
- [MyBatis：动态 where 与空条件的业务风险](/tech/2015/07/15/mybatis-dynamic-where/)

## 参考资料

1. [MyBatis 3 SQL 映射文档](https://mybatis.org/mybatis-3/sqlmap-xml.html)
2. [MyBatis 3.2.8 源码](https://github.com/mybatis/mybatis-3/tree/mybatis-3.2.8)
