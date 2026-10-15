---
layout: post
title: 车联网学习：CAN 仲裁、帧与物理层先分清
subtitle: 接上两根线看到报文，只是研究开始。
date: 2017-11-05 08:00:00 +0800
author: edyang
header-style: text
catalog: true
tags:
- 车联网
- CAN总线
tech_note: true
note_id: canbus-arbitration-physical-layer
permalink: /tech/2017/11/05/canbus-arbitration-physical-layer/
excerpt: 接上两根线看到报文，只是研究开始。
privacy_reviewed: true
content_revision: 3
images:
- /img/tech-notes/canbus-arbitration-physical-layer.svg
technology_since: '2013-01-01'
---

接上两根线看到报文，只是研究开始。总线类型、波特率与终端匹配决定接入是否合理。

本文使用Linux SocketCAN、can-utils 与隔离台架或 vcan 虚拟总线。CAN（控制器局域网）定义传输与仲裁，不提供通用的车型信号字典。大众尚酷的具体网段、信号位和校验方式必须靠对应资料与验证，本文不把演示标识符当成实车控制报文。

## 1. 从现象推到机制

经典 CAN 通过标识符参与仲裁，标识符本身不直接等于某个设备地址。数据字段需要上层协议定义，同一标识符在不同车型网段也可能有不同含义。控制器和收发器属于不同层次，电气接入不能靠软件猜测。

![车联网学习：CAN 仲裁、帧与物理层先分清的处理、反馈与观察关系](/img/tech-notes/canbus-arbitration-physical-layer.svg)

图中的四个节点分别表示业务信号、CAN 帧、控制器收发器、总线条件。顺着实线检查输入如何变成输出，再沿虚线核对反馈条件。图示表达的是本文讨论的关系，不是实测曲线或现场截图。

## 2. 最小实现与输入条件

先阅读适配器和目标网段资料，离线研究帧结构。台架断电测量与布线需按硬件手册进行，不在未知带电接口上试接。

```text
application signal -> payload definition
CAN controller -> frame and arbitration
transceiver -> electrical bus interface
physical network -> wiring, bitrate, termination
```

默认先分析离线日志或使用 vcan。真实总线观测需确认适配器处于正确只听模式与电气接入条件；主动发送只在独立台架、已确认协议与可停止条件下讨论，不在行驶车辆试错。

## 3. 用对照区分原因

下表列出需要主动改变的条件。预期行为来自机制分析，复现时还需记录运行环境和原始输出，不能将预期当作已经测得的结果。

| 改变的条件 | 需要验证的行为 |
| --- | --- |
| 相同标识符出现在不同车型 | 不能自动解释为同一信号 |
| 软件接口已启动 | 不代表电气与波特率正确 |
| 只看到数据字节变化 | 还不能推断控制用途 |

### 对照 1：相同标识符出现在不同车型

不能自动解释为同一信号。观察时记录车型版本与网段资料。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 2：软件接口已启动

不代表电气与波特率正确。观察时记录实际接收错误和硬件条件。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 3：只看到数据字节变化

还不能推断控制用途。观察时记录动作对照与协议证据。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。

## 4. 适用条件与取舍

标准只定义部分通信机制，不包含大众尚酷全部信号字典。未知内容应保持待验证，不能用其他车辆的例子补成事实。

一次正常运行只覆盖了这组输入。继续扩展前，应把上面的异常对照保留下来，尤其关注“只看到数据字节变化”这一分支。后续方案若改变了图中任意一处依赖，原来的判断就要重新验证，不能仅凭界面相似或返回值相同沿用结论。

## 同月延伸

- [车联网学习：先用 SocketCAN 建立可重复的只读记录](/tech/2017/11/15/socketcan-listen-capture/)
- [大众尚酷 CAN 研究：怎样筛选左右灯候选信号](/tech/2017/11/25/scirocco-can-signal-candidates/)

## 参考资料

1. [Linux SocketCAN 文档](https://www.kernel.org/doc/Documentation/networking/can.txt)
2. [linux-can/can-utils](https://github.com/linux-can/can-utils)
