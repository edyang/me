---
layout: post
title: 物联网命令：谁能控制、控制了什么要可追溯
subtitle: 界面上能看到设备，不意味着拥有执行全部命令的权限。
date: 2019-08-25 08:00:00 +0800
author: edyang
header-style: text
catalog: true
tags:
- 物联网
- 可靠性
tech_note: true
note_id: iot-command-authorization-audit
permalink: /tech/2019/08/25/iot-command-authorization-audit/
excerpt: 界面上能看到设备，不意味着拥有执行全部命令的权限。
privacy_reviewed: true
content_revision: 3
images:
- /img/tech-notes/iot-command-authorization-audit.svg
technology_since: '2018-08-14'
---

界面上能看到设备，不意味着拥有执行全部命令的权限。读取与控制应分别授权。

本文使用MQTT 3.1.1、Node-RED 0.19 与虚构设备消息。从能通信走向稳定运行，需要对离线、重复、乱序和恢复建立明确语义。本文使用演示身份和事件，不连接真实控制负载，也没有声称取得未经记录的现场效果。

## 1. 从现象推到机制

命令携带业务身份、目标设备、期望动作与有效期限，服务端按操作者权限和设备能力校验。设备反馈关联同一命令号。审计记录事实和结果，不把用户请求值直接当成设备已执行状态。

![物联网命令：谁能控制、控制了什么要可追溯的处理、反馈与观察关系](/img/tech-notes/iot-command-authorization-audit.svg)

图中的四个节点分别表示用户意图、命令校验、设备反馈、审计记录。顺着实线检查输入如何变成输出，再沿虚线核对反馈条件。图示表达的是本文讨论的关系，不是实测曲线或现场截图。

## 2. 最小实现与输入条件

先用虚拟灯验证读者和操作者两类角色，重复发送同一命令号。过期消息拒绝执行，保留拒绝原因。

```text
authorize actor -> device scope -> allowed capability
command_id + expires_at + desired_state
device feedback -> same command_id + actual result
audit -> requested, accepted, executed, observed separately
```

保留设备、网关和服务端各自时间与状态，按固定故障顺序复现。每次恢复后检查数据归属和未完成工作，不只观察连接图标重新变绿。

## 3. 用对照区分原因

下表列出需要主动改变的条件。预期行为来自机制分析，复现时还需记录运行环境和原始输出，不能将预期当作已经测得的结果。

| 改变的条件 | 需要验证的行为 |
| --- | --- |
| 只有只读权限的用户发命令 | 服务端应拒绝而非只隐藏按钮 |
| 同命令重复到达 | 不能重复触发一次性动作 |
| 命令超过有效期限 | 应按规则拒绝旧意图 |

### 对照 1：只有只读权限的用户发命令

服务端应拒绝而非只隐藏按钮。观察时记录真实接口权限判断。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 2：同命令重复到达

不能重复触发一次性动作。观察时记录业务命令号与处理记录。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 3：命令超过有效期限

应按规则拒绝旧意图。观察时记录时钟质量与到期判断。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。

## 4. 适用条件与取舍

审计不能无限保存敏感内容。保留必要身份角色、目标与结果即可，秘密和无关私人数据不应进入公开日志。

一次正常运行只覆盖了这组输入。继续扩展前，应把上面的异常对照保留下来，尤其关注“命令超过有效期限”这一分支。后续方案若改变了图中任意一处依赖，原来的判断就要重新验证，不能仅凭界面相似或返回值相同沿用结论。

## 同月延伸

- [物联网安全研究：TLS 加密还需要验证对端身份](/tech/2019/08/05/iot-tls-server-identity/)
- [物联网设备身份：批量共用一个密码的问题](/tech/2019/08/15/iot-device-credential-lifecycle/)

## 参考资料

1. [MQTT 3.1.1 标准](https://docs.oasis-open.org/mqtt/mqtt/v3.1.1/os/mqtt-v3.1.1-os.html)
2. [Node-RED 0.19 发布记录](https://nodered.org/blog/2018/08/14/version-0-19-released)
