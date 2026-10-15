---
layout: post
title: 物联网视觉联动：识别到了不代表动作完成
subtitle: 检测到目标后发出控制命令，整个流程至少有观察、决策、发送和执行反馈四个阶段。
date: 2019-11-25 08:00:00 +0800
author: edyang
header-style: text
catalog: true
tags:
- 边缘计算
- 物联网视觉
tech_note: true
note_id: iot-vision-command-result-boundary
permalink: /tech/2019/11/25/iot-vision-command-result-boundary/
excerpt: 检测到目标后发出控制命令，整个流程至少有观察、决策、发送和执行反馈四个阶段。
privacy_reviewed: true
content_revision: 3
images:
- /img/tech-notes/iot-vision-command-result-boundary.svg
technology_since: '2018-05-06'
---

检测到目标后发出控制命令，整个流程至少有观察、决策、发送和执行反馈四个阶段。

本文使用树莓派网关、独立视觉工作进程与合成业务事件。物联网与视觉结合后，数据采集、推理和业务动作有不同速率与可靠性。本文以可停止的演示链路研究状态归属，不把接口成功等同于物理动作完成。

## 1. 从现象推到机制

模型结果只是观测证据，规则结合权限与设备状态形成意图。命令发送成功不证明执行器完成动作，设备反馈也需要与当前事件关联。视觉误检、过期数据和重复命令都可能影响联动。

![物联网视觉联动：识别到了不代表动作完成的处理、反馈与观察关系](/img/tech-notes/iot-vision-command-result-boundary.svg)

图中的四个节点分别表示视觉证据、业务决策、命令发送、执行确认。顺着实线检查输入如何变成输出，再沿虚线核对反馈条件。图示表达的是本文讨论的关系，不是实测曲线或现场截图。

## 2. 最小实现与输入条件

先让识别结果只点亮模拟状态，再加入独立台架指示灯。全程保留事件与命令身份，超时进入待确认，不补造完成反馈。

```text
observation -> model result and source image
decision -> explicit rule and current device state
command -> stable identity and expiry
feedback -> accepted / executed / independently observed
```

从单设备单图片开始，保存事件身份和所有输入输出。再逐项加入队列、重试和告警，检查重启后的归属与恢复；外部写入或控制需要明确规则与权限。

## 3. 用对照区分原因

下表列出需要主动改变的条件。预期行为来自机制分析，复现时还需记录运行环境和原始输出，不能将预期当作已经测得的结果。

| 改变的条件 | 需要验证的行为 |
| --- | --- |
| 模型结果已经过期 | 规则不应继续触发实时动作 |
| 命令成功发送但无反馈 | 流程仍未确认执行完成 |
| 重复处理同一事件 | 不应重复产生一次性动作 |

### 对照 1：模型结果已经过期

规则不应继续触发实时动作。观察时记录结果采集时间与有效窗口。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 2：命令成功发送但无反馈

流程仍未确认执行完成。观察时记录发送结果与设备反馈。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 3：重复处理同一事件

不应重复产生一次性动作。观察时记录事件和命令幂等身份。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。

## 4. 适用条件与取舍

真实执行需要独立权限、人工停止和硬件约束。演示台架通过不能直接外推到工业设备或道路车辆控制。

一次正常运行只覆盖了这组输入。继续扩展前，应把上面的异常对照保留下来，尤其关注“重复处理同一事件”这一分支。后续方案若改变了图中任意一处依赖，原来的判断就要重新验证，不能仅凭界面相似或返回值相同沿用结论。

## 同月延伸

- [物联网与视觉融合：事件、图片和设备状态如何对齐](/tech/2019/11/05/iot-vision-event-correlation/)
- [边缘视觉队列：图像处理慢时不要无限堆内存](/tech/2019/11/15/edge-queue-backpressure-images/)

## 参考资料

1. [MQTT 3.1.1](https://docs.oasis-open.org/mqtt/mqtt/v3.1.1/os/mqtt-v3.1.1-os.html)
2. [Darknet 2018 源码](https://github.com/pjreddie/darknet/tree/f6d861736038da22c9eb0739dca84003c5a5e275)
3. [Node-RED 0.19](https://nodered.org/blog/2018/08/14/version-0-19-released)
