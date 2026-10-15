---
layout: post
title: Arduino 串口：先定义一条命令怎样结束
subtitle: 串口读到一两个字节就解析，可能把半条命令当完整消息。
date: 2018-05-25 08:00:00 +0800
author: edyang
header-style: text
catalog: true
tags:
- Arduino
- 嵌入式
tech_note: true
note_id: arduino-serial-command-framing
permalink: /tech/2018/05/25/arduino-serial-command-framing/
excerpt: 串口读到一两个字节就解析，可能把半条命令当完整消息。
privacy_reviewed: true
content_revision: 3
images:
- /img/tech-notes/arduino-serial-command-framing.svg
technology_since: '2017-09-28'
---

串口读到一两个字节就解析，可能把半条命令当完整消息。边界与长度需要写进协议。

本文使用Arduino IDE 1.8.5、Uno 级演示板与该版本配套核心库。Arduino（开源微控制器平台）简化编译和烧录，仍需要理解循环、计时与硬件状态。不同板卡的电压、编号和库支持不能互相默认兼容。

## 1. 从现象推到机制

串口也是字节流，分隔符或长度字段决定帧结束。缓冲区必须有上限，接收超时后丢弃半帧并恢复。文本协议还需要校验参数数量和范围，不能直接把任意字符串转换成电机或继电器动作。

![Arduino 串口：先定义一条命令怎样结束的处理、反馈与观察关系](/img/tech-notes/arduino-serial-command-framing.svg)

图中的四个节点分别表示字节接收、有限缓冲、完整解析、状态回复。顺着实线检查输入如何变成输出，再沿虚线核对反馈条件。图示表达的是本文讨论的关系，不是实测曲线或现场截图。

## 2. 最小实现与输入条件

用换行结束的合成命令演示，先控制板载灯。解析成功后再执行，错误只返回说明，不保留半更新状态。

```text
frame: LED,ON\n
receive byte -> bounded buffer
newline -> validate whole command
valid -> update demo LED and reply state
invalid or timeout -> clear partial frame
```

从串口输出和板载灯开始，外部电路先确认限流与供电。示例避免市电负载；库版本、板卡选项与编译输出需要一起保留，方便换电脑后复现。

## 3. 用对照区分原因

下表列出需要主动改变的条件。预期行为来自机制分析，复现时还需记录运行环境和原始输出，不能将预期当作已经测得的结果。

| 改变的条件 | 需要验证的行为 |
| --- | --- |
| 命令分两次到达 | 接收端应等待完整帧 |
| 输入超过最大长度 | 应拒绝并恢复接收边界 |
| 参数不在白名单 | 不能继续猜测执行动作 |

### 对照 1：命令分两次到达

接收端应等待完整帧。观察时记录缓冲区状态与结束符。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 2：输入超过最大长度

应拒绝并恢复接收边界。观察时记录容量检查和清理动作。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 3：参数不在白名单

不能继续猜测执行动作。观察时记录解析结果与允许值集合。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。

## 4. 适用条件与取舍

串口回复也要区分已接收、已执行和实际反馈。对于有机械风险的负载，还需要独立停止与硬件保护。

一次正常运行只覆盖了这组输入。继续扩展前，应把上面的异常对照保留下来，尤其关注“参数不在白名单”这一分支。后续方案若改变了图中任意一处依赖，原来的判断就要重新验证，不能仅凭界面相似或返回值相同沿用结论。

## 同月延伸

- [Arduino 环境：板卡核心与库版本怎样共同影响编译](/tech/2018/05/05/arduino18-board-library-version/)
- [Arduino 编程：用 millis 替代长时间 delay](/tech/2018/05/15/arduino-millis-nonblocking/)

## 参考资料

1. [Arduino IDE 1.8.5 历史源码](https://github.com/arduino/Arduino/tree/1.8.5)
2. [Arduino 内置示例](https://docs.arduino.cc/built-in-examples/)
