---
layout: post
title: 透彻学习 JDK：wait 为什么必须放在 while 中
subtitle: 等待通知后条件未必仍然成立。
date: 2013-06-15 08:00:00 +0800
author: edyang
header-style: text
catalog: true
tags:
- Java
- JDK源码
tech_note: true
note_id: jdk7-monitor-wait-notify
permalink: /tech/2013/06/15/jdk7-monitor-wait-notify/
excerpt: 等待通知后条件未必仍然成立。
privacy_reviewed: true
content_revision: 3
images:
- /img/tech-notes/jdk7-monitor-wait-notify.svg
technology_since: '2011-07-28'
---

等待通知后条件未必仍然成立。生产者消费者模型里，通知只是重新检查条件的机会。

本文使用JDK 7，示例为方法体或类定义片段。源码学习需要区分语言规则、公共接口约定与某个版本的实现。本文把讨论范围固定在 Java 7，不把后续版本的集合结构或语法写进来。

## 1. 从现象推到机制

wait 必须在持有对应监视器时调用，并在等待时释放该监视器。被唤醒后需要重新竞争锁，还可能经历虚假唤醒，或被其他线程先消费条件，因此用 while 重新检查共享状态。

![透彻学习 JDK：wait 为什么必须放在 while 中的处理、反馈与观察关系](/img/tech-notes/jdk7-monitor-wait-notify.svg)

图中的四个节点分别表示共享条件、等待集合、通知发生、再次检查。顺着实线检查输入如何变成输出，再沿虚线核对反馈条件。图示表达的是本文讨论的关系，不是实测曲线或现场截图。

## 2. 最小实现与输入条件

用容量为一的缓冲区表示条件，把状态检查、修改和通知放在同一锁保护内。这里只展示消费者侧，生产者也必须遵循同一协议。

```java
synchronized (lock) {
    while (slot == null) {
        lock.wait();
    }
    Object value = slot;
    slot = null;
    lock.notifyAll();
}
```

将片段放入独立的小工程，补齐 imports（导入声明）和调用入口。观察返回值、异常类型及对象状态；并发实验需要重复交错，单次没有出错不能证明线程安全。

## 3. 用对照区分原因

下表列出需要主动改变的条件。预期行为来自机制分析，复现时还需记录运行环境和原始输出，不能将预期当作已经测得的结果。

| 改变的条件 | 需要验证的行为 |
| --- | --- |
| 先启动消费者 | 条件不满足时进入等待 |
| 唤醒后被其他消费者抢先 | 继续等待而非读取空值 |
| 使用不同对象调用通知 | 无法唤醒正确等待集合 |

### 对照 1：先启动消费者

条件不满足时进入等待。观察时记录锁是否在 wait 时释放。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 2：唤醒后被其他消费者抢先

继续等待而非读取空值。观察时记录重新获得锁后的条件。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 3：使用不同对象调用通知

无法唤醒正确等待集合。观察时记录wait 与 notify 使用的监视器。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。

## 4. 适用条件与取舍

notifyAll 会唤醒等待线程参与竞争，不保证谁先获得锁。复杂队列优先考虑已有阻塞队列实现，手写协议更适合帮助理解。

一次正常运行只覆盖了这组输入。继续扩展前，应把上面的异常对照保留下来，尤其关注“使用不同对象调用通知”这一分支。后续方案若改变了图中任意一处依赖，原来的判断就要重新验证，不能仅凭界面相似或返回值相同沿用结论。

## 同月延伸

- [透彻学习 JDK：start 与 run 的线程边界](/tech/2013/06/05/jdk7-thread-lifecycle/)
- [透彻学习 JDK：volatile 能见度不等于复合操作原子性](/tech/2013/06/25/jdk7-volatile-atomicity/)

## 参考资料

1. [Java SE 7 API 文档](https://docs.oracle.com/javase/7/docs/api/)
2. [Java SE 7 语言规范](https://docs.oracle.com/javase/specs/jls/se7/html/index.html)
