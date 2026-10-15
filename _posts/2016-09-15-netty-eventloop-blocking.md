---
layout: post
title: Netty 研究：EventLoop 里为什么不能随便查数据库
subtitle: 一个通道处理器里执行慢查询，可能拖住同一事件循环负责的其他连接。
date: 2016-09-15 08:00:00 +0800
author: edyang
header-style: text
catalog: true
tags:
- Netty
- 网络编程
tech_note: true
note_id: netty-eventloop-blocking
permalink: /tech/2016/09/15/netty-eventloop-blocking/
excerpt: 一个通道处理器里执行慢查询，可能拖住同一事件循环负责的其他连接。
privacy_reviewed: true
content_revision: 3
images:
- /img/tech-notes/netty-eventloop-blocking.svg
technology_since: '2015-11-01'
---

一个通道处理器里执行慢查询，可能拖住同一事件循环负责的其他连接。

本文使用JDK 8 与 Netty 4.0，代码为处理器结构片段。TCP（传输控制协议）提供有序字节流，消息边界和处理线程仍由应用协议与框架约定。网络读到数据与业务处理完成需要分别观察。

## 1. 从现象推到机制

EventLoop（事件循环）负责多个通道的事件处理，阻塞操作会占用这条线程。业务工作移到其他执行器后，还要处理结果回传、消息顺序与资源释放。异步化不是把任务丢进无界队列。

![Netty 研究：EventLoop 里为什么不能随便查数据库的处理、反馈与观察关系](/img/tech-notes/netty-eventloop-blocking.svg)

图中的四个节点分别表示网络事件、业务提交、工作线程、结果回传。顺着实线检查输入如何变成输出，再沿虚线核对反馈条件。图示表达的是本文讨论的关系，不是实测曲线或现场截图。

## 2. 最小实现与输入条件

演示中把耗时工作交给有界执行器，回写通过明确的通道上下文完成。记录事件循环延迟与工作队列长度，检查连接关闭后的结果处理。

```text
channel read -> decode
submit bounded business task
worker -> compute result
channel context -> write response
closed channel -> discard or compensate by contract
```

使用本机客户端和服务端发送演示字节，记录每次读取长度与解码结果。固定 Netty 版本，补齐 pipeline 配置，资源释放责任必须跟随具体处理器类型判断。

## 3. 用对照区分原因

下表列出需要主动改变的条件。预期行为来自机制分析，复现时还需记录运行环境和原始输出，不能将预期当作已经测得的结果。

| 改变的条件 | 需要验证的行为 |
| --- | --- |
| 处理器中同步等待慢查询 | 其他连接事件也可能延迟 |
| 转移到无界业务队列 | 可能把压力变成内存和排队 |
| 连接先于业务完成关闭 | 结果不能无条件继续写回 |

### 对照 1：处理器中同步等待慢查询

其他连接事件也可能延迟。观察时记录同一事件循环的任务时间。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 2：转移到无界业务队列

可能把压力变成内存和排队。观察时记录队列增长与拒绝策略。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 3：连接先于业务完成关闭

结果不能无条件继续写回。观察时记录通道状态与任务归属。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。

## 4. 适用条件与取舍

跨线程后要显式定义每个对象的可变性与归属。连接内消息是否允许并行，取决于协议顺序要求，不能只追求线程数。

一次正常运行只覆盖了这组输入。继续扩展前，应把上面的异常对照保留下来，尤其关注“连接先于业务完成关闭”这一分支。后续方案若改变了图中任意一处依赖，原来的判断就要重新验证，不能仅凭界面相似或返回值相同沿用结论。

## 同月延伸

- [Netty 研究：粘包拆包其实是消息边界问题](/tech/2016/09/05/netty-tcp-frame-decoder/)
- [Netty 研究：ByteBuf 的引用计数与跨线程传递](/tech/2016/09/25/netty-bytebuf-reference-count/)

## 参考资料

1. [Netty 4.0 用户指南](https://netty.io/wiki/user-guide-for-4.x.html)
2. [Netty 4.0.32 源码](https://github.com/netty/netty/tree/netty-4.0.32.Final)
