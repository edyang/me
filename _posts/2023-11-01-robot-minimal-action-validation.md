---
layout: post
title: ROS 机器人控制：从最小动作到串口反馈
subtitle: 远程 VS Code 已连接树莓派，ROS 服务返回 success，机器人却不一定移动。
date: 2023-11-01 08:00:00 +0800
author: edyang
header-style: text
catalog: true
tags:
- 机器人
- 串口
- ROS
tech_note: true
note_id: robot-minimal-action-validation
source_date: '2026-10-08'
source_dates:
- '2026-10-08'
- '2026-10-09'
- '2026-10-10'
- '2026-10-11'
published_at: '2026-10-12T12:51:43+08:00'
updated_at: '2026-10-13T17:59:15+08:00'
verification: partial
privacy_reviewed: true
permalink: /tech/2026/10/08/robot-minimal-action-validation/
excerpt: 远程 VS Code 已连接树莓派，ROS 服务返回 success，机器人却不一定移动。
archive_date: '2023-11-01'
date_basis: simulated_weekly_archive
content_revision: 2
images:
- /img/tech-notes/robot-minimal-action-validation.svg
---

远程 VS Code 已连接树莓派，ROS 服务返回 success，机器人却不一定移动。我希望从一个简单动作重建调试路径，再组合转向与抓取，避免完整流程里同时排查太多变量。

## 研究与排查过程

最初将上层请求、控制进程、串口发送和真实动作放在同一条证据链上。早期记录确认单步、转向与两步前进可用。后续近距离抓取也有成功反馈，但较远位置自动抓取未完成；目标丢失还曾引发重复后退。另一次前进测试收到下位机 START，却没有 COMPLETE，不能被以前的成功覆盖。

![ROS 机器人控制：从最小动作到串口反馈研究路径示意](/img/tech-notes/robot-minimal-action-validation.svg)

## 涉及的技术与取舍

技术检查包括 ROS 服务回执、串口进程占用、发送与接收时间、START/COMPLETE/ERROR 及动作状态机。success 的含义由接口实现决定，可能只表示接收请求。控制流程应分别记录触发、等待、完成与退出，不把视觉目标丢失当作抓取成功。串口检查先做只读观察和小动作，保留受控机械边界。

### 辅助检查示例

以下为通用示例，用于理解上述检查；变量、设备和参数需对应实际环境。

```text
上层：请求 ID、动作名、发送与返回时间
通信：串口发送、接收及 START/COMPLETE/ERROR
现场：实际动作与是否符合预期
```

## 这轮研究的结论

结论是每轮、每动作都独立记录成功范围，完整流程要靠分段完成证据推进。现有记录支持基础动作与近距离抓取可用，后来前进异常和自动流程仍未确认解决。本篇不公开动作库、坐标和阈值，分享的是如何把软件回执与实际执行对应起来。
