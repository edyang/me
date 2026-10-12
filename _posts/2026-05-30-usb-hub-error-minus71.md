---
layout: post
title: USB 扩展坞反复报 err=-71：先用鼠标做交叉测试
subtitle: 串口设备消失时，普通鼠标也不能稳定工作，故障范围就应回到扩展坞、线材和供电。
date: 2026-05-30 08:00:00 +0800
author: edyang
header-style: text
catalog: true
tags:
- 硬件
- USB
- 故障排查
tech_note: true
note_id: usb-hub-error-minus71
source_date: '2026-05-30'
source_dates:
- '2026-05-30'
published_at: '2026-10-12T12:51:43+08:00'
updated_at: '2026-10-12T12:51:43+08:00'
verification: observed
privacy_reviewed: true
permalink: /tech/2026/05/30/usb-hub-error-minus71/
excerpt: 串口设备消失时，普通鼠标也不能稳定工作，故障范围就应回到扩展坞、线材和供电。
---

给边缘盒子加了带外部供电的 USB 扩展后，串口适配器不再出现。原接口可以识别，扩展接口不行。此时最有效的补充证据，是换一个简单 USB 设备交叉测试。

## 关键证据来自普通鼠标

鼠标插入扩展坞也无法稳定使用。日志显示 Hub 状态读取失败，出现 `err=-71`，并反复断开、重连。这个现象把故障范围推向 USB 链路，而不是 Node-RED 的串口配置。

## 按这个顺序换变量

先用明确支持数据传输的短上行线；确认接的是扩展坞 HOST 上行口；按设备说明连接外部电源。随后分别测试鼠标、串口适配器，以及另一台主机。每次只换一个部件并保留内核日志。

```bash
lsusb -t
sudo dmesg --follow
```

`-71` 是协议层错误线索，不能凭错误码单独断定一定是供电不足。线材质量、接口接触、扩展坞兼容性和电源状态都需要测试。外部电源铭牌正常，也不证明端口实际供电稳定。

## 何时再回到串口软件

等鼠标或其它简单设备在扩展坞上持续稳定工作，且不再出现 USB 断开日志，再检查串口驱动和 Modbus。否则在上层增加重试，只会把底层掉线包装成看似随机的业务超时。

原记录确认了扩展链路异常，没有确认更换哪个部件最终修复。把这一点保留下来，有助于后续排查避免过早归因。

## 参考资料

- [Linux USB 错误说明](https://docs.kernel.org/driver-api/usb/error-codes.html)
