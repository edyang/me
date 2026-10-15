---
layout: post
title: Netty 研究：ByteBuf 的引用计数与跨线程传递
subtitle: 内存增长不一定出现在 Java 堆里。
date: 2016-09-25 08:00:00 +0800
author: edyang
header-style: text
catalog: true
tags:
- Netty
- 网络编程
tech_note: true
note_id: netty-bytebuf-reference-count
permalink: /tech/2016/09/25/netty-bytebuf-reference-count/
excerpt: 内存增长不一定出现在 Java 堆里。
privacy_reviewed: true
content_revision: 3
images:
- /img/tech-notes/netty-bytebuf-reference-count.svg
technology_since: '2015-11-01'
---

内存增长不一定出现在 Java 堆里。使用直接缓冲区时，引用计数释放责任尤其重要。

本文使用JDK 8 与 Netty 4.0，代码为处理器结构片段。TCP（传输控制协议）提供有序字节流，消息边界和处理线程仍由应用协议与框架约定。网络读到数据与业务处理完成需要分别观察。

## 1. 从现象推到机制

ByteBuf（字节缓冲区）的引用计数决定何时释放底层资源。部分处理器会自动释放入站消息，跨线程保留时需要按具体路径 retain，并在最终使用后 release。重复释放和忘记释放都属于生命周期错误。

![Netty 研究：ByteBuf 的引用计数与跨线程传递的处理、反馈与观察关系](/img/tech-notes/netty-bytebuf-reference-count.svg)

图中的四个节点分别表示入站缓冲、跨线程保留、业务完成、内存观察。顺着实线检查输入如何变成输出，再沿虚线核对反馈条件。图示表达的是本文讨论的关系，不是实测曲线或现场截图。

## 2. 最小实现与输入条件

先画消息从读取、解码到业务执行的所有权路径。根据处理器基类判断是否自动释放，不机械地在每个方法末尾再 release 一次。

```java
ByteBuf saved = input.retain();
executor.execute(() -> {
  try {
    consume(saved);
  } finally {
    saved.release();
  }
});
// 还需处理任务提交被拒绝的释放路径
```

使用本机客户端和服务端发送演示字节，记录每次读取长度与解码结果。固定 Netty 版本，补齐 pipeline 配置，资源释放责任必须跟随具体处理器类型判断。

## 3. 用对照区分原因

下表列出需要主动改变的条件。预期行为来自机制分析，复现时还需记录运行环境和原始输出，不能将预期当作已经测得的结果。

| 改变的条件 | 需要验证的行为 |
| --- | --- |
| 入站处理器自动释放 | 异步使用前需要保留有效引用 |
| 工作任务被拒绝 | 预先保留的引用也必须释放 |
| 同一引用重复释放 | 可能访问已释放资源或抛错 |

### 对照 1：入站处理器自动释放

异步使用前需要保留有效引用。观察时记录处理器类型与当前引用计数。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 2：工作任务被拒绝

预先保留的引用也必须释放。观察时记录提交失败分支。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 3：同一引用重复释放

可能访问已释放资源或抛错。观察时记录每条路径的取得与释放次数。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。

## 4. 适用条件与取舍

示例缺省的外层所有权需要在真实 pipeline 中明确。堆使用正常不能排除直接内存泄漏，应结合泄漏检测与资源指标。

一次正常运行只覆盖了这组输入。继续扩展前，应把上面的异常对照保留下来，尤其关注“同一引用重复释放”这一分支。后续方案若改变了图中任意一处依赖，原来的判断就要重新验证，不能仅凭界面相似或返回值相同沿用结论。

## 同月延伸

- [Netty 研究：粘包拆包其实是消息边界问题](/tech/2016/09/05/netty-tcp-frame-decoder/)
- [Netty 研究：EventLoop 里为什么不能随便查数据库](/tech/2016/09/15/netty-eventloop-blocking/)

## 参考资料

1. [Netty 4.0 用户指南](https://netty.io/wiki/user-guide-for-4.x.html)
2. [Netty 4.0.32 源码](https://github.com/netty/netty/tree/netty-4.0.32.Final)
