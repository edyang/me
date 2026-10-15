---
layout: post
title: MQTT 重连：会话恢复与业务补传分别设计
subtitle: 设备重连后收到旧消息，可能是会话策略正常恢复。
date: 2019-01-15 08:00:00 +0800
author: edyang
header-style: text
catalog: true
tags:
- 物联网
- 可靠性
tech_note: true
note_id: mqtt-session-reconnect-duplicates
permalink: /tech/2019/01/15/mqtt-session-reconnect-duplicates/
excerpt: 设备重连后收到旧消息，可能是会话策略正常恢复。
privacy_reviewed: true
content_revision: 3
images:
- /img/tech-notes/mqtt-session-reconnect-duplicates.svg
technology_since: '2018-08-14'
---

设备重连后收到旧消息，可能是会话策略正常恢复。重新订阅与重复消费需要结合协议条件理解。

本文使用MQTT 3.1.1、Node-RED 0.19 与虚构设备消息。从能通信走向稳定运行，需要对离线、重复、乱序和恢复建立明确语义。本文使用演示身份和事件，不连接真实控制负载，也没有声称取得未经记录的现场效果。

## 1. 从现象推到机制

Clean Session（清理会话标志）、客户端身份与代理配置共同影响会话保留。客户端重启生成新身份，可能失去原来的会话关系。业务补传还需要稳定事件号和本地状态，不能仅依赖代理替所有数据保管。

![MQTT 重连：会话恢复与业务补传分别设计的处理、反馈与观察关系](/img/tech-notes/mqtt-session-reconnect-duplicates.svg)

图中的四个节点分别表示稳定身份、会话规则、启动身份、业务补传。顺着实线检查输入如何变成输出，再沿虚线核对反馈条件。图示表达的是本文讨论的关系，不是实测曲线或现场截图。

## 2. 最小实现与输入条件

用演示客户端分别保持和清理会话，记录订阅、离线消息与重连结果。设备重启时保留独立启动身份，避免采样序号重置后冲突。

```text
device_id -> stable identity
boot_id -> one device runtime session
sample_id -> boot_id + sequence
reconnect -> inspect session and replay policy
consumer -> deduplicate by business sample identity
```

保留设备、网关和服务端各自时间与状态，按固定故障顺序复现。每次恢复后检查数据归属和未完成工作，不只观察连接图标重新变绿。

## 3. 用对照区分原因

下表列出需要主动改变的条件。预期行为来自机制分析，复现时还需记录运行环境和原始输出，不能将预期当作已经测得的结果。

| 改变的条件 | 需要验证的行为 |
| --- | --- |
| 重连时更换客户端身份 | 可能建立另一套会话 |
| 离线期间存在待交付消息 | 恢复行为取决于协议和配置 |
| 设备重启序号从零开始 | 需要启动身份避免样本冲突 |

### 对照 1：重连时更换客户端身份

可能建立另一套会话。观察时记录代理看到的实际 client id。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 2：离线期间存在待交付消息

恢复行为取决于协议和配置。观察时记录会话保留与消息 QoS。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 3：设备重启序号从零开始

需要启动身份避免样本冲突。观察时记录事件身份组成。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。

## 4. 适用条件与取舍

离线缓存有容量与保留期限。超过能力范围时要报告丢失或缺口，不能宣称任何时长断网都能无损恢复。

一次正常运行只覆盖了这组输入。继续扩展前，应把上面的异常对照保留下来，尤其关注“设备重启序号从零开始”这一分支。后续方案若改变了图中任意一处依赖，原来的判断就要重新验证，不能仅凭界面相似或返回值相同沿用结论。

## 同月延伸

- [MQTT 设备在线：遗嘱、心跳和数据新鲜度分开看](/tech/2019/01/05/mqtt-last-will-heartbeat-freshness/)
- [物联网时间研究：采样时刻与接收时刻不能混成一列](/tech/2019/01/25/iot-sample-time-receive-time/)

## 参考资料

1. [MQTT 3.1.1 标准](https://docs.oasis-open.org/mqtt/mqtt/v3.1.1/os/mqtt-v3.1.1-os.html)
2. [Node-RED 0.19 发布记录](https://nodered.org/blog/2018/08/14/version-0-19-released)
