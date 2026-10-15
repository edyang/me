---
layout: post
title: MQTT 保留消息：适合状态，不适合随便保存动作
subtitle: 新订阅者立刻收到一条旧消息，可能是 retained（保留消息）机制正常工作，不是设备刚刚执行了一次。
date: 2018-01-25 08:00:00 +0800
author: edyang
header-style: text
catalog: true
tags:
- 物联网
- 通信协议
tech_note: true
note_id: mqtt-retained-message-state
permalink: /tech/2018/01/25/mqtt-retained-message-state/
excerpt: 新订阅者立刻收到一条旧消息，可能是 retained（保留消息）机制正常工作，不是设备刚刚执行了一次。
privacy_reviewed: true
content_revision: 3
images:
- /img/tech-notes/mqtt-retained-message-state.svg
technology_since: '2014-10-29'
---

新订阅者立刻收到一条旧消息，可能是 retained（保留消息）机制正常工作，不是设备刚刚执行了一次。

本文使用MQTT 3.1.1、HTTP 或 CoAP 的演示设备与消息。设备通信需要同时定义身份、数据语义、时序与失败处理。协议传输确认不自动代表业务动作完成，采样时间也不能简单用服务器收到消息的时刻替代。

## 1. 从现象推到机制

保留消息保存主题的最近一份状态供后续订阅者获取，不是完整历史队列。若把一次性动作当成保留命令，设备重连后可能重新看到旧意图。消息还应带状态时间，让消费方判断是否陈旧。

![MQTT 保留消息：适合状态，不适合随便保存动作的处理、反馈与观察关系](/img/tech-notes/mqtt-retained-message-state.svg)

图中的四个节点分别表示状态发布、代理保留、新订阅者、新鲜度判断。顺着实线检查输入如何变成输出，再沿虚线核对反馈条件。图示表达的是本文讨论的关系，不是实测曲线或现场截图。

## 2. 最小实现与输入条件

先在演示主题发布带采样时间的状态，再启动新订阅者观察。清除保留消息按协议使用相应空载荷方式，不在真实控制主题练习。

```text
retained state: reported_state, observed_at
new subscriber -> receives last retained state
consumer -> checks freshness before showing current status
one-shot command -> separate non-retained policy
```

在独立代理与虚构设备标识下实验，保留发布端、代理和消费端记录。命令与遥测使用不同主题及权限；网络断开、重复消息和设备重启都要作为正常分支观察。

## 3. 用对照区分原因

下表列出需要主动改变的条件。预期行为来自机制分析，复现时还需记录运行环境和原始输出，不能将预期当作已经测得的结果。

| 改变的条件 | 需要验证的行为 |
| --- | --- |
| 新订阅者收到旧状态 | 应显示原始观测时间 |
| 一次性动作被保留 | 重连可能再次呈现旧动作 |
| 主题没有保存完整历史 | 不能用于追溯全部变化 |

### 对照 1：新订阅者收到旧状态

应显示原始观测时间。观察时记录消息的保留标志与时间字段。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 2：一次性动作被保留

重连可能再次呈现旧动作。观察时记录命令语义与 retained 配置。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 3：主题没有保存完整历史

不能用于追溯全部变化。观察时记录保留消息数量与历史存储。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。

## 4. 适用条件与取舍

保留状态也需要权限和生命周期。设备退役时清理旧主题，避免新设备复用身份后误读历史状态。

一次正常运行只覆盖了这组输入。继续扩展前，应把上面的异常对照保留下来，尤其关注“主题没有保存完整历史”这一分支。后续方案若改变了图中任意一处依赖，原来的判断就要重新验证，不能仅凭界面相似或返回值相同沿用结论。

## 同月延伸

- [物联网协议：命令、遥测和状态主题分开设计](/tech/2018/01/05/mqtt311-topics-command-telemetry/)
- [MQTT QoS：协议确认不等于业务只执行一次](/tech/2018/01/15/mqtt311-qos-business-once/)

## 参考资料

1. [MQTT 3.1.1 标准](https://docs.oasis-open.org/mqtt/mqtt/v3.1.1/os/mqtt-v3.1.1-os.html)
2. [CoAP：RFC 7252](https://www.rfc-editor.org/rfc/rfc7252)
