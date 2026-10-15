---
layout: post
title: 物联网基础：HTTP、MQTT 与 CoAP 按交互方式比较
subtitle: 协议选择不能只比较报文大小。
date: 2018-02-15 08:00:00 +0800
author: edyang
header-style: text
catalog: true
tags:
- 物联网
- 通信协议
tech_note: true
note_id: iot-coap-http-mqtt-selection
permalink: /tech/2018/02/15/iot-coap-http-mqtt-selection/
excerpt: 协议选择不能只比较报文大小。
privacy_reviewed: true
content_revision: 3
images:
- /img/tech-notes/iot-coap-http-mqtt-selection.svg
technology_since: '2014-10-29'
---

协议选择不能只比较报文大小。设备是否长连接、是否需要服务端推送，会改变方案。

本文使用MQTT 3.1.1、HTTP 或 CoAP 的演示设备与消息。设备通信需要同时定义身份、数据语义、时序与失败处理。协议传输确认不自动代表业务动作完成，采样时间也不能简单用服务器收到消息的时刻替代。

## 1. 从现象推到机制

HTTP 便于请求响应与现有 Web 接口集成，MQTT 借助代理实现发布订阅，CoAP 面向受限设备设计轻量资源交互。传输、可靠性和安全机制各有前提，弱网不意味着任意一种协议都会自动省电或可靠。

![物联网基础：HTTP、MQTT 与 CoAP 按交互方式比较的处理、反馈与观察关系](/img/tech-notes/iot-coap-http-mqtt-selection.svg)

图中的四个节点分别表示交互需求、设备约束、协议机制、最小实验。顺着实线检查输入如何变成输出，再沿虚线核对反馈条件。图示表达的是本文讨论的关系，不是实测曲线或现场截图。

## 2. 最小实现与输入条件

先列设备采样周期、网络类型、下行需求和代理条件，再为一种交互做最小实验。比较完整连接和重传成本，而非只看单个载荷字节。

```text
request / response -> HTTP or resource-oriented CoAP evaluation
publish / subscribe -> MQTT evaluation
constraints -> power, network, payload, downlink, authentication
```

在独立代理与虚构设备标识下实验，保留发布端、代理和消费端记录。命令与遥测使用不同主题及权限；网络断开、重复消息和设备重启都要作为正常分支观察。

## 3. 用对照区分原因

下表列出需要主动改变的条件。预期行为来自机制分析，复现时还需记录运行环境和原始输出，不能将预期当作已经测得的结果。

| 改变的条件 | 需要验证的行为 |
| --- | --- |
| 设备经常休眠 | 连接维护和重连成本需要计算 |
| 需要向多订阅者推送 | 发布订阅可减少直接耦合 |
| 网络有丢包 | 仍需检查协议具体重传语义 |

### 对照 1：设备经常休眠

连接维护和重连成本需要计算。观察时记录唤醒周期与实际网络耗时。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 2：需要向多订阅者推送

发布订阅可减少直接耦合。观察时记录代理可用性与主题权限。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 3：网络有丢包

仍需检查协议具体重传语义。观察时记录端到端成功与重复消息。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。

## 4. 适用条件与取舍

协议适配层不应改变业务事件身份。未来替换传输方式时，采样、命令和状态契约仍应保持可解释。

一次正常运行只覆盖了这组输入。继续扩展前，应把上面的异常对照保留下来，尤其关注“网络有丢包”这一分支。后续方案若改变了图中任意一处依赖，原来的判断就要重新验证，不能仅凭界面相似或返回值相同沿用结论。

## 同月延伸

- [物联网基础：设备数据契约先定义单位和质量](/tech/2018/02/05/iot-device-data-contract/)
- [米家研究：设备、网关、云与授权的关系](/tech/2018/02/25/mijia-device-gateway-cloud/)

## 参考资料

1. [MQTT 3.1.1 标准](https://docs.oasis-open.org/mqtt/mqtt/v3.1.1/os/mqtt-v3.1.1-os.html)
2. [CoAP：RFC 7252](https://www.rfc-editor.org/rfc/rfc7252)
