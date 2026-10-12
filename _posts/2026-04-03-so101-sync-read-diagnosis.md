---
layout: post
title: SO101 校准报 No status packet：连接成功后还要检查协议层
subtitle: 网页工具能读到舵机，LeRobot 却同步读取失败。这说明排查需要从连接层继续向协议和时序推进。
date: 2026-04-03 08:00:00 +0800
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
updated_at: '2026-10-12T12:51:43+08:00'
verification: partial
privacy_reviewed: true
permalink: /tech/2026/04/03/so101-sync-read-diagnosis/
excerpt: 网页工具能读到舵机，LeRobot 却同步读取失败。这说明排查需要从连接层继续向协议和时序推进。
---

校准机械臂时，网页工具能扫描到六个舵机并读取位置，LeRobot 也显示设备已连接，但读取 `Present_Position` 时出现 `There is no status packet`。这种情况不能直接归为“串口没有权限”。

## 已经知道什么

已有工具成功读取位置，说明至少在那一次操作中，端口、供电和部分通信路径可以工作。它不能保证另一套程序使用了相同的波特率、舵机 ID、读包方式或时序。

```text
connected
sync read Present_Position
There is no status packet
```

## 用单舵机读取缩小问题范围

关闭其它串口工具，先确认没有进程占用端口。随后在同一程序里只读一个已知 ID，再逐步增加设备数量。如果单读可用、同步读失败，应重点检查同步读取实现、固件支持、返回时序和重试策略，而不是继续改操作系统权限。

把两套工具使用的端口、波特率、ID 列表、库版本和读包方法并排记录。采集发送包、回包长度和超时日志，比仅看“connected”更能说明问题。连接提示通常只是端口已打开，并不代表动作协议已通过。

## 校准前保留机械安全边界

先做只读测试，再进行低速、小范围的校准动作。避免用大动作判断通信是否正常。供电、机械限位和急停应当先确认，校准过程中也要避免多程序同时发指令。

历史记录没有最终校准成功的反馈。当前可复用的结论是：基础通信可用并没有排除同步读协议或时序问题。

## 参考资料

- [LeRobot SO101 文档](https://huggingface.co/docs/lerobot/so101)
