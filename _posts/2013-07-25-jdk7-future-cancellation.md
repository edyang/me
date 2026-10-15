---
layout: post
title: 透彻学习 JDK：Future 超时以后任务停了吗
subtitle: 等待结果超时，只说明调用方停止等待。
date: 2013-07-25 08:00:00 +0800
author: edyang
header-style: text
catalog: true
tags:
- Java
- JDK源码
tech_note: true
note_id: jdk7-future-cancellation
permalink: /tech/2013/07/25/jdk7-future-cancellation/
excerpt: 等待结果超时，只说明调用方停止等待。
privacy_reviewed: true
content_revision: 3
images:
- /img/tech-notes/jdk7-future-cancellation.svg
technology_since: '2011-07-28'
---

等待结果超时，只说明调用方停止等待。后台任务可能仍在运行，并继续占用资源。

本文使用JDK 7，示例为方法体或类定义片段。源码学习需要区分语言规则、公共接口约定与某个版本的实现。本文把讨论范围固定在 Java 7，不把后续版本的集合结构或语法写进来。

## 1. 从现象推到机制

Future.get 的超时不自动取消任务。cancel(true) 尝试中断执行线程，任务仍须检查中断或调用可中断的阻塞操作。忽略 InterruptedException 后继续循环，会让取消请求失效。

![透彻学习 JDK：Future 超时以后任务停了吗的处理、反馈与观察关系](/img/tech-notes/jdk7-future-cancellation.svg)

图中的四个节点分别表示等待结果、超时分支、取消请求、任务退出。顺着实线检查输入如何变成输出，再沿虚线核对反馈条件。图示表达的是本文讨论的关系，不是实测曲线或现场截图。

## 2. 最小实现与输入条件

在演示任务中使用可中断等待，并在捕获中断后恢复标记或结束任务。把取消返回值、线程退出和外部动作是否发生分别观察。

```java
try {
    return future.get(1, TimeUnit.SECONDS);
} catch (TimeoutException e) {
    future.cancel(true);
    throw e;
}
```

将片段放入独立的小工程，补齐 imports（导入声明）和调用入口。观察返回值、异常类型及对象状态；并发实验需要重复交错，单次没有出错不能证明线程安全。

## 3. 用对照区分原因

下表列出需要主动改变的条件。预期行为来自机制分析，复现时还需记录运行环境和原始输出，不能将预期当作已经测得的结果。

| 改变的条件 | 需要验证的行为 |
| --- | --- |
| 等待时间先到 | 调用方收到超时但任务可继续 |
| 任务响应中断 | 取消后能较快结束执行 |
| 任务已执行外部写入 | 取消无法自动撤销副作用 |

### 对照 1：等待时间先到

调用方收到超时但任务可继续。观察时记录后台任务实际结束时间。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 2：任务响应中断

取消后能较快结束执行。观察时记录中断分支是否退出循环。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 3：任务已执行外部写入

取消无法自动撤销副作用。观察时记录外部动作与取消请求的先后。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。

## 4. 适用条件与取舍

取消是协作协议，不能作为事务回滚机制。涉及外部服务的任务需要幂等标识和后续查询，避免重试时重复执行业务动作。

一次正常运行只覆盖了这组输入。继续扩展前，应把上面的异常对照保留下来，尤其关注“任务已执行外部写入”这一分支。后续方案若改变了图中任意一处依赖，原来的判断就要重新验证，不能仅凭界面相似或返回值相同沿用结论。

## 同月延伸

- [透彻学习 JDK：线程池队列满了以后怎么办](/tech/2013/07/05/jdk7-threadpool-backpressure/)
- [透彻学习 JDK 7：ConcurrentHashMap 的分段锁](/tech/2013/07/15/jdk7-concurrenthashmap-segments/)

## 参考资料

1. [Java SE 7 API 文档](https://docs.oracle.com/javase/7/docs/api/)
2. [Java SE 7 语言规范](https://docs.oracle.com/javase/specs/jls/se7/html/index.html)
