---
layout: post
title: 树莓派网关：断网缓存需要容量和补传规则
subtitle: 本地缓存能应对短断网，但磁盘有限，恢复后也不能无限速把历史数据压向服务端。
date: 2019-04-25 08:00:00 +0800
author: edyang
header-style: text
catalog: true
tags:
- 树莓派
- 工业协议
tech_note: true
note_id: gateway-offline-buffer-replay
permalink: /tech/2019/04/25/gateway-offline-buffer-replay/
excerpt: 本地缓存能应对短断网，但磁盘有限，恢复后也不能无限速把历史数据压向服务端。
privacy_reviewed: true
content_revision: 3
images:
- /img/tech-notes/gateway-offline-buffer-replay.svg
technology_since: '2016-02-29'
---

本地缓存能应对短断网，但磁盘有限，恢复后也不能无限速把历史数据压向服务端。

本文使用树莓派 3、Linux 与模拟 Modbus 从站或离线字节。网关首先负责协议与数据质量转换，不把每次收到字节都当成有效工程量。地址、字节顺序、采样周期与设备身份都应由明确协议定义。

## 1. 从现象推到机制

每个样本保存稳定身份和采样时刻，发送成功后按确认规则清理。服务端通过事件号去重。缓存需要容量上限、满载策略和缺口报告，补传采用有限批次，实时数据与历史队列分配资源。

![树莓派网关：断网缓存需要容量和补传规则的处理、反馈与观察关系](/img/tech-notes/gateway-offline-buffer-replay.svg)

图中的四个节点分别表示采样事件、本地队列、有界发送、确认清理。顺着实线检查输入如何变成输出，再沿虚线核对反馈条件。图示表达的是本文讨论的关系，不是实测曲线或现场截图。

## 2. 最小实现与输入条件

先用本地 SQLite 演示待发送队列，模拟响应丢失而服务端已经处理。重发保持相同事件号，不按发送次数生成新身份。

```text
sample -> persist pending event
send bounded batch -> verify server acknowledgement
acknowledged -> mark delivered
restart -> replay same event ids
full storage -> explicit loss or backpressure policy
```

先用模拟设备或离线报文验证，硬件侧按接口手册接入。轮询失败保留异常和最后有效时间，写寄存器不属于默认测试范围，不向未知真实设备发送控制指令。

## 3. 用对照区分原因

下表列出需要主动改变的条件。预期行为来自机制分析，复现时还需记录运行环境和原始输出，不能将预期当作已经测得的结果。

| 改变的条件 | 需要验证的行为 |
| --- | --- |
| 服务端处理后响应丢失 | 重发应被识别为同一事件 |
| 断网持续超过容量 | 需要明确缺口与满载处理 |
| 恢复后全量瞬间补传 | 可能挤压实时业务 |

### 对照 1：服务端处理后响应丢失

重发应被识别为同一事件。观察时记录稳定身份与服务器去重记录。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 2：断网持续超过容量

需要明确缺口与满载处理。观察时记录剩余空间和保留策略。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 3：恢复后全量瞬间补传

可能挤压实时业务。观察时记录批量限速与队列年龄。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。

## 4. 适用条件与取舍

本地落盘也需要事务和介质验证。只能承诺已验证容量和故障范围内的恢复，不能笼统写成永不丢数据。

一次正常运行只覆盖了这组输入。继续扩展前，应把上面的异常对照保留下来，尤其关注“恢复后全量瞬间补传”这一分支。后续方案若改变了图中任意一处依赖，原来的判断就要重新验证，不能仅凭界面相似或返回值相同沿用结论。

## 同月延伸

- [树莓派网关：Modbus 文档地址与协议偏移](/tech/2019/04/05/modbus-register-addressing/)
- [树莓派网关：两个寄存器怎样组合成浮点数](/tech/2019/04/15/modbus-byte-word-order/)

## 参考资料

1. [Modbus 应用协议规范](https://www.modbus.org/file/secure/modbusprotocolspecification.pdf)
2. [Raspberry Pi 官方文档](https://www.raspberrypi.com/documentation/)
