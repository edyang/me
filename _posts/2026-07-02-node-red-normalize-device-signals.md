---
layout: post
title: Node-RED 设备信号：先统一语义，再写报警逻辑
subtitle: 组合信号与独立信号不能用同一含义解释，数据格式也需要在入口统一。
date: 2026-07-02 08:00:00 +0800
author: edyang
header-style: text
catalog: true
tags:
- Node-RED
- 物联网
- Modbus
tech_note: true
note_id: node-red-normalize-device-signals
source_date: '2026-07-02'
source_dates:
- '2026-07-02'
published_at: '2026-10-12T12:51:43+08:00'
updated_at: '2026-10-12T12:51:43+08:00'
verification: notes
privacy_reviewed: true
permalink: /tech/2026/07/02/node-red-normalize-device-signals/
excerpt: 组合信号与独立信号不能用同一含义解释，数据格式也需要在入口统一。
---

不同设备可能把状态分别提供，也可能只给一个组合结果。业务规则看起来相同，实际可观察的信息却不同。先统一字段含义，后续逻辑才不会把无法区分的状态强行拆开。

## 组合信号的信息已经丢失

例如“两个条件同时满足”只提供 true/false。结果为 false 时，不能知道到底是哪一个条件不满足。软件命名成两个字段，并不能恢复硬件没有提供的信息。

## 在入口统一数据格式

Node-RED 输入可能是 Buffer、JSON 字符串、数组或对象。入口先解析成一致对象，随后统一单位、有效电平和缺失值。解析失败与信号为 false 应当区分。

```javascript
let data = msg.payload;
if (Buffer.isBuffer(data)) data = data.toString("utf8");
if (typeof data === "string") {
  try { data = JSON.parse(data); }
  catch (e) { node.warn("invalid input"); return null; }
}
msg.payload = data;
return msg;
```

这只是入口解析示例。寄存器映射和报警条件要根据实际模块另行实现，不能直接当成完整控制流程。

## 再处理变化、优先级和限流

周期采集可以与变化事件分开：状态持续更新，报警按规则触发并限制重复播报。多个条件同时成立时明确优先级，恢复事件也要有定义。连接失效时，不要继续把最后一个值当作新鲜数据。

原交流有不同接线条件下的规则讨论，但本文不公开实际 I/O 地址或设备控制逻辑，只保留通用的数据语义和可观察性原则。

## 参考资料

- [Node-RED Function 节点](https://nodered.org/docs/user-guide/writing-functions)
