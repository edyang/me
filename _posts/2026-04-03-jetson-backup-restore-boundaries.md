---
layout: post
title: Jetson 备份：先分清文件备份、rootfs 克隆和整机恢复
subtitle: 恢复目标不同，备份范围也不同。镜像文件存在并不等于现场设备能够恢复。
date: 2026-04-03 08:00:00 +0800
author: edyang
header-style: text
catalog: true
tags:
- Jetson
- 运维
tech_note: true
note_id: jetson-backup-restore-boundaries
source_date: '2026-04-03'
source_dates:
- '2026-04-03'
published_at: '2026-10-12T12:51:43+08:00'
updated_at: '2026-10-12T12:51:43+08:00'
verification: proposal
privacy_reviewed: true
permalink: /tech/2026/04/03/jetson-backup-restore-boundaries/
excerpt: 恢复目标不同，备份范围也不同。镜像文件存在并不等于现场设备能够恢复。
---

边缘设备装好驱动、模型和服务以后，重新搭一遍环境往往比刷系统更费时间。我讨论过用另一台 Linux 主机备份 Jetson，希望以后能较快恢复。第一步应当把“恢复到什么程度”写清楚。

## 三种备份不能相互替代

文件备份保存代码、配置、数据和依赖清单；rootfs 克隆保存系统分区内容；板级备份恢复工具还涉及启动相关分区。设备的系统盘可能在 eMMC、NVMe 或其它介质上，必须分别确认覆盖范围。

| 恢复目标 | 应保存的内容 |
| --- | --- |
| 重新部署应用 | 代码、容器版本、配置、模型与数据 |
| 恢复原系统环境 | 系统分区镜像、分区信息与匹配的 BSP |
| 恢复可启动设备 | 板级配置、启动分区、外置盘与应用资产 |

## 版本与硬件信息要跟镜像放在一起

至少记录 JetPack/L4T 版本、模块和载板型号、系统盘设备、分区布局、镜像校验值及备份时间。不同载板或存储布局之间不能默认直接恢复。官方 BSP 中的工具路径和参数也随版本变化，应使用对应版本说明。

## 恢复演练才是最终检查

先完成应用级备份，再按匹配的官方流程进行板级备份。找一台允许恢复的同配置设备，检查能否启动、网络是否正常、外置盘是否挂载、容器和串口是否工作，最后验证一个真实业务动作。

这篇是备份方案笔记，原交流没有恢复演练成功记录。因此我不会把“工具可用”写成“已经实现一键恢复”。真正可交付的备份，应带有一份可重复执行的恢复检查表。

## 参考资料

- [Jetson Linux 官方归档](https://developer.nvidia.com/embedded/jetson-linux-archive)
- [Flashing Support](https://docs.nvidia.com/jetson/archives/r36.4.3/DeveloperGuide/SD/FlashingSupport.html)
