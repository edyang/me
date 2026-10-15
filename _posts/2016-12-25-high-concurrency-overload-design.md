---
layout: post
title: 高并发系统研究：过载时拒绝比无限等待更可控
subtitle: 入口持续接收超出能力的请求，会让排队、内存和超时一起增长。
date: 2016-12-25 08:00:00 +0800
author: edyang
header-style: text
catalog: true
tags:
- 高并发
- 性能分析
tech_note: true
note_id: high-concurrency-overload-design
permalink: /tech/2016/12/25/high-concurrency-overload-design/
excerpt: 入口持续接收超出能力的请求，会让排队、内存和超时一起增长。
privacy_reviewed: true
content_revision: 3
images:
- /img/tech-notes/high-concurrency-overload-design.svg
technology_since: '2015-01-01'
---

入口持续接收超出能力的请求，会让排队、内存和超时一起增长。系统需要明确承载边界。

本文使用有限容量的 Java 服务与固定输入的实验负载。性能问题需要同时看吞吐、排队、错误和延迟分布。示例数字用于演算与设计实验，不代表任何真实系统已经达到的性能成绩。

## 1. 从现象推到机制

限流控制进入速率，有限队列限制等待，超时限制资源占用，隔离减少故障传播。它们解决不同问题，需要按同一容量预算协调。拒绝结果应该可识别，调用方重试也必须有退避，避免形成更大洪峰。

![高并发系统研究：过载时拒绝比无限等待更可控的处理、反馈与观察关系](/img/tech-notes/high-concurrency-overload-design.svg)

图中的四个节点分别表示入口流量、容量约束、过载反馈、恢复观察。顺着实线检查输入如何变成输出，再沿虚线核对反馈条件。图示表达的是本文讨论的关系，不是实测曲线或现场截图。

## 2. 最小实现与输入条件

给演示服务设置最大在途数量与短队列，压测时同时观察成功吞吐、拒绝率和排队时间。目标是稳定退化，而非只追求接收数。

```text
if in_flight >= capacity or queue_is_full:
    return explicit_busy_response
else:
    accept with deadline
caller retries only when allowed, with bounded backoff
```

从稳定低负载开始增加压力，分别记录进入与完成速率。固定请求数据、连接策略和观察窗口，保留错误响应；只有成功请求的平均耗时不足以代表系统体验。

## 3. 用对照区分原因

下表列出需要主动改变的条件。预期行为来自机制分析，复现时还需记录运行环境和原始输出，不能将预期当作已经测得的结果。

| 改变的条件 | 需要验证的行为 |
| --- | --- |
| 进入速率长期超过完成能力 | 应触发可识别拒绝而非无限积压 |
| 调用方立即无限重试 | 会进一步放大故障流量 |
| 负载恢复到容量以内 | 系统应逐步清空等待并恢复 |

### 对照 1：进入速率长期超过完成能力

应触发可识别拒绝而非无限积压。观察时记录在途数队列与拒绝率。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 2：调用方立即无限重试

会进一步放大故障流量。观察时记录原请求与重试的比例。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 3：负载恢复到容量以内

系统应逐步清空等待并恢复。观察时记录队列回落和尾部延迟。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。

## 4. 适用条件与取舍

容量数字需要在目标环境验证，并为故障与重任务保留余量。拒绝策略也要与业务协商，关键写入不可被静默丢弃。

一次正常运行只覆盖了这组输入。继续扩展前，应把上面的异常对照保留下来，尤其关注“负载恢复到容量以内”这一分支。后续方案若改变了图中任意一处依赖，原来的判断就要重新验证，不能仅凭界面相似或返回值相同沿用结论。

## 同月延伸

- [高性能框架研究：Disruptor 的序号比环形数组更关键](/tech/2016/12/05/disruptor-ring-buffer-sequence/)
- [高性能研究：减少对象分配之前先量化来源](/tech/2016/12/15/high-performance-memory-allocation/)

## 参考资料

1. [Java 8 并发 API](https://docs.oracle.com/javase/8/docs/api/java/util/concurrent/package-summary.html)
2. [LMAX Disruptor 技术论文](https://lmax-exchange.github.io/disruptor/files/Disruptor-1.0.pdf)
