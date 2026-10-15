---
layout: post
title: Netty 研究：粘包拆包其实是消息边界问题
subtitle: 一次 write 不对应一次 read。
date: 2016-09-05 08:00:00 +0800
author: edyang
header-style: text
catalog: true
tags:
- Netty
- 网络编程
tech_note: true
note_id: netty-tcp-frame-decoder
permalink: /tech/2016/09/05/netty-tcp-frame-decoder/
excerpt: 一次 write 不对应一次 read。
privacy_reviewed: true
content_revision: 3
images:
- /img/tech-notes/netty-tcp-frame-decoder.svg
technology_since: '2015-11-01'
---

一次 write 不对应一次 read。TCP 接收端看到的是字节流，需要协议自己定义消息边界。

本文使用JDK 8 与 Netty 4.0，代码为处理器结构片段。TCP（传输控制协议）提供有序字节流，消息边界和处理线程仍由应用协议与框架约定。网络读到数据与业务处理完成需要分别观察。

## 1. 从现象推到机制

消息可能被拆成多次读取，也可能多条一起到达。固定长度、分隔符与长度字段是不同编码方式。长度字段协议需要校验最大帧长，避免不可信长度触发大量分配或无限等待。

![Netty 研究：粘包拆包其实是消息边界问题的处理、反馈与观察关系](/img/tech-notes/netty-tcp-frame-decoder.svg)

图中的四个节点分别表示TCP 字节流、长度判断、累计解码、业务消息。顺着实线检查输入如何变成输出，再沿虚线核对反馈条件。图示表达的是本文讨论的关系，不是实测曲线或现场截图。

## 2. 最小实现与输入条件

用长度前缀加正文的演示协议，把同一消息分两段发送，再一次发送两条。解码器先检查可读字节，不足时保留状态等待。

```text
frame = length(4 bytes) + payload
if readable < 4: wait
read length and validate upper bound
if readable payload insufficient: restore reader index and wait
else emit exactly one message
```

使用本机客户端和服务端发送演示字节，记录每次读取长度与解码结果。固定 Netty 版本，补齐 pipeline 配置，资源释放责任必须跟随具体处理器类型判断。

## 3. 用对照区分原因

下表列出需要主动改变的条件。预期行为来自机制分析，复现时还需记录运行环境和原始输出，不能将预期当作已经测得的结果。

| 改变的条件 | 需要验证的行为 |
| --- | --- |
| 一条消息分多次到达 | 解码器等待完整帧再输出 |
| 多条消息同批到达 | 应逐条解出而非拼成一条 |
| 长度字段异常巨大 | 应尽早拒绝超限帧 |

### 对照 1：一条消息分多次到达

解码器等待完整帧再输出。观察时记录累计可读字节与 reader index。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 2：多条消息同批到达

应逐条解出而非拼成一条。观察时记录帧长和输出消息数量。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 3：长度字段异常巨大

应尽早拒绝超限帧。观察时记录最大帧长与实际内存申请。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。

## 4. 适用条件与取舍

消息边界正确之后还需处理字符编码、版本与业务校验。不要把解码成功当成对端身份可信。

一次正常运行只覆盖了这组输入。继续扩展前，应把上面的异常对照保留下来，尤其关注“长度字段异常巨大”这一分支。后续方案若改变了图中任意一处依赖，原来的判断就要重新验证，不能仅凭界面相似或返回值相同沿用结论。

## 同月延伸

- [Netty 研究：EventLoop 里为什么不能随便查数据库](/tech/2016/09/15/netty-eventloop-blocking/)
- [Netty 研究：ByteBuf 的引用计数与跨线程传递](/tech/2016/09/25/netty-bytebuf-reference-count/)

## 参考资料

1. [Netty 4.0 用户指南](https://netty.io/wiki/user-guide-for-4.x.html)
2. [Netty 4.0.32 源码](https://github.com/netty/netty/tree/netty-4.0.32.Final)
