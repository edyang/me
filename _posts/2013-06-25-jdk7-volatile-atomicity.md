---
layout: post
title: 透彻学习 JDK：volatile 能见度不等于复合操作原子性
subtitle: 给计数器加 volatile 后，多线程累加仍可能丢失更新，因为一次自增不是一个不可分割步骤。
date: 2013-06-25 08:00:00 +0800
author: edyang
header-style: text
catalog: true
tags:
- Java
- JDK源码
tech_note: true
note_id: jdk7-volatile-atomicity
permalink: /tech/2013/06/25/jdk7-volatile-atomicity/
excerpt: 给计数器加 volatile 后，多线程累加仍可能丢失更新，因为一次自增不是一个不可分割步骤。
privacy_reviewed: true
content_revision: 3
images:
- /img/tech-notes/jdk7-volatile-atomicity.svg
technology_since: '2011-07-28'
---

给计数器加 volatile 后，多线程累加仍可能丢失更新，因为一次自增不是一个不可分割步骤。

本文使用JDK 7，示例为方法体或类定义片段。源码学习需要区分语言规则、公共接口约定与某个版本的实现。本文把讨论范围固定在 Java 7，不把后续版本的集合结构或语法写进来。

## 1. 从现象推到机制

volatile 建立相关读写的可见性与顺序约束，但 count++ 包括读取、加一和写回。两个线程读取相同旧值后，各自写回相同新值，结果就少一次。原子类或锁才能把这类更新表达成受保护操作。

![透彻学习 JDK：volatile 能见度不等于复合操作原子性的处理、反馈与观察关系](/img/tech-notes/jdk7-volatile-atomicity.svg)

图中的四个节点分别表示共享变量、读取旧值、复合更新、最终总数。顺着实线检查输入如何变成输出，再沿虚线核对反馈条件。图示表达的是本文讨论的关系，不是实测曲线或现场截图。

## 2. 最小实现与输入条件

对比普通变量、volatile 变量和 AtomicInteger。用 join 等待所有线程完成，再比较总数；不能在工作尚未结束时就判定丢失更新。

```java
AtomicInteger counter = new AtomicInteger();
// 每个工作线程重复调用：
counter.incrementAndGet();
// 所有工作线程 join 后再读取：
int total = counter.get();
```

将片段放入独立的小工程，补齐 imports（导入声明）和调用入口。观察返回值、异常类型及对象状态；并发实验需要重复交错，单次没有出错不能证明线程安全。

## 3. 用对照区分原因

下表列出需要主动改变的条件。预期行为来自机制分析，复现时还需记录运行环境和原始输出，不能将预期当作已经测得的结果。

| 改变的条件 | 需要验证的行为 |
| --- | --- |
| 多个线程更新 volatile 计数 | 仍可能小于理论总数 |
| 改用 AtomicInteger 自增 | 每次增量具有原子更新语义 |
| 只共享停止标记 | volatile 可用于可见性通知 |

### 对照 1：多个线程更新 volatile 计数

仍可能小于理论总数。观察时记录读取与写回之间的交错。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 2：改用 AtomicInteger 自增

每次增量具有原子更新语义。观察时记录线程完成后的最终总数。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 3：只共享停止标记

volatile 可用于可见性通知。观察时记录循环是否实际重新读取标记。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。

## 4. 适用条件与取舍

原子变量只保护该变量的单项操作。余额与流水等多字段一致性，需要更大的同步或事务边界，不能各放一个原子变量就认为整体正确。

一次正常运行只覆盖了这组输入。继续扩展前，应把上面的异常对照保留下来，尤其关注“只共享停止标记”这一分支。后续方案若改变了图中任意一处依赖，原来的判断就要重新验证，不能仅凭界面相似或返回值相同沿用结论。

## 同月延伸

- [透彻学习 JDK：start 与 run 的线程边界](/tech/2013/06/05/jdk7-thread-lifecycle/)
- [透彻学习 JDK：wait 为什么必须放在 while 中](/tech/2013/06/15/jdk7-monitor-wait-notify/)

## 参考资料

1. [Java SE 7 API 文档](https://docs.oracle.com/javase/7/docs/api/)
2. [Java SE 7 语言规范](https://docs.oracle.com/javase/specs/jls/se7/html/index.html)
