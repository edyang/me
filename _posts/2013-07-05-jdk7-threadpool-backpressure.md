---
layout: post
title: 透彻学习 JDK：线程池队列满了以后怎么办
subtitle: 线程池限制线程数量，却可能把压力转移到任务队列。
date: 2013-07-05 08:00:00 +0800
author: edyang
header-style: text
catalog: true
tags:
- Java
- JDK源码
tech_note: true
note_id: jdk7-threadpool-backpressure
permalink: /tech/2013/07/05/jdk7-threadpool-backpressure/
excerpt: 线程池限制线程数量，却可能把压力转移到任务队列。
privacy_reviewed: true
content_revision: 3
images:
- /img/tech-notes/jdk7-threadpool-backpressure.svg
technology_since: '2011-07-28'
---

线程池限制线程数量，却可能把压力转移到任务队列。没有队列边界时，内存也会成为排队资源。

本文使用JDK 7，示例为方法体或类定义片段。源码学习需要区分语言规则、公共接口约定与某个版本的实现。本文把讨论范围固定在 Java 7，不把后续版本的集合结构或语法写进来。

## 1. 从现象推到机制

ThreadPoolExecutor 的任务接纳涉及核心线程、队列、最大线程数和拒绝策略。队列未满时不一定继续增加到最大线程数；无界队列会让最大值对普通扩容几乎不起作用。拒绝必须成为调用方可处理的结果。

![透彻学习 JDK：线程池队列满了以后怎么办的处理、反馈与观察关系](/img/tech-notes/jdk7-threadpool-backpressure.svg)

图中的四个节点分别表示任务提交、有界队列、工作线程、拒绝反馈。顺着实线检查输入如何变成输出，再沿虚线核对反馈条件。图示表达的是本文讨论的关系，不是实测曲线或现场截图。

## 2. 最小实现与输入条件

使用有界队列和明确拒绝策略，任务里用短等待模拟慢依赖。观察提交延迟、队列长度和拒绝次数，示例参数仅用于小规模实验。

```java
ThreadPoolExecutor pool = new ThreadPoolExecutor(
    2, 4, 30, TimeUnit.SECONDS,
    new ArrayBlockingQueue<Runnable>(8),
    new ThreadPoolExecutor.AbortPolicy());
```

将片段放入独立的小工程，补齐 imports（导入声明）和调用入口。观察返回值、异常类型及对象状态；并发实验需要重复交错，单次没有出错不能证明线程安全。

## 3. 用对照区分原因

下表列出需要主动改变的条件。预期行为来自机制分析，复现时还需记录运行环境和原始输出，不能将预期当作已经测得的结果。

| 改变的条件 | 需要验证的行为 |
| --- | --- |
| 提交速度低于处理速度 | 队列不应持续增长 |
| 持续超量提交 | 最终触发拒绝策略 |
| 慢依赖长期阻塞 | 工作线程可能全部占满 |

### 对照 1：提交速度低于处理速度

队列不应持续增长。观察时记录活动线程数与队列长度。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 2：持续超量提交

最终触发拒绝策略。观察时记录拒绝发生时的队列容量。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 3：慢依赖长期阻塞

工作线程可能全部占满。观察时记录任务执行栈与依赖等待时间。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。

## 4. 适用条件与取舍

CallerRunsPolicy 会把工作转给提交线程，可能形成背压，也可能拖住请求线程。选择策略要按业务容忍度决定，不能为了不报错而静默丢任务。

一次正常运行只覆盖了这组输入。继续扩展前，应把上面的异常对照保留下来，尤其关注“慢依赖长期阻塞”这一分支。后续方案若改变了图中任意一处依赖，原来的判断就要重新验证，不能仅凭界面相似或返回值相同沿用结论。

## 同月延伸

- [透彻学习 JDK 7：ConcurrentHashMap 的分段锁](/tech/2013/07/15/jdk7-concurrenthashmap-segments/)
- [透彻学习 JDK：Future 超时以后任务停了吗](/tech/2013/07/25/jdk7-future-cancellation/)

## 参考资料

1. [Java SE 7 API 文档](https://docs.oracle.com/javase/7/docs/api/)
2. [Java SE 7 语言规范](https://docs.oracle.com/javase/specs/jls/se7/html/index.html)
