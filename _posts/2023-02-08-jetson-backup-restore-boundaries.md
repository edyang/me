---
layout: post
title: 研究 Jetson 系统备份与恢复方案
subtitle: 边缘设备安装好驱动、模型和服务以后，真正难重建的是整套运行环境。
date: 2023-02-08 08:00:00 +0800
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
updated_at: '2026-10-13T17:59:15+08:00'
verification: proposal
privacy_reviewed: true
permalink: /tech/2026/04/03/jetson-backup-restore-boundaries/
excerpt: 边缘设备安装好驱动、模型和服务以后，真正难重建的是整套运行环境。
archive_date: '2023-02-08'
date_basis: simulated_weekly_archive
content_revision: 2
images:
- /img/tech-notes/jetson-backup-restore-boundaries.svg
---

边缘设备安装好驱动、模型和服务以后，真正难重建的是整套运行环境。我希望用另一台 Linux 主机保存设备状态，故障时尽快恢复，因此先研究不同备份工具到底保存了哪些内容。

## 研究与排查过程

讨论先把恢复目标拆开：只重新部署应用、恢复系统分区，还是恢复一台能直接启动的同配置设备。随后再检查系统位于 eMMC 还是外置 NVMe，启动分区和应用数据是否在同一介质。这个顺序很有用，因为仅复制根目录，可能保存了程序，却遗漏启动配置或外置盘。

![研究 Jetson 系统备份与恢复方案研究路径示意](/img/tech-notes/jetson-backup-restore-boundaries.svg)

## 涉及的技术与取舍

技术上区分应用文件备份、rootfs 克隆和匹配 Jetson Linux BSP 的板级备份恢复。应用层保存代码、容器版本、模型和配置；系统层保存镜像与分区信息；板级恢复还需对应模块、载板和启动相关分区。镜像旁同时记录 JetPack/L4T 版本、存储布局和校验值，避免拿不匹配的刷机工具直接恢复。

## 这轮研究的结论

初步结论是先建立应用资产备份，再选择与板卡版本匹配的系统备份路径。真正的验收要在允许恢复的同配置设备上演练，检查启动、网络、挂载、串口和业务请求。这轮没有恢复成功的实测记录，因此只能确认方案层次，尚不能称为一键恢复。

## 参考资料

- [Jetson Linux 官方归档](https://developer.nvidia.com/embedded/jetson-linux-archive)
- [Flashing Support](https://docs.nvidia.com/jetson/archives/r36.4.3/DeveloperGuide/SD/FlashingSupport.html)
