---
layout: post
title: 分库分表研究：全局排序和聚合会付出什么成本
subtitle: 每个分片取二十条后拼起来，不能直接当成全局第二页。
date: 2016-10-25 08:00:00 +0800
author: edyang
header-style: text
catalog: true
tags:
- 分库分表
- 系统架构
tech_note: true
note_id: sharding-cross-shard-pagination
permalink: /tech/2016/10/25/sharding-cross-shard-pagination/
excerpt: 每个分片取二十条后拼起来，不能直接当成全局第二页。
privacy_reviewed: true
content_revision: 3
images:
- /img/tech-notes/sharding-cross-shard-pagination.svg
technology_since: '2015-01-01'
---

每个分片取二十条后拼起来，不能直接当成全局第二页。跨分片排序需要统一比较和边界。

本文使用关系数据库的逻辑分片演算与路由伪代码。分片把单点容量问题变成数据路由与跨分片协调问题。先确定业务访问模式和事务边界，再决定是否值得承担新的复杂度。

## 1. 从现象推到机制

全局有序结果可以从各分片候选集合归并，但深分页可能需要读取越来越多候选。聚合计数与金额也需要同口径和一致性窗口。部分分片失败时，返回的不能仍假装是完整统计。

![分库分表研究：全局排序和聚合会付出什么成本的处理、反馈与观察关系](/img/tech-notes/sharding-cross-shard-pagination.svg)

图中的四个节点分别表示分片候选、统一归并、全局游标、完整性。顺着实线检查输入如何变成输出，再沿虚线核对反馈条件。图示表达的是本文讨论的关系，不是实测曲线或现场截图。

## 2. 最小实现与输入条件

用两个分片各十条演示记录，按时间与唯一编号归并。先处理第一页，再分析后续游标需要保存哪些各分片位置。

```text
for each shard: fetch bounded ordered candidates
merge by (created_at, global_id)
return first page and routing-aware cursor
aggregate response includes completeness status
```

在演示数据中保存分片键、路由版本与业务身份。先验证查询能否定位，再检查扩容、聚合和故障恢复；路由函数能运行不表示全生命周期已经正确。

## 3. 用对照区分原因

下表列出需要主动改变的条件。预期行为来自机制分析，复现时还需记录运行环境和原始输出，不能将预期当作已经测得的结果。

| 改变的条件 | 需要验证的行为 |
| --- | --- |
| 各分片时间有同值 | 仍需全局唯一次级排序键 |
| 某一分片超时 | 结果应标注不完整或整体失败 |
| 偏移页码越来越深 | 候选读取成本可能快速上升 |

### 对照 1：各分片时间有同值

仍需全局唯一次级排序键。观察时记录归并比较器的完整规则。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 2：某一分片超时

结果应标注不完整或整体失败。观察时记录参与分片与失败范围。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 3：偏移页码越来越深

候选读取成本可能快速上升。观察时记录实际读取与返回数量之比。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。

## 4. 适用条件与取舍

经营分析类查询可能更适合独立汇总模型。不要为了保持单库一样的任意 SQL，给在线分片系统增加无限广播。

一次正常运行只覆盖了这组输入。继续扩展前，应把上面的异常对照保留下来，尤其关注“偏移页码越来越深”这一分支。后续方案若改变了图中任意一处依赖，原来的判断就要重新验证，不能仅凭界面相似或返回值相同沿用结论。

## 同月延伸

- [分库分表研究：分片键要跟主要查询走](/tech/2016/10/05/sharding-key-query-affinity/)
- [分布式编号研究：时间、节点与序号的约束](/tech/2016/10/15/distributed-id-clock-boundary/)

## 参考资料

1. [MySQL 5.6 历史源码](https://github.com/mysql/mysql-server/tree/mysql-5.6.23)
2. [Twitter Snowflake 原始项目](https://github.com/twitter-archive/snowflake)
