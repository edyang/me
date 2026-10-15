---
layout: post
title: 大众尚酷 CAN 研究：怎样筛选左右灯候选信号
subtitle: 某个字节与转向灯同时变化，只能成为候选证据，不能直接认定它就是控制位。
date: 2017-11-25 08:00:00 +0800
author: edyang
header-style: text
catalog: true
tags:
- 车联网
- CAN总线
tech_note: true
note_id: scirocco-can-signal-candidates
permalink: /tech/2017/11/25/scirocco-can-signal-candidates/
excerpt: 某个字节与转向灯同时变化，只能成为候选证据，不能直接认定它就是控制位。
privacy_reviewed: true
content_revision: 3
images:
- /img/tech-notes/scirocco-can-signal-candidates.svg
technology_since: '2013-01-01'
---

某个字节与转向灯同时变化，只能成为候选证据，不能直接认定它就是控制位。

本文使用Linux SocketCAN、can-utils 与隔离台架或 vcan 虚拟总线。CAN（控制器局域网）定义传输与仲裁，不提供通用的车型信号字典。大众尚酷的具体网段、信号位和校验方式必须靠对应资料与验证，本文不把演示标识符当成实车控制报文。

## 1. 从现象推到机制

车灯操作可能带来开关输入、状态广播、仪表反馈与网关转发等多种变化。需要固定车辆条件，多次执行关闭、左侧、关闭、右侧的对照，检查周期、位变化与其他动作的混杂。计数器与校验字段也会变化。

![大众尚酷 CAN 研究：怎样筛选左右灯候选信号的处理、反馈与观察关系](/img/tech-notes/scirocco-can-signal-candidates.svg)

图中的四个节点分别表示动作对照、候选变化、混杂排除、信号解释。顺着实线检查输入如何变成输出，再沿虚线核对反馈条件。图示表达的是本文讨论的关系，不是实测曲线或现场截图。

## 2. 最小实现与输入条件

在离线日志中按标识符、长度和时间分组，计算候选位变化。把原始观测与信号解释分列，不填写未经确认的真实标识符。

```text
condition -> OFF / LEFT / OFF / RIGHT
observation -> id, dlc, timestamp, changed_bits
interpretation -> candidate input/status/control
confidence -> repeated evidence and unresolved confounders
```

默认先分析离线日志或使用 vcan。真实总线观测需确认适配器处于正确只听模式与电气接入条件；主动发送只在独立台架、已确认协议与可停止条件下讨论，不在行驶车辆试错。

## 3. 用对照区分原因

下表列出需要主动改变的条件。预期行为来自机制分析，复现时还需记录运行环境和原始输出，不能将预期当作已经测得的结果。

| 改变的条件 | 需要验证的行为 |
| --- | --- |
| 每次左侧动作候选位变化 | 仍需排除周期计数与其他事件 |
| 无动作时该位也变化 | 可能并非灯光状态位 |
| 候选帧来自另一网段 | 还要解释网关与信号方向 |

### 对照 1：每次左侧动作候选位变化

仍需排除周期计数与其他事件。观察时记录多次独立重复的时间对齐。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 2：无动作时该位也变化

可能并非灯光状态位。观察时记录静止基线日志。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 3：候选帧来自另一网段

还要解释网关与信号方向。观察时记录接入位置和网络拓扑。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。

## 4. 适用条件与取舍

本篇不声称已经找到尚酷左右灯控制报文。最终需要对应车型资料、方向验证和隔离台架证据，不能把相关性当成控制权限。

一次正常运行只覆盖了这组输入。继续扩展前，应把上面的异常对照保留下来，尤其关注“候选帧来自另一网段”这一分支。后续方案若改变了图中任意一处依赖，原来的判断就要重新验证，不能仅凭界面相似或返回值相同沿用结论。

## 同月延伸

- [车联网学习：CAN 仲裁、帧与物理层先分清](/tech/2017/11/05/canbus-arbitration-physical-layer/)
- [车联网学习：先用 SocketCAN 建立可重复的只读记录](/tech/2017/11/15/socketcan-listen-capture/)

## 参考资料

1. [Linux SocketCAN 文档](https://www.kernel.org/doc/Documentation/networking/can.txt)
2. [linux-can/can-utils](https://github.com/linux-can/can-utils)
