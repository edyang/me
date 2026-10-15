---
layout: post
title: 高性能研究：减少对象分配之前先量化来源
subtitle: 看到垃圾回收耗时就建立对象池，可能增加共享状态和内存保留，反而让程序更复杂。
date: 2016-12-15 08:00:00 +0800
author: edyang
header-style: text
catalog: true
tags:
- 高并发
- 性能分析
tech_note: true
note_id: high-performance-memory-allocation
permalink: /tech/2016/12/15/high-performance-memory-allocation/
excerpt: 看到垃圾回收耗时就建立对象池，可能增加共享状态和内存保留，反而让程序更复杂。
privacy_reviewed: true
content_revision: 3
images:
- /img/tech-notes/high-performance-memory-allocation.svg
technology_since: '2015-01-01'
---

看到垃圾回收耗时就建立对象池，可能增加共享状态和内存保留，反而让程序更复杂。

本文使用有限容量的 Java 服务与固定输入的实验负载。性能问题需要同时看吞吐、排队、错误和延迟分布。示例数字用于演算与设计实验，不代表任何真实系统已经达到的性能成绩。

## 1. 从现象推到机制

对象分配速率、存活时间和保留链共同影响回收成本。短命小对象可能很便宜，长寿命大对象才是另一类问题。对象池延长生命周期，还可能需要同步与重置，不能从“少 new”直接推出更快。

![高性能研究：减少对象分配之前先量化来源的处理、反馈与观察关系](/img/tech-notes/high-performance-memory-allocation.svg)

图中的四个节点分别表示分配来源、生命周期、局部优化、结果比较。顺着实线检查输入如何变成输出，再沿虚线核对反馈条件。图示表达的是本文讨论的关系，不是实测曲线或现场截图。

## 2. 最小实现与输入条件

先定位高频分配路径，再区分重复中间对象与必要业务对象。对照优化前后的分配量、回收后存活量和请求延迟。

```text
measure allocation rate
measure live set after collection
identify repeated temporary transformations
change one hot path
compare throughput, tail latency, retained memory
```

从稳定低负载开始增加压力，分别记录进入与完成速率。固定请求数据、连接策略和观察窗口，保留错误响应；只有成功请求的平均耗时不足以代表系统体验。

## 3. 用对照区分原因

下表列出需要主动改变的条件。预期行为来自机制分析，复现时还需记录运行环境和原始输出，不能将预期当作已经测得的结果。

| 改变的条件 | 需要验证的行为 |
| --- | --- |
| 分配很多但很快回收 | 不必然形成长期内存问题 |
| 池中对象持续积累 | 可能增加保留内存 |
| 复用对象未重置字段 | 可能造成跨请求数据残留 |

### 对照 1：分配很多但很快回收

不必然形成长期内存问题。观察时记录分配速率与回收后存活量。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 2：池中对象持续积累

可能增加保留内存。观察时记录池容量与使用后归还情况。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 3：复用对象未重置字段

可能造成跨请求数据残留。观察时记录每次任务开始时的对象状态。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。

## 4. 适用条件与取舍

性能改动必须保留正确性边界。减少分配不能以混淆请求归属、泄漏数据或破坏线程安全为代价。

一次正常运行只覆盖了这组输入。继续扩展前，应把上面的异常对照保留下来，尤其关注“复用对象未重置字段”这一分支。后续方案若改变了图中任意一处依赖，原来的判断就要重新验证，不能仅凭界面相似或返回值相同沿用结论。

## 同月延伸

- [高性能框架研究：Disruptor 的序号比环形数组更关键](/tech/2016/12/05/disruptor-ring-buffer-sequence/)
- [高并发系统研究：过载时拒绝比无限等待更可控](/tech/2016/12/25/high-concurrency-overload-design/)

## 参考资料

1. [Java 8 并发 API](https://docs.oracle.com/javase/8/docs/api/java/util/concurrent/package-summary.html)
2. [LMAX Disruptor 技术论文](https://lmax-exchange.github.io/disruptor/files/Disruptor-1.0.pdf)
