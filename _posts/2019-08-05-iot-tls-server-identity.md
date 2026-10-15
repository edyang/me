---
layout: post
title: 物联网安全研究：TLS 加密还需要验证对端身份
subtitle: 连接启用了 TLS，却关闭证书校验，仍然不能确认连接到的是预期服务。
date: 2019-08-05 08:00:00 +0800
author: edyang
header-style: text
catalog: true
tags:
- 物联网
- 可靠性
tech_note: true
note_id: iot-tls-server-identity
permalink: /tech/2019/08/05/iot-tls-server-identity/
excerpt: 连接启用了 TLS，却关闭证书校验，仍然不能确认连接到的是预期服务。
privacy_reviewed: true
content_revision: 3
images:
- /img/tech-notes/iot-tls-server-identity.svg
technology_since: '2018-08-14'
---

连接启用了 TLS，却关闭证书校验，仍然不能确认连接到的是预期服务。

本文使用MQTT 3.1.1、Node-RED 0.19 与虚构设备消息。从能通信走向稳定运行，需要对离线、重复、乱序和恢复建立明确语义。本文使用演示身份和事件，不连接真实控制负载，也没有声称取得未经记录的现场效果。

## 1. 从现象推到机制

TLS（传输层安全）同时涉及加密与身份验证。信任链、主机名和时间影响证书判断，设备时间错误可能导致校验失败。解决方向是修复时间与信任配置，而不是永久跳过验证。

![物联网安全研究：TLS 加密还需要验证对端身份的处理、反馈与观察关系](/img/tech-notes/iot-tls-server-identity.svg)

图中的四个节点分别表示网络连接、证书链、主机身份、应用认证。顺着实线检查输入如何变成输出，再沿虚线核对反馈条件。图示表达的是本文讨论的关系，不是实测曲线或现场截图。

## 2. 最小实现与输入条件

用演示服务比较正确证书、错误主机名与不可信证书。私钥不进入源码，错误信息应能区分网络和身份问题。

```text
connect -> validate trusted certificate chain
verify hostname -> expected server identity
check device time -> certificate validity window
only then -> authenticate application session
```

保留设备、网关和服务端各自时间与状态，按固定故障顺序复现。每次恢复后检查数据归属和未完成工作，不只观察连接图标重新变绿。

## 3. 用对照区分原因

下表列出需要主动改变的条件。预期行为来自机制分析，复现时还需记录运行环境和原始输出，不能将预期当作已经测得的结果。

| 改变的条件 | 需要验证的行为 |
| --- | --- |
| 网络可达但证书不可信 | 连接应按策略失败 |
| 主机名与证书不一致 | 不能因加密已建立就忽略 |
| 设备时间明显错误 | 先修复可靠时间来源 |

### 对照 1：网络可达但证书不可信

连接应按策略失败。观察时记录证书链与信任根。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 2：主机名与证书不一致

不能因加密已建立就忽略。观察时记录请求主机名与证书身份。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 3：设备时间明显错误

先修复可靠时间来源。观察时记录本机时间与证书有效期。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。

## 4. 适用条件与取舍

证书和凭据需要更新计划。长期离线设备的过期与恢复策略应提前验证，不能等批量失联再临时关闭安全检查。

一次正常运行只覆盖了这组输入。继续扩展前，应把上面的异常对照保留下来，尤其关注“设备时间明显错误”这一分支。后续方案若改变了图中任意一处依赖，原来的判断就要重新验证，不能仅凭界面相似或返回值相同沿用结论。

## 同月延伸

- [物联网设备身份：批量共用一个密码的问题](/tech/2019/08/15/iot-device-credential-lifecycle/)
- [物联网命令：谁能控制、控制了什么要可追溯](/tech/2019/08/25/iot-command-authorization-audit/)

## 参考资料

1. [MQTT 3.1.1 标准](https://docs.oasis-open.org/mqtt/mqtt/v3.1.1/os/mqtt-v3.1.1-os.html)
2. [Node-RED 0.19 发布记录](https://nodered.org/blog/2018/08/14/version-0-19-released)
