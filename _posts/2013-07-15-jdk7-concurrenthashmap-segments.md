---
layout: post
title: 透彻学习 JDK 7：ConcurrentHashMap 的分段锁
subtitle: 并发容器不只是给整个 Map 加一把锁。
date: 2013-07-15 08:00:00 +0800
author: edyang
header-style: text
catalog: true
tags:
- Java
- JDK源码
tech_note: true
note_id: jdk7-concurrenthashmap-segments
permalink: /tech/2013/07/15/jdk7-concurrenthashmap-segments/
excerpt: 并发容器不只是给整个 Map 加一把锁。
privacy_reviewed: true
content_revision: 3
images:
- /img/tech-notes/jdk7-concurrenthashmap-segments.svg
technology_since: '2011-07-28'
---

并发容器不只是给整个 Map 加一把锁。Java 7 的分段结构提供了不同的并发访问边界。

本文使用JDK 7，示例为方法体或类定义片段。源码学习需要区分语言规则、公共接口约定与某个版本的实现。本文把讨论范围固定在 Java 7，不把后续版本的集合结构或语法写进来。

## 1. 从现象推到机制

Java 7 ConcurrentHashMap 的更新锁粒度落在分段上，不同段可以并发更新。线程安全的方法不意味着多个方法组合后仍是原子操作。先 containsKey 再 put 存在间隙，putIfAbsent 才表达条件写入。

![透彻学习 JDK 7：ConcurrentHashMap 的分段锁的处理、反馈与观察关系](/img/tech-notes/jdk7-concurrenthashmap-segments.svg)

图中的四个节点分别表示并发请求、分段容器、条件写入、对象使用。顺着实线检查输入如何变成输出，再沿虚线核对反馈条件。图示表达的是本文讨论的关系，不是实测曲线或现场截图。

## 2. 最小实现与输入条件

做一个缓存初始化例子，让多个线程同时尝试放入同一键。需要判断返回的旧值，并避免把“只有一个值写入”误认为初始化函数只运行一次。

```java
Value created = loadValue();
Value old = cache.putIfAbsent(key, created);
Value actual = old == null ? created : old;
```

将片段放入独立的小工程，补齐 imports（导入声明）和调用入口。观察返回值、异常类型及对象状态；并发实验需要重复交错，单次没有出错不能证明线程安全。

## 3. 用对照区分原因

下表列出需要主动改变的条件。预期行为来自机制分析，复现时还需记录运行环境和原始输出，不能将预期当作已经测得的结果。

| 改变的条件 | 需要验证的行为 |
| --- | --- |
| 不同线程首次写相同键 | 只有一个映射成为最终值 |
| 初始化函数有外部副作用 | 副作用可能执行多次 |
| 复合执行读取再修改 | 仍需要专门的原子协议 |

### 对照 1：不同线程首次写相同键

只有一个映射成为最终值。观察时记录putIfAbsent 返回的旧值。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 2：初始化函数有外部副作用

副作用可能执行多次。观察时记录函数调用次数与成功放入次数。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 3：复合执行读取再修改

仍需要专门的原子协议。观察时记录两次方法调用间的交错。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。

## 4. 适用条件与取舍

分段锁是该版本实现细节，不应写成所有版本都固定如此。缓存对象自身若可变，容器的线程安全也不会自动保护对象内部字段。

一次正常运行只覆盖了这组输入。继续扩展前，应把上面的异常对照保留下来，尤其关注“复合执行读取再修改”这一分支。后续方案若改变了图中任意一处依赖，原来的判断就要重新验证，不能仅凭界面相似或返回值相同沿用结论。

## 同月延伸

- [透彻学习 JDK：线程池队列满了以后怎么办](/tech/2013/07/05/jdk7-threadpool-backpressure/)
- [透彻学习 JDK：Future 超时以后任务停了吗](/tech/2013/07/25/jdk7-future-cancellation/)

## 参考资料

1. [Java SE 7 API 文档](https://docs.oracle.com/javase/7/docs/api/)
2. [Java SE 7 语言规范](https://docs.oracle.com/javase/specs/jls/se7/html/index.html)
