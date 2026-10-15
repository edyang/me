---
layout: post
title: 分布式编号研究：时间、节点与序号的约束
subtitle: 分库后自增编号不再天然全局唯一。
date: 2016-10-15 08:00:00 +0800
author: edyang
header-style: text
catalog: true
tags:
- 分库分表
- 系统架构
tech_note: true
note_id: distributed-id-clock-boundary
permalink: /tech/2016/10/15/distributed-id-clock-boundary/
excerpt: 分库后自增编号不再天然全局唯一。
privacy_reviewed: true
content_revision: 3
images:
- /img/tech-notes/distributed-id-clock-boundary.svg
technology_since: '2015-01-01'
---

分库后自增编号不再天然全局唯一。组合式编号方案也有节点分配和时钟边界。

本文使用关系数据库的逻辑分片演算与路由伪代码。分片把单点容量问题变成数据路由与跨分片协调问题。先确定业务访问模式和事务边界，再决定是否值得承担新的复杂度。

## 1. 从现象推到机制

时间字段、节点字段与局部序号可以组合成有序编号，但位宽决定容量和生命周期。节点号重复会冲突，时钟回退也可能使旧时间片重新出现。全局唯一与严格按业务完成顺序排序不是同一承诺。

![分布式编号研究：时间、节点与序号的约束的处理、反馈与观察关系](/img/tech-notes/distributed-id-clock-boundary.svg)

图中的四个节点分别表示时间部分、节点身份、局部序号、全局结果。顺着实线检查输入如何变成输出，再沿虚线核对反馈条件。图示表达的是本文讨论的关系，不是实测曲线或现场截图。

## 2. 最小实现与输入条件

先用纸面位分配计算每毫秒容量，再定义节点号取得方式与回退处理。示例是结构演算，不是可直接上线的编号器。

```text
id = timestamp_part | worker_part | sequence_part
require unique worker ownership
if clock moves backward: stop or use explicit recovery policy
if sequence exhausted: wait for next allowed time slot
```

在演示数据中保存分片键、路由版本与业务身份。先验证查询能否定位，再检查扩容、聚合和故障恢复；路由函数能运行不表示全生命周期已经正确。

## 3. 用对照区分原因

下表列出需要主动改变的条件。预期行为来自机制分析，复现时还需记录运行环境和原始输出，不能将预期当作已经测得的结果。

| 改变的条件 | 需要验证的行为 |
| --- | --- |
| 两个进程使用同一节点号 | 可能生成冲突编号 |
| 时钟发生回退 | 必须进入明确异常处理 |
| 单时间片序号耗尽 | 不能静默循环覆盖旧序号 |

### 对照 1：两个进程使用同一节点号

可能生成冲突编号。观察时记录节点身份的独占分配。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 2：时钟发生回退

必须进入明确异常处理。观察时记录当前时间与上次生成时间。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 3：单时间片序号耗尽

不能静默循环覆盖旧序号。观察时记录位宽容量与等待策略。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。

## 4. 适用条件与取舍

编号中的时间信息可能泄露业务节奏，不一定适合直接作为公开凭据。权限和不可猜测访问令牌应另外设计。

一次正常运行只覆盖了这组输入。继续扩展前，应把上面的异常对照保留下来，尤其关注“单时间片序号耗尽”这一分支。后续方案若改变了图中任意一处依赖，原来的判断就要重新验证，不能仅凭界面相似或返回值相同沿用结论。

## 同月延伸

- [分库分表研究：分片键要跟主要查询走](/tech/2016/10/05/sharding-key-query-affinity/)
- [分库分表研究：全局排序和聚合会付出什么成本](/tech/2016/10/25/sharding-cross-shard-pagination/)

## 参考资料

1. [MySQL 5.6 历史源码](https://github.com/mysql/mysql-server/tree/mysql-5.6.23)
2. [Twitter Snowflake 原始项目](https://github.com/twitter-archive/snowflake)
