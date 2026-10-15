---
layout: post
title: 物联网设备身份：批量共用一个密码的问题
subtitle: 所有设备使用同一凭据，一台泄露就可能影响整个群体。
date: 2019-08-15 08:00:00 +0800
author: edyang
header-style: text
catalog: true
tags:
- 物联网
- 可靠性
tech_note: true
note_id: iot-device-credential-lifecycle
permalink: /tech/2019/08/15/iot-device-credential-lifecycle/
excerpt: 所有设备使用同一凭据，一台泄露就可能影响整个群体。
privacy_reviewed: true
content_revision: 3
images:
- /img/tech-notes/iot-device-credential-lifecycle.svg
technology_since: '2018-08-14'
---

所有设备使用同一凭据，一台泄露就可能影响整个群体。身份需要能独立撤销与追踪。

本文使用MQTT 3.1.1、Node-RED 0.19 与虚构设备消息。从能通信走向稳定运行，需要对离线、重复、乱序和恢复建立明确语义。本文使用演示身份和事件，不连接真实控制负载，也没有声称取得未经记录的现场效果。

## 1. 从现象推到机制

设备身份、安装位置和业务归属不应完全混为一体。独立凭据允许按设备限制主题与权限，轮换时还需保留过渡与失败恢复。退役设备应撤销访问，而不是只从界面隐藏。

![物联网设备身份：批量共用一个密码的问题的处理、反馈与观察关系](/img/tech-notes/iot-device-credential-lifecycle.svg)

图中的四个节点分别表示设备登记、独立凭据、权限校验、轮换退役。顺着实线检查输入如何变成输出，再沿虚线核对反馈条件。图示表达的是本文讨论的关系，不是实测曲线或现场截图。

## 2. 最小实现与输入条件

建立虚构设备登记表，记录身份状态和凭据版本，不记录明文秘密。使用代理权限验证一台设备无法访问另一台主题。

```text
device identity -> independent credential
permissions -> own topics and allowed actions
rotation -> new version, verified cutover, old revocation
retirement -> revoke access and clean retained state
```

保留设备、网关和服务端各自时间与状态，按固定故障顺序复现。每次恢复后检查数据归属和未完成工作，不只观察连接图标重新变绿。

## 3. 用对照区分原因

下表列出需要主动改变的条件。预期行为来自机制分析，复现时还需记录运行环境和原始输出，不能将预期当作已经测得的结果。

| 改变的条件 | 需要验证的行为 |
| --- | --- |
| 设备尝试访问他人主题 | 应由服务端权限拒绝 |
| 凭据轮换后设备未更新 | 需有可恢复的过渡流程 |
| 设备已经退役 | 访问能力应被正式撤销 |

### 对照 1：设备尝试访问他人主题

应由服务端权限拒绝。观察时记录实际认证身份与 ACL。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 2：凭据轮换后设备未更新

需有可恢复的过渡流程。观察时记录版本与最后成功连接。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 3：设备已经退役

访问能力应被正式撤销。观察时记录服务端身份状态与旧连接。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。

## 4. 适用条件与取舍

序列号可用于识别，不应单独作为秘密。出厂和现场配置也要控制日志与备份，避免凭据在批量脚本中公开。

一次正常运行只覆盖了这组输入。继续扩展前，应把上面的异常对照保留下来，尤其关注“设备已经退役”这一分支。后续方案若改变了图中任意一处依赖，原来的判断就要重新验证，不能仅凭界面相似或返回值相同沿用结论。

## 同月延伸

- [物联网安全研究：TLS 加密还需要验证对端身份](/tech/2019/08/05/iot-tls-server-identity/)
- [物联网命令：谁能控制、控制了什么要可追溯](/tech/2019/08/25/iot-command-authorization-audit/)

## 参考资料

1. [MQTT 3.1.1 标准](https://docs.oasis-open.org/mqtt/mqtt/v3.1.1/os/mqtt-v3.1.1-os.html)
2. [Node-RED 0.19 发布记录](https://nodered.org/blog/2018/08/14/version-0-19-released)
