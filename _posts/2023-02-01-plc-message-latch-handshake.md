---
layout: post
title: PLC 与视觉系统握手：排查完成信号丢失
subtitle: 我在梳理机械动作与视觉结果的衔接时，关注到一个很典型的问题：视觉侧已经返回完成消息，PLC 仍停在等待步骤；另一种情况则是上一轮的完成消息让下一轮提前继续。
date: 2023-02-01 08:00:00 +0800
author: edyang
header-style: text
catalog: true
tags:
- PLC
- 工业通信
tech_note: true
note_id: plc-message-latch-handshake
source_date: '2026-03-30'
source_dates:
- '2026-03-30'
published_at: '2026-10-12T12:51:43+08:00'
updated_at: '2026-10-13T17:59:15+08:00'
verification: notes
privacy_reviewed: true
permalink: /tech/2026/03/30/plc-message-latch-handshake/
excerpt: 我在梳理机械动作与视觉结果的衔接时，关注到一个很典型的问题：视觉侧已经返回完成消息，PLC 仍停在等待步骤；另一种情况则是上一轮的完成消息让下一轮提前继续。
archive_date: '2023-02-01'
date_basis: simulated_weekly_archive
content_revision: 2
images:
- /img/tech-notes/plc-message-latch-handshake.svg
---

我在梳理机械动作与视觉结果的衔接时，关注到一个很典型的问题：视觉侧已经返回完成消息，PLC 仍停在等待步骤；另一种情况则是上一轮的完成消息让下一轮提前继续。要解决它，需要先搞清楚消息何时到达，又何时被程序使用。

## 研究与排查过程

讨论从 PLC 扫描周期展开。接收程序和工序状态机并不一定在同一时刻处理同一个值，如果消息先到、等待步骤后到，中间又覆盖了寄存器，就可能错过结果。反过来，消费后不清理标志，旧结果会继续满足下一轮条件。因此排查方案是对照请求、接收、进入等待和消费四个时间点，而不是只看一个完成位。

![PLC 与视觉系统握手：排查完成信号丢失研究路径示意](/img/tech-notes/plc-message-latch-handshake.svg)

## 涉及的技术与取舍

技术方案采用有效消息锁存、任务序号和明确的状态转换。接收区负责保存消息，状态机核对任务归属后再消费；完成、忙碌和故障分别表示，消费后发确认并清理待处理状态。序号用于排除旧任务回执，超时用于结束异常等待，重复消息则通过已消费记录处理。这里公开的是通用设计，不涉及现场寄存器或控制节拍。

### 辅助检查示例

以下为通用示例，用于理解上述检查；变量、设备和参数需对应实际环境。

```text
请求：task_id、command
响应：task_id、state、result
消费条件：task_id 与当前任务一致，state 为完成
消费后：记录结果，清除待处理标志，发送确认
```

## 这轮研究的结论

这轮形成的结论是：跨系统握手要管理消息生命周期，单个瞬时完成码无法表达全部状态。记录支持了漏信号的分析方向，但没有完整的现场回归结果。下一次验证应同时覆盖正常周期、提前回执、重复回执、断线和超时，不能只测一次成功动作。
