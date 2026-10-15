---
layout: post
title: 高性能框架研究：Disruptor 的序号比环形数组更关键
subtitle: 环形数组只是存储形式。
date: 2016-12-05 08:00:00 +0800
author: edyang
header-style: text
catalog: true
tags:
- 高并发
- 性能分析
tech_note: true
note_id: disruptor-ring-buffer-sequence
permalink: /tech/2016/12/05/disruptor-ring-buffer-sequence/
excerpt: 环形数组只是存储形式。
privacy_reviewed: true
content_revision: 3
images:
- /img/tech-notes/disruptor-ring-buffer-sequence.svg
technology_since: '2015-01-01'
---

环形数组只是存储形式。多生产者和消费者如何知道哪些位置可以复用，才是关键协调问题。

本文使用有限容量的 Java 服务与固定输入的实验负载。性能问题需要同时看吞吐、排队、错误和延迟分布。示例数字用于演算与设计实验，不代表任何真实系统已经达到的性能成绩。

## 1. 从现象推到机制

Disruptor（环形队列框架）通过序号表达发布与消费进度，生产者不能覆盖仍被消费者使用的槽位。预分配减少部分分配成本，却要求处理完一个事件后不再随意持有可复用对象。

![高性能框架研究：Disruptor 的序号比环形数组更关键的处理、反馈与观察关系](/img/tech-notes/disruptor-ring-buffer-sequence.svg)

图中的四个节点分别表示序号申请、事件发布、消费进度、空间复用。顺着实线检查输入如何变成输出，再沿虚线核对反馈条件。图示表达的是本文讨论的关系，不是实测曲线或现场截图。

## 2. 最小实现与输入条件

先用单生产者单消费者演示，观察发布序号与消费序号的距离。再比较等待策略，不直接套论文中的特定硬件性能数字。

```text
claim next sequence
wait until slot is reusable
write event fields
publish sequence
consumer handles event and advances gating sequence
```

从稳定低负载开始增加压力，分别记录进入与完成速率。固定请求数据、连接策略和观察窗口，保留错误响应；只有成功请求的平均耗时不足以代表系统体验。

## 3. 用对照区分原因

下表列出需要主动改变的条件。预期行为来自机制分析，复现时还需记录运行环境和原始输出，不能将预期当作已经测得的结果。

| 改变的条件 | 需要验证的行为 |
| --- | --- |
| 消费者明显变慢 | 生产者最终受到可复用空间约束 |
| 处理后继续持有事件引用 | 复用时可能看到被改写内容 |
| 选择忙等待策略 | 延迟与 CPU 使用存在取舍 |

### 对照 1：消费者明显变慢

生产者最终受到可复用空间约束。观察时记录发布与消费序号的距离。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 2：处理后继续持有事件引用

复用时可能看到被改写内容。观察时记录对象生命周期与复制需求。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 3：选择忙等待策略

延迟与 CPU 使用存在取舍。观察时记录相同负载下的资源和延迟。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。

## 4. 适用条件与取舍

Disruptor 适合明确的低延迟事件管道，不代替持久消息系统。进程退出后的恢复与业务重放需要另行设计。

一次正常运行只覆盖了这组输入。继续扩展前，应把上面的异常对照保留下来，尤其关注“选择忙等待策略”这一分支。后续方案若改变了图中任意一处依赖，原来的判断就要重新验证，不能仅凭界面相似或返回值相同沿用结论。

## 同月延伸

- [高性能研究：减少对象分配之前先量化来源](/tech/2016/12/15/high-performance-memory-allocation/)
- [高并发系统研究：过载时拒绝比无限等待更可控](/tech/2016/12/25/high-concurrency-overload-design/)

## 参考资料

1. [Java 8 并发 API](https://docs.oracle.com/javase/8/docs/api/java/util/concurrent/package-summary.html)
2. [LMAX Disruptor 技术论文](https://lmax-exchange.github.io/disruptor/files/Disruptor-1.0.pdf)
