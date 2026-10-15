---
layout: post
title: 树莓派网关：Modbus 文档地址与协议偏移
subtitle: 手册写四万开头地址，库函数却要求从零开始的偏移。
date: 2019-04-05 08:00:00 +0800
author: edyang
header-style: text
catalog: true
tags:
- 树莓派
- 工业协议
tech_note: true
note_id: modbus-register-addressing
permalink: /tech/2019/04/05/modbus-register-addressing/
excerpt: 手册写四万开头地址，库函数却要求从零开始的偏移。
privacy_reviewed: true
content_revision: 3
images:
- /img/tech-notes/modbus-register-addressing.svg
technology_since: '2016-02-29'
---

手册写四万开头地址，库函数却要求从零开始的偏移。地址表示法不统一会读错寄存器。

本文使用树莓派 3、Linux 与模拟 Modbus 从站或离线字节。网关首先负责协议与数据质量转换，不把每次收到字节都当成有效工程量。地址、字节顺序、采样周期与设备身份都应由明确协议定义。

## 1. 从现象推到机制

功能码选择寄存器区域，协议请求中的地址通常是区内偏移，手册可能使用另一套编号。输入寄存器和保持寄存器不能仅凭数字相近就互换。读取数量与数据类型也要同时确认。

![树莓派网关：Modbus 文档地址与协议偏移的处理、反馈与观察关系](/img/tech-notes/modbus-register-addressing.svg)

图中的四个节点分别表示手册编号、协议请求、原始寄存器、工程字段。顺着实线检查输入如何变成输出，再沿虚线核对反馈条件。图示表达的是本文讨论的关系，不是实测曲线或现场截图。

## 2. 最小实现与输入条件

先在模拟从站设置两个可区分值，按手册映射逐项核对。本文不提供任何未知设备的真实寄存器控制表。

```text
manual label -> function code + protocol offset
read count -> number of 16-bit registers
response -> raw words + quality
conversion -> model-specific documented mapping
```

先用模拟设备或离线报文验证，硬件侧按接口手册接入。轮询失败保留异常和最后有效时间，写寄存器不属于默认测试范围，不向未知真实设备发送控制指令。

## 3. 用对照区分原因

下表列出需要主动改变的条件。预期行为来自机制分析，复现时还需记录运行环境和原始输出，不能将预期当作已经测得的结果。

| 改变的条件 | 需要验证的行为 |
| --- | --- |
| 偏移差一位 | 可能读到合法但完全不同的值 |
| 区域功能码选错 | 可能异常或得到另一块数据 |
| 一项数据占两个寄存器 | 读取数量需要覆盖完整字段 |

### 对照 1：偏移差一位

可能读到合法但完全不同的值。观察时记录模拟从站的相邻寄存器。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 2：区域功能码选错

可能异常或得到另一块数据。观察时记录功能码与手册区域。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 3：一项数据占两个寄存器

读取数量需要覆盖完整字段。观察时记录字段宽度与返回字数。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。

## 4. 适用条件与取舍

读到稳定数字不代表地址正确。只有与已知输入和手册字段对应，才能把原始值解释为工程量。

一次正常运行只覆盖了这组输入。继续扩展前，应把上面的异常对照保留下来，尤其关注“一项数据占两个寄存器”这一分支。后续方案若改变了图中任意一处依赖，原来的判断就要重新验证，不能仅凭界面相似或返回值相同沿用结论。

## 同月延伸

- [树莓派网关：两个寄存器怎样组合成浮点数](/tech/2019/04/15/modbus-byte-word-order/)
- [树莓派网关：断网缓存需要容量和补传规则](/tech/2019/04/25/gateway-offline-buffer-replay/)

## 参考资料

1. [Modbus 应用协议规范](https://www.modbus.org/file/secure/modbusprotocolspecification.pdf)
2. [Raspberry Pi 官方文档](https://www.raspberrypi.com/documentation/)
