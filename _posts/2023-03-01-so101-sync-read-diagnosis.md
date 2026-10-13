---
layout: post
title: SO101 校准通信异常：从单舵机读取开始
subtitle: 校准机械臂时，网页工具能扫描六个舵机并读取位置，LeRobot 也显示 connected，可同步读取 Present_Position 却返回
  There is no status packet。
date: 2023-03-01 08:00:00 +0800
author: edyang
header-style: text
catalog: true
tags:
- 机器人
- 串口
- Python
tech_note: true
note_id: so101-sync-read-diagnosis
source_date: '2026-04-03'
source_dates:
- '2026-04-03'
published_at: '2026-10-12T12:51:43+08:00'
updated_at: '2026-10-13T17:59:15+08:00'
verification: partial
privacy_reviewed: true
permalink: /tech/2026/04/03/so101-sync-read-diagnosis/
excerpt: 校准机械臂时，网页工具能扫描六个舵机并读取位置，LeRobot 也显示 connected，可同步读取 Present_Position 却返回
  There is no status packet。
archive_date: '2023-03-01'
date_basis: simulated_weekly_archive
content_revision: 2
images:
- /img/tech-notes/so101-sync-read-diagnosis.svg
---

校准机械臂时，网页工具能扫描六个舵机并读取位置，LeRobot 也显示 connected，可同步读取 Present_Position 却返回 There is no status packet。我首先要区分端口被打开和舵机按预期协议回包这两件事。

## 研究与排查过程

研究沿着已有成功证据展开：另一工具能读到位置，说明至少那次供电和部分通信路径可用，但不能证明两套程序参数一致。排查方案先关闭其它串口工具，在同一套程序中只读取一个已知舵机，再逐步增加数量。若单读正常而同步读失败，重点就转向协议实现和回包时序。

![SO101 校准通信异常：从单舵机读取开始研究路径示意](/img/tech-notes/so101-sync-read-diagnosis.svg)

## 涉及的技术与取舍

技术上对照串口路径、波特率、ID 列表、固件与通信库版本，同时保留请求包、回包长度和超时。同步读取是否被设备支持，要由固件和实现确认；connected 通常不足以证明这一点。动作验证应在只读链路通过后进行，并采用小范围动作，避免通信异常时直接执行完整校准。

### 辅助检查示例

以下为通用示例，用于理解上述检查；变量、设备和参数需对应实际环境。

```text
connected
sync read Present_Position
There is no status packet
```

## 这轮研究的结论

这次形成了从单设备到多设备的排查路径，没有最终校准成功记录。结论是已有工具的成功值得利用，但需要逐项对照参数，不能直接推出另一程序也应成功；协议级证据比继续修改串口权限更能缩小故障范围。

## 参考资料

- [LeRobot SO101 文档](https://huggingface.co/docs/lerobot/so101)
