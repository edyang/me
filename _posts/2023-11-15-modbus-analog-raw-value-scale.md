---
layout: post
title: 模拟量采集：研究寄存器值到电压的换算
subtitle: 给模拟量输入施加约 12V 后，读到接近 [0, 21220] 的数组。
date: 2023-11-15 08:00:00 +0800
author: edyang
header-style: text
catalog: true
tags:
- Modbus
- 传感器
- 物联网
tech_note: true
note_id: modbus-analog-raw-value-scale
source_date: '2026-10-09'
source_dates:
- '2026-10-09'
published_at: '2026-10-12T12:51:43+08:00'
updated_at: '2026-10-13T17:59:15+08:00'
verification: observed
privacy_reviewed: true
permalink: /tech/2026/10/09/modbus-analog-raw-value-scale/
excerpt: 给模拟量输入施加约 12V 后，读到接近 [0, 21220] 的数组。
archive_date: '2023-11-15'
date_basis: simulated_weekly_archive
content_revision: 2
images:
- /img/tech-notes/modbus-analog-raw-value-scale.svg
---

给模拟量输入施加约 12V 后，读到接近 [0, 21220] 的数组。我想把它换成电压，但一组读数只能证明有响应，还不能确认数组含义、零点与比例。

## 研究与排查过程

研究先查寄存器布局：两项可能是两个通道，也可能是高低字或带状态结果。起始地址、读取数量、类型、字节序与厂家比例需要对照手册。随后提出在允许量程内用多个已测输入点记录原始值，用两点检查零点和斜率，再用第三点判断线性，而不把电源铭牌当精密参考。

![模拟量采集：研究寄存器值到电压的换算研究路径示意](/img/tech-notes/modbus-analog-raw-value-scale.svg)

## 涉及的技术与取舍

技术涉及 Modbus 数据模型、原始采集、比例换算与有效值检查。量程和通道模式固定后再标定，失联与无效数据不能当成 0V。业务阈值在换算稳定后实现，阈值附近可研究滞回与防抖；输入接法与隔离关系仍以模块结构和手册为准，本文不公开现场接线。

### 辅助检查示例

以下为通用示例，用于理解上述检查；变量、设备和参数需对应实际环境。

```text
记录项：通道、量程模式、参考电压、原始值、换算值、时间
```

## 这轮研究的结论

现有记录确认输入对应寄存器变化，没有最终换算验收。结论是先证明读的是预期物理量，再建立单位转换，最后加入业务判断。单点比例即使看起来合理，也需要独立输入验证后才能使用。

## 参考资料

- [Modbus 数据模型与协议](https://www.modbus.org/specs.php)
