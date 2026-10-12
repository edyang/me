---
layout: post
title: 机器人控制调试：先证明走一步，再连完整流程
subtitle: 接口返回 success 与机器人实际完成动作，需要分别验证。
date: 2026-10-08 08:00:00 +0800
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
published_at: '2026-10-12T12:51:43+08:00'
updated_at: '2026-10-12T12:51:43+08:00'
verification: observed
privacy_reviewed: true
permalink: /tech/2026/10/08/robot-minimal-action-validation/
excerpt: 接口返回 success 与机器人实际完成动作，需要分别验证。
---

远程 VS Code 已经连接树莓派，ROS 服务返回 success，机器人却没有移动。最有效的处理方式，是暂时缩小到一个低风险动作，从进程、串口和真实动作逐段验证。

## 服务成功不一定表示物理动作完成

success 可能仅代表请求被接收或服务调用返回。需要继续确认控制程序读到了动作、串口发送了正确协议、下位机反馈了完成，并且实际动作可见。

## 三组证据放在一起

```text
上层：请求 ID、动作名、发送与返回时间
通信：串口发送、接收及 START/COMPLETE/ERROR
现场：实际动作与是否符合预期
```

同时检查串口是否被多个进程占用。设备路径存在，也不等于控制进程使用了它。不要因为进程名看起来正确，就跳过实际通信日志。

## 最小动作成功之后再组合

原交流后来确认了单步前进，以及右转、左转和连续前进两步。这个成功范围应明确保留：它证明基础动作链可用，没有证明比赛完整流程已经完成。

下一阶段可以把流程拆成若干检查点，每段记录开始、结束、条件与失败处理。目标丢失、动作超时和重复触发都要纳入检查，避免旧坐标或旧状态驱动后续动作。

本文去掉了队伍、动作库文件名和现场路径，只保留可复用的调试顺序。
