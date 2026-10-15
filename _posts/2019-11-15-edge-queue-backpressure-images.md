---
layout: post
title: 边缘视觉队列：图像处理慢时不要无限堆内存
subtitle: 相机持续采图，推理速度跟不上时，队列会把有限内存吃完。
date: 2019-11-15 08:00:00 +0800
author: edyang
header-style: text
catalog: true
tags:
- 边缘计算
- 物联网视觉
tech_note: true
note_id: edge-queue-backpressure-images
permalink: /tech/2019/11/15/edge-queue-backpressure-images/
excerpt: 相机持续采图，推理速度跟不上时，队列会把有限内存吃完。
privacy_reviewed: true
content_revision: 3
images:
- /img/tech-notes/edge-queue-backpressure-images.svg
technology_since: '2018-05-06'
---

相机持续采图，推理速度跟不上时，队列会把有限内存吃完。必须先确定业务能丢什么。

本文使用树莓派网关、独立视觉工作进程与合成业务事件。物联网与视觉结合后，数据采集、推理和业务动作有不同速率与可靠性。本文以可停止的演示链路研究状态归属，不把接口成功等同于物理动作完成。

## 1. 从现象推到机制

实时预览可能允许保留最新帧，逐件检测则不能静默丢掉已承诺事件。两种业务应使用不同队列策略。排队还增加结果年龄，即使每张最后都处理，也可能错过实时动作窗口。

![边缘视觉队列：图像处理慢时不要无限堆内存的处理、反馈与观察关系](/img/tech-notes/edge-queue-backpressure-images.svg)

图中的四个节点分别表示业务承诺、有限队列、过载动作、结果核对。顺着实线检查输入如何变成输出，再沿虚线核对反馈条件。图示表达的是本文讨论的关系，不是实测曲线或现场截图。

## 2. 最小实现与输入条件

用合成帧号模拟生产快于消费，记录队列长度和最老事件年龄。满载时明确拒绝、减速或丢弃策略，并保留计数。

```text
preview -> bounded latest-frame policy
committed inspection -> durable event queue or upstream backpressure
measure -> queue length, age, dropped, rejected
result -> event identity and freshness
```

从单设备单图片开始，保存事件身份和所有输入输出。再逐项加入队列、重试和告警，检查重启后的归属与恢复；外部写入或控制需要明确规则与权限。

## 3. 用对照区分原因

下表列出需要主动改变的条件。预期行为来自机制分析，复现时还需记录运行环境和原始输出，不能将预期当作已经测得的结果。

| 改变的条件 | 需要验证的行为 |
| --- | --- |
| 预览帧允许跳过 | 可优先处理最新画面 |
| 逐件事件必须有结果 | 不能套用静默覆盖策略 |
| 队列长度有限但等待太久 | 还需按截止时间处理过期工作 |

### 对照 1：预览帧允许跳过

可优先处理最新画面。观察时记录丢帧计数与结果年龄。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 2：逐件事件必须有结果

不能套用静默覆盖策略。观察时记录已受理事件与完成记录。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 3：队列长度有限但等待太久

还需按截止时间处理过期工作。观察时记录最老事件年龄与业务窗口。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。

## 4. 适用条件与取舍

队列是容量缓冲，不创造推理能力。长期过载需要降低输入、扩展处理或调整需求，不能只继续扩大队列。

一次正常运行只覆盖了这组输入。继续扩展前，应把上面的异常对照保留下来，尤其关注“队列长度有限但等待太久”这一分支。后续方案若改变了图中任意一处依赖，原来的判断就要重新验证，不能仅凭界面相似或返回值相同沿用结论。

## 同月延伸

- [物联网与视觉融合：事件、图片和设备状态如何对齐](/tech/2019/11/05/iot-vision-event-correlation/)
- [物联网视觉联动：识别到了不代表动作完成](/tech/2019/11/25/iot-vision-command-result-boundary/)

## 参考资料

1. [MQTT 3.1.1](https://docs.oasis-open.org/mqtt/mqtt/v3.1.1/os/mqtt-v3.1.1-os.html)
2. [Darknet 2018 源码](https://github.com/pjreddie/darknet/tree/f6d861736038da22c9eb0739dca84003c5a5e275)
3. [Node-RED 0.19](https://nodered.org/blog/2018/08/14/version-0-19-released)
