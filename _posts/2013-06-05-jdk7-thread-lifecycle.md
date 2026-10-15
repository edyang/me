---
layout: post
title: 透彻学习 JDK：start 与 run 的线程边界
subtitle: 直接调用 run 能得到输出，却没有创建新的执行线程。
date: 2013-06-05 08:00:00 +0800
author: edyang
header-style: text
catalog: true
tags:
- Java
- JDK源码
tech_note: true
note_id: jdk7-thread-lifecycle
permalink: /tech/2013/06/05/jdk7-thread-lifecycle/
excerpt: 直接调用 run 能得到输出，却没有创建新的执行线程。
privacy_reviewed: true
content_revision: 3
images:
- /img/tech-notes/jdk7-thread-lifecycle.svg
technology_since: '2011-07-28'
---

直接调用 run 能得到输出，却没有创建新的执行线程。线程实验要观察身份与执行顺序。

本文使用JDK 7，示例为方法体或类定义片段。源码学习需要区分语言规则、公共接口约定与某个版本的实现。本文把讨论范围固定在 Java 7，不把后续版本的集合结构或语法写进来。

## 1. 从现象推到机制

start 请求启动新的线程并由虚拟机安排执行，run 只是普通方法入口。线程不能通过重复 start 重新启动；结束后要创建新实例。sleep 暂停当前线程，但不会自动释放已持有的监视器锁。

![透彻学习 JDK：start 与 run 的线程边界的处理、反馈与观察关系](/img/tech-notes/jdk7-thread-lifecycle.svg)

图中的四个节点分别表示调用线程、线程调度、任务代码、结束等待。顺着实线检查输入如何变成输出，再沿虚线核对反馈条件。图示表达的是本文讨论的关系，不是实测曲线或现场截图。

## 2. 最小实现与输入条件

分别在主线程和工作代码中打印名称，再用 join 等待工作结束。输出先后可能变化，不能依赖某一次顺序表达业务依赖。

```java
Thread t = new Thread(new Runnable() {
    public void run() {
        System.out.println(Thread.currentThread().getName());
    }
}, "worker");
t.start();
t.join();
```

将片段放入独立的小工程，补齐 imports（导入声明）和调用入口。观察返回值、异常类型及对象状态；并发实验需要重复交错，单次没有出错不能证明线程安全。

## 3. 用对照区分原因

下表列出需要主动改变的条件。预期行为来自机制分析，复现时还需记录运行环境和原始输出，不能将预期当作已经测得的结果。

| 改变的条件 | 需要验证的行为 |
| --- | --- |
| 直接调用 run | 执行线程仍是调用方 |
| 使用 start 后 join | 调用方等待目标线程结束 |
| 再次调用同一线程的 start | 应抛线程状态异常 |

### 对照 1：直接调用 run

执行线程仍是调用方。观察时记录当前线程的名称与标识。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 2：使用 start 后 join

调用方等待目标线程结束。观察时记录join 返回时目标是否存活。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 3：再次调用同一线程的 start

应抛线程状态异常。观察时记录线程实例的启动历史。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。

## 4. 适用条件与取舍

线程生命周期与任务生命周期不是同一件事。频繁创建短任务可以交给线程池，但停止任务仍需协作式取消，不能把中断当作强制终止。

一次正常运行只覆盖了这组输入。继续扩展前，应把上面的异常对照保留下来，尤其关注“再次调用同一线程的 start”这一分支。后续方案若改变了图中任意一处依赖，原来的判断就要重新验证，不能仅凭界面相似或返回值相同沿用结论。

## 同月延伸

- [透彻学习 JDK：wait 为什么必须放在 while 中](/tech/2013/06/15/jdk7-monitor-wait-notify/)
- [透彻学习 JDK：volatile 能见度不等于复合操作原子性](/tech/2013/06/25/jdk7-volatile-atomicity/)

## 参考资料

1. [Java SE 7 API 文档](https://docs.oracle.com/javase/7/docs/api/)
2. [Java SE 7 语言规范](https://docs.oracle.com/javase/specs/jls/se7/html/index.html)
