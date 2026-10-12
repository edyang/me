---
layout: post
title: Android WebView 没有实时消息：页面刷新可能反复断开 WebSocket
subtitle: 服务端有 WebSocket 接口，不代表 WebView 已经建立并维持连接。
date: 2026-09-15 08:00:00 +0800
author: edyang
header-style: text
catalog: true
tags:
- Android
- WebSocket
- 故障排查
tech_note: true
note_id: android-webview-websocket-reconnect
source_date: '2026-09-15'
source_dates:
- '2026-09-15'
published_at: '2026-10-12T12:51:43+08:00'
updated_at: '2026-10-12T12:51:43+08:00'
verification: proposal
privacy_reviewed: true
permalink: /tech/2026/09/15/android-webview-websocket-reconnect/
excerpt: 服务端有 WebSocket 接口，不代表 WebView 已经建立并维持连接。
---

网页中的实时状态正常，在 Android WebView 里却一直显示断开。除了地址和网络策略，还应检查页面是否被定时 reload，导致连接不断被销毁。

## 页面生命周期是一个重点

`loadUrl` 或 `reload` 会重新加载页面。若应用每隔几秒刷新一次，页面内的 WebSocket 也可能随之关闭并重建。服务端有接口、网页有重连代码，都不能排除这一问题。

## 从服务端连接日志开始

先确认是否出现握手、accepted 和断开记录。如果根本没握手，检查 URL、网络和明文访问策略。如果周期性连接又立刻断开，检查页面生命周期和应用后台行为。

## 重连应使用受控退避

连接失败时延迟重试，并设置上限和抖动；恢复后重置退避。页面销毁时清理旧连接和定时器，避免同时存在多个 socket。连接状态、最后消息时间和业务数据有效性，也应分开显示。

涉及 `http/ws` 时，按 Android 网络安全配置明确允许范围；不要为了调试在生产中无差别放开全部明文流量。优先使用与部署环境匹配的安全连接。

原交流没有 Android 源码，reload 只是待验证方向。本文明确保留这一点，不把怀疑写成已确认根因。

## 参考资料

- [Android 网络安全配置](https://developer.android.com/privacy-and-security/security-config)
