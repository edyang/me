---
layout: post
title: Mac 与 Ubuntu 共用键鼠：Deskflow 的安装和自启动要分开测
subtitle: 局域网共享键鼠要确认服务端、客户端、权限和图形会话，再设置自动启动。
date: 2026-09-14 08:00:00 +0800
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
updated_at: '2026-10-12T12:51:43+08:00'
verification: partial
privacy_reviewed: true
permalink: /tech/2026/09/14/deskflow-flatpak-startup/
excerpt: 局域网共享键鼠要确认服务端、客户端、权限和图形会话，再设置自动启动。
---

希望 Mac 的键鼠控制 Ubuntu，且不需要远程桌面。Deskflow 属于软件 KVM：鼠标跨屏时，输入被转发到另一台设备。它的安装成功、连接成功和开机自动连接，是三件事。

## 安装错误先找具体来源

历史安装遇到 Flathub remote 缺失，也遇到下载慢。先检查远程源是否存在，再处理网络下载问题。Ubuntu 发行版代号应与安装包匹配，不能只因文件名新就选择其它发行版的包。

```bash
flatpak remotes
flatpak run org.deskflow.deskflow
```

这个应用 ID 来自当时的安装记录。后续版本或分发方式变化时，以官方仓库和应用清单为准。

## 服务端与客户端都要验证

拥有物理键鼠的机器作为服务端，另一台作为客户端。核对两台机器的名称、屏幕位置、连接地址和安全配对。macOS 侧检查输入相关系统权限，Linux 侧确认当前图形会话支持情况。

## 自动启动依赖登录后的图形环境

先手动连接稳定，再使用系统登录项或桌面会话自启动。Flatpak 应用的配置与命令要以当前版本为准，不把普通系统服务直接塞到无图形环境中。

原记录没有自动连接验收结果。最后需要重启两端，验证登录后能自动连接、键盘布局正常、剪贴板符合设置，且断网后能恢复。

## 参考资料

- [Deskflow 官方仓库](https://github.com/deskflow/deskflow)
- [Flatpak 使用文档](https://docs.flatpak.org/en/latest/using-flatpak.html)
