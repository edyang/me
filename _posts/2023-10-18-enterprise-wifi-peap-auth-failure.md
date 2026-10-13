---
layout: post
title: 企业 Wi-Fi 连接停滞：定位 802.1X 认证阶段
subtitle: Wi-Fi 能发现 AP，却一直停在 configuring。
date: 2023-10-18 08:00:00 +0800
author: edyang
header-style: text
catalog: true
tags:
- Linux
- 网络
- 故障排查
tech_note: true
note_id: enterprise-wifi-peap-auth-failure
source_date: '2026-10-08'
source_dates:
- '2026-10-08'
published_at: '2026-10-12T12:51:43+08:00'
updated_at: '2026-10-13T17:59:15+08:00'
verification: partial
privacy_reviewed: true
permalink: /tech/2026/10/08/enterprise-wifi-peap-auth-failure/
excerpt: Wi-Fi 能发现 AP，却一直停在 configuring。
archive_date: '2023-10-18'
date_basis: simulated_weekly_archive
content_revision: 2
images:
- /img/tech-notes/enterprise-wifi-peap-auth-failure.svg
---

Wi-Fi 能发现 AP，却一直停在 configuring。我需要判断是关联、802.1X 认证、地址分配还是业务访问失败，因此先读取 NetworkManager 日志，而不是直接换成静态 IP。

## 研究与排查过程

关键线索是 EAP-MSCHAPV2: Password expired、错误 648 和请求新密码。它们将这轮排查指向认证账户状态；地址获取在后面，静态 IP 不会让未认证链路自动可用。随后方案转向由网络管理员核对账号状态和策略，并按要求更新配置与证书。

![企业 Wi-Fi 连接停滞：定位 802.1X 认证阶段研究路径示意](/img/tech-notes/enterprise-wifi-peap-auth-failure.svg)

## 涉及的技术与取舍

技术检查采用 nmcli、NetworkManager journal 与 EAP 认证阶段分析。认证完成后继续验证 DHCP、默认路由、DNS 和业务端口，逐层保存结果。公开日志去除 SSID、用户和设备标识，保留认证方式与错误码；不能为临时连接成功随意关闭证书校验。

### 辅助检查示例

以下为通用示例，用于理解上述检查；变量、设备和参数需对应实际环境。

```bash
nmcli device status
nmcli connection show --active
sudo journalctl -u NetworkManager --since "15 minutes ago"
```

## 这轮研究的结论

记录确认认证错误，没有账号调整后的成功反馈。结论是连接状态需要按阶段解释，图标与配置值无法代替认证证据。后续验证应从认证完成一直走到业务请求可达，才能宣布恢复。

## 参考资料

- [NetworkManager nmcli 文档](https://networkmanager.dev/docs/api/latest/nmcli.html)
