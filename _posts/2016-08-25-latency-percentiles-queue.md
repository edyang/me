---
layout: post
title: 高并发研究：平均延迟会遮住哪些问题
subtitle: 大多数请求很快，少部分等待数秒，平均值仍可能看起来不错。
date: 2016-08-25 08:00:00 +0800
author: edyang
header-style: text
catalog: true
tags:
- 高并发
- 性能分析
tech_note: true
note_id: latency-percentiles-queue
permalink: /tech/2016/08/25/latency-percentiles-queue/
excerpt: 大多数请求很快，少部分等待数秒，平均值仍可能看起来不错。
privacy_reviewed: true
content_revision: 3
images:
- /img/tech-notes/latency-percentiles-queue.svg
technology_since: '2015-01-01'
---

大多数请求很快，少部分等待数秒，平均值仍可能看起来不错。用户遇到的尾部延迟不能被平均掉。

本文使用有限容量的 Java 服务与固定输入的实验负载。性能问题需要同时看吞吐、排队、错误和延迟分布。示例数字用于演算与设计实验，不代表任何真实系统已经达到的性能成绩。

## 1. 从现象推到机制

分位数描述分布位置，不同接口和请求规模混合后会失去解释性。排队、垃圾回收和慢依赖都可能制造尾部。多个服务的分位数也不能直接相加当成整条链路的同一分位数。

![高并发研究：平均延迟会遮住哪些问题的处理、反馈与观察关系](/img/tech-notes/latency-percentiles-queue.svg)

图中的四个节点分别表示单请求耗时、分层分布、尾部来源、整体体验。顺着实线检查输入如何变成输出，再沿虚线核对反馈条件。图示表达的是本文讨论的关系，不是实测曲线或现场截图。

## 2. 最小实现与输入条件

按接口类别记录完整请求耗时，包含错误响应，并同时展示样本量。比较优化前后使用同等负载，不只截取最好的一段时间。

```text
record latency for each request
group by endpoint and outcome
report count, median, p95, p99, max
also report queue_wait and dependency_time
```

从稳定低负载开始增加压力，分别记录进入与完成速率。固定请求数据、连接策略和观察窗口，保留错误响应；只有成功请求的平均耗时不足以代表系统体验。

## 3. 用对照区分原因

下表列出需要主动改变的条件。预期行为来自机制分析，复现时还需记录运行环境和原始输出，不能将预期当作已经测得的结果。

| 改变的条件 | 需要验证的行为 |
| --- | --- |
| 少量请求极慢 | 平均值变化可能很小 |
| 把轻重接口混合统计 | 分布可能受请求比例变化影响 |
| 直接相加多个服务 p99 | 不能得到可靠的端到端 p99 |

### 对照 1：少量请求极慢

平均值变化可能很小。观察时记录高分位与最大值。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 2：把轻重接口混合统计

分布可能受请求比例变化影响。观察时记录各接口样本量与独立分布。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 3：直接相加多个服务 p99

不能得到可靠的端到端 p99。观察时记录同一请求的真实链路耗时。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。

## 4. 适用条件与取舍

高分位需要足够样本和稳定测量。样本很少时应直接展示原始范围，不用精确百分位制造不必要的确定感。

一次正常运行只覆盖了这组输入。继续扩展前，应把上面的异常对照保留下来，尤其关注“直接相加多个服务 p99”这一分支。后续方案若改变了图中任意一处依赖，原来的判断就要重新验证，不能仅凭界面相似或返回值相同沿用结论。

## 同月延伸

- [高并发研究：用 Little 定律理解在途请求](/tech/2016/08/05/concurrency-littles-law/)
- [高并发研究：压测客户端也可能掩盖过载](/tech/2016/08/15/load-test-open-closed-model/)

## 参考资料

1. [Java 8 并发 API](https://docs.oracle.com/javase/8/docs/api/java/util/concurrent/package-summary.html)
2. [LMAX Disruptor 技术论文](https://lmax-exchange.github.io/disruptor/files/Disruptor-1.0.pdf)
