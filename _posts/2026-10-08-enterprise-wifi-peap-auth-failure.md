---
layout: post
title: 企业 Wi-Fi 卡在 configuring：先区分认证和 DHCP
subtitle: 已关联 AP 不代表认证通过，密码过期日志也不能靠改 IP 解决。
date: 2026-10-08 08:00:00 +0800
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
updated_at: '2026-10-12T12:51:43+08:00'
verification: partial
privacy_reviewed: true
permalink: /tech/2026/10/08/enterprise-wifi-peap-auth-failure/
excerpt: 已关联 AP 不代表认证通过，密码过期日志也不能靠改 IP 解决。
---

NetworkManager 显示 Wi-Fi 一直处于 configuring，设备能看到 AP，却没有进入正常联网状态。排查需要分清关联、802.1X 认证、地址获取和路由。

## 按阶段看日志

```bash
nmcli device status
nmcli connection show --active
sudo journalctl -u NetworkManager --since "15 minutes ago"
```

公开日志前应移除真实 SSID、用户名、设备 MAC 和内部地址。保留认证方法、错误码和阶段即可。

## 一条明确的认证错误

历史记录出现 `EAP-MSCHAPV2: Password expired`、错误 648 和请求新密码的提示。这些线索指向认证账户状态，而不是 DHCP 没分配地址。设备配置静态 IP，也不会让未通过认证的链路自动可用。

## 修复后重新验证后续阶段

由网络管理员核对账号状态和认证策略，再按组织要求更新配置与证书。认证通过后继续检查 DHCP、默认路由、DNS 和目标业务端口。不能为了连接成功就随意关闭证书校验。

记录确认了认证日志线索，没有账户调整后的成功反馈。因此最后应补一组从认证完成到业务可达的证据，避免只看 Wi-Fi 图标。

## 参考资料

- [NetworkManager nmcli 文档](https://networkmanager.dev/docs/api/latest/nmcli.html)
