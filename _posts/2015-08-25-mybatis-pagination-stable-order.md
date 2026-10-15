---
layout: post
title: MyBatis：分页不只是给 SQL 加 limit
subtitle: 翻到第二页出现重复记录，可能是排序不稳定，也可能是第一页之后数据发生变化。
date: 2015-08-25 08:00:00 +0800
author: edyang
header-style: text
catalog: true
tags:
- MyBatis
- SQL
tech_note: true
note_id: mybatis-pagination-stable-order
permalink: /tech/2015/08/25/mybatis-pagination-stable-order/
excerpt: 翻到第二页出现重复记录，可能是排序不稳定，也可能是第一页之后数据发生变化。
privacy_reviewed: true
content_revision: 3
images:
- /img/tech-notes/mybatis-pagination-stable-order.svg
technology_since: '2015-01-01'
---

翻到第二页出现重复记录，可能是排序不稳定，也可能是第一页之后数据发生变化。

本文使用MyBatis 3.2 系列、Java 7 与 JDBC 数据源，XML 为 Mapper 片段。MyBatis（SQL 映射框架）让查询显式可见，也要求开发者对参数、结果结构和执行成本负责。映射成功不代表查询满足权限与业务约束。

## 1. 从现象推到机制

分页必须有明确顺序，同值排序字段后面需要唯一键。深偏移分页让数据库跳过大量记录，返回十行不代表只扫描十行。游标式分页可减少偏移成本，但随机跳页和动态排序需要另作设计。

![MyBatis：分页不只是给 SQL 加 limit的处理、反馈与观察关系](/img/tech-notes/mybatis-pagination-stable-order.svg)

图中的四个节点分别表示筛选范围、稳定排序、分页游标、后续读取。顺着实线检查输入如何变成输出，再沿虚线核对反馈条件。图示表达的是本文讨论的关系，不是实测曲线或现场截图。

## 2. 最小实现与输入条件

以创建时间和编号倒序为例，游标包含最后一条的两个值。第一页与后续页使用相同过滤条件和权限范围。

```sql
SELECT id, created_at FROM orders
WHERE created_at < :last_time
   OR (created_at = :last_time AND id < :last_id)
ORDER BY created_at DESC, id DESC LIMIT 20;
```

先准备两三条能区分边界的数据，输出参数化 SQL 与映射结果。会话与事务由明确的管理方式维护；使用 Spring 集成时，不再手工提交同一受管事务。

## 3. 用对照区分原因

下表列出需要主动改变的条件。预期行为来自机制分析，复现时还需记录运行环境和原始输出，不能将预期当作已经测得的结果。

| 改变的条件 | 需要验证的行为 |
| --- | --- |
| 多条记录创建时间相同 | 唯一次级键保证确定顺序 |
| 页间插入更新记录 | 偏移分页可能发生位置漂移 |
| 游标只保存时间字段 | 相同时间记录可能遗漏 |

### 对照 1：多条记录创建时间相同

唯一次级键保证确定顺序。观察时记录相同时间内的编号排列。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 2：页间插入更新记录

偏移分页可能发生位置漂移。观察时记录分页期间的数据变化。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 3：游标只保存时间字段

相同时间记录可能遗漏。观察时记录游标是否覆盖完整排序键。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。

## 4. 适用条件与取舍

游标查询示例还需加入真实权限与筛选条件，并用括号保持布尔逻辑。导出全量一致快照与普通页面翻页是不同需求。

一次正常运行只覆盖了这组输入。继续扩展前，应把上面的异常对照保留下来，尤其关注“游标只保存时间字段”这一分支。后续方案若改变了图中任意一处依赖，原来的判断就要重新验证，不能仅凭界面相似或返回值相同沿用结论。

## 同月延伸

- [MyBatis：一级缓存不等于全局实时数据](/tech/2015/08/05/mybatis-cache-invalidation/)
- [MyBatis：批处理执行、刷新和事务提交](/tech/2015/08/15/mybatis-batch-insert-flush/)

## 参考资料

1. [MyBatis 3 SQL 映射文档](https://mybatis.org/mybatis-3/sqlmap-xml.html)
2. [MyBatis 3.2.8 源码](https://github.com/mybatis/mybatis-3/tree/mybatis-3.2.8)
