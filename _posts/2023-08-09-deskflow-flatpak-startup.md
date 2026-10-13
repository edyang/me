---
layout: post
title: Mac 与 Ubuntu 共享键鼠：研究 Deskflow 自启动
subtitle: 我希望 Mac 的物理键鼠跨屏控制 Ubuntu，同时在登录后自动连接，不需要整套远程桌面。
date: 2023-08-09 08:00:00 +0800
author: edyang
header-style: text
catalog: true
tags:
- macOS
- Linux
- 效率工具
tech_note: true
note_id: deskflow-flatpak-startup
source_date: '2026-09-14'
source_dates:
- '2026-09-14'
published_at: '2026-10-12T12:51:43+08:00'
updated_at: '2026-10-13T17:59:15+08:00'
verification: partial
privacy_reviewed: true
permalink: /tech/2026/09/14/deskflow-flatpak-startup/
excerpt: 我希望 Mac 的物理键鼠跨屏控制 Ubuntu，同时在登录后自动连接，不需要整套远程桌面。
archive_date: '2023-08-09'
date_basis: simulated_weekly_archive
content_revision: 2
images:
- /img/tech-notes/deskflow-flatpak-startup.svg
---

我希望 Mac 的物理键鼠跨屏控制 Ubuntu，同时在登录后自动连接，不需要整套远程桌面。研究选择了 Deskflow，并碰到 Flatpak 源配置和下载慢的问题，因此安装、连接和自启动分三个阶段处理。

## 研究与排查过程

先检查 Flatpak remote 与应用是否可启动，下载异常再看实际下载进程的网络。手动连通阶段对照服务端、客户端名称与屏幕位置，并检查 macOS 输入权限及 Linux 图形会话支持。拥有物理键鼠的一端作为服务端，另一端接收输入，名称配置需要一致。

![Mac 与 Ubuntu 共享键鼠：研究 Deskflow 自启动研究路径示意](/img/tech-notes/deskflow-flatpak-startup.svg)

## 涉及的技术与取舍

采用的软件 KVM 技术只转发输入，自动启动依赖登录后的图形环境。方案研究系统登录项或桌面会话自启动，调用当前安装的应用命令并复用正确配置。断网重连、键盘布局和剪贴板能力需要分别检查，普通无图形系统服务不能直接替代桌面应用启动。

### 辅助检查示例

以下为通用示例，用于理解上述检查；变量、设备和参数需对应实际环境。

```bash
flatpak remotes
flatpak run org.deskflow.deskflow
```

## 这轮研究的结论

初步结论是先让两端手动连接稳定，再做登录后自动启动与恢复测试。原记录没有重启后自动连接验收，因而不能宣称已经完成无人干预。后续应重启两端并测试断网恢复，保留权限与配置版本。

## 参考资料

- [Deskflow 官方仓库](https://github.com/deskflow/deskflow)
- [Flatpak 使用文档](https://docs.flatpak.org/en/latest/using-flatpak.html)
