---
layout: post
title: USB 扩展坞 err=-71：一次交叉测试的思路
subtitle: 串口适配器接原接口可以识别，接带外部供电的扩展坞却不出现。
date: 2023-04-26 08:00:00 +0800
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
updated_at: '2026-10-13T17:59:15+08:00'
verification: observed
privacy_reviewed: true
permalink: /tech/2026/05/30/usb-hub-error-minus71/
excerpt: 串口适配器接原接口可以识别，接带外部供电的扩展坞却不出现。
archive_date: '2023-04-26'
date_basis: simulated_weekly_archive
content_revision: 2
images:
- /img/tech-notes/usb-hub-error-minus71.svg
---

串口适配器接原接口可以识别，接带外部供电的扩展坞却不出现。我原先可能继续查串口驱动，但普通鼠标在扩展坞上也不稳定，故障范围因此转向整个 USB 上行链路。

## 研究与排查过程

日志里 Hub 状态读取出现 err=-71，并伴随反复断开重连。下一步提出只改变一个变量：换确定能传数据的短上行线，确认 HOST 口，再分别测试鼠标、串口与另一台主机。每次保存相同时间窗口的内核日志，以区分线材、接口、主机兼容和设备本身。

![USB 扩展坞 err=-71：一次交叉测试的思路研究路径示意](/img/tech-notes/usb-hub-error-minus71.svg)

## 涉及的技术与取舍

采用的是 USB 拓扑观察、内核错误定位与交叉替换。lsusb -t 展示设备层级，dmesg --follow 观察插拔时序。-71 提供协议错误线索，却不能单独证明供电不足；外接电源的铭牌同样无法代表端口实际稳定性。先让简单 USB 设备持续工作，之后再回到串口与 Modbus。

### 辅助检查示例

以下为通用示例，用于理解上述检查；变量、设备和参数需对应实际环境。

```bash
lsusb -t
sudo dmesg --follow
```

## 这轮研究的结论

已观察到扩展链路异常，但没有最终更换部件后的结果。结论是通用设备的交叉测试可以快速判断问题是否属于某个业务驱动。在底层持续掉线时提高上层重试次数，只会让故障表现更随机，无法替代链路修复。

## 参考资料

- [Linux USB 错误说明](https://docs.kernel.org/driver-api/usb/error-codes.html)
