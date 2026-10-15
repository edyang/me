---
layout: post
title: MQTT 设备在线：遗嘱、心跳和数据新鲜度分开看
subtitle: 代理显示客户端在线，但传感器已经停止采样，说明连接健康和数据健康不是同一指标。
date: 2019-01-05 08:00:00 +0800
author: edyang
header-style: text
catalog: true
tags:
- 物联网
- 可靠性
tech_note: true
note_id: mqtt-last-will-heartbeat-freshness
permalink: /tech/2019/01/05/mqtt-last-will-heartbeat-freshness/
excerpt: 代理显示客户端在线，但传感器已经停止采样，说明连接健康和数据健康不是同一指标。
privacy_reviewed: true
content_revision: 3
images:
- /img/tech-notes/mqtt-last-will-heartbeat-freshness.svg
technology_since: '2018-08-14'
---

代理显示客户端在线，但传感器已经停止采样，说明连接健康和数据健康不是同一指标。

本文使用MQTT 3.1.1、Node-RED 0.19 与虚构设备消息。从能通信走向稳定运行，需要对离线、重复、乱序和恢复建立明确语义。本文使用演示身份和事件，不连接真实控制负载，也没有声称取得未经记录的现场效果。

## 1. 从现象推到机制

Keep Alive（保活）帮助协议端发现失联，遗嘱在符合条件的异常断开后由代理发布。正常断开不一定触发相同消息。数据新鲜度还需按最后有效采样判断，不能因为连接没断就展示实时。

![MQTT 设备在线：遗嘱、心跳和数据新鲜度分开看的处理、反馈与观察关系](/img/tech-notes/mqtt-last-will-heartbeat-freshness.svg)

图中的四个节点分别表示协议连接、遗嘱消息、有效采样、健康展示。顺着实线检查输入如何变成输出，再沿虚线核对反馈条件。图示表达的是本文讨论的关系，不是实测曲线或现场截图。

## 2. 最小实现与输入条件

分别模拟正常退出、异常失联和采样线程停止。状态消息带观测时间，界面将连接与数据质量分别显示。

```text
connection_state -> broker/session evidence
last_valid_sample -> data freshness
will_message -> unexpected disconnect semantics
health = connection + sampling + business checks
```

保留设备、网关和服务端各自时间与状态，按固定故障顺序复现。每次恢复后检查数据归属和未完成工作，不只观察连接图标重新变绿。

## 3. 用对照区分原因

下表列出需要主动改变的条件。预期行为来自机制分析，复现时还需记录运行环境和原始输出，不能将预期当作已经测得的结果。

| 改变的条件 | 需要验证的行为 |
| --- | --- |
| 采样停止但连接保持 | 设备可在线而数据已过期 |
| 客户端正常发送断开 | 不能默认出现异常遗嘱 |
| 网络突然失联 | 遗嘱发布时间受检测时序影响 |

### 对照 1：采样停止但连接保持

设备可在线而数据已过期。观察时记录最近有效采样与会话状态。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 2：客户端正常发送断开

不能默认出现异常遗嘱。观察时记录协议断开过程。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 3：网络突然失联

遗嘱发布时间受检测时序影响。观察时记录保活配置与实际超时。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。

## 4. 适用条件与取舍

遗嘱不提供精确故障发生时刻。告警应表达已观察到的失联或过期，不把检测时刻写成设备真正停止工作的准确时间。

一次正常运行只覆盖了这组输入。继续扩展前，应把上面的异常对照保留下来，尤其关注“网络突然失联”这一分支。后续方案若改变了图中任意一处依赖，原来的判断就要重新验证，不能仅凭界面相似或返回值相同沿用结论。

## 同月延伸

- [MQTT 重连：会话恢复与业务补传分别设计](/tech/2019/01/15/mqtt-session-reconnect-duplicates/)
- [物联网时间研究：采样时刻与接收时刻不能混成一列](/tech/2019/01/25/iot-sample-time-receive-time/)

## 参考资料

1. [MQTT 3.1.1 标准](https://docs.oasis-open.org/mqtt/mqtt/v3.1.1/os/mqtt-v3.1.1-os.html)
2. [Node-RED 0.19 发布记录](https://nodered.org/blog/2018/08/14/version-0-19-released)
