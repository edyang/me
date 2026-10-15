---
layout: post
title: 边缘视觉部署：先算内存、温度和并发预算
subtitle: 模型在开发机能跑，不代表小型边缘设备能同时承担采集、推理和界面。
date: 2019-09-05 08:00:00 +0800
author: edyang
header-style: text
catalog: true
tags:
- 边缘计算
- 物联网视觉
tech_note: true
note_id: edge-inference-resource-budget
permalink: /tech/2019/09/05/edge-inference-resource-budget/
excerpt: 模型在开发机能跑，不代表小型边缘设备能同时承担采集、推理和界面。
privacy_reviewed: true
content_revision: 3
images:
- /img/tech-notes/edge-inference-resource-budget.svg
technology_since: '2018-05-06'
---

模型在开发机能跑，不代表小型边缘设备能同时承担采集、推理和界面。

本文使用树莓派网关、独立视觉工作进程与合成业务事件。物联网与视觉结合后，数据采集、推理和业务动作有不同速率与可靠性。本文以可停止的演示链路研究状态归属，不把接口成功等同于物理动作完成。

## 1. 从现象推到机制

模型权重只是内存的一部分，输入缓冲、中间特征、解码和并发任务都会增加峰值。持续负载还受散热和供电影响。平均内存正常不代表首个请求或批处理峰值安全。

![边缘视觉部署：先算内存、温度和并发预算的处理、反馈与观察关系](/img/tech-notes/edge-inference-resource-budget.svg)

图中的四个节点分别表示目标设备、单任务基线、有限并发、发布条件。顺着实线检查输入如何变成输出，再沿虚线核对反馈条件。图示表达的是本文讨论的关系，不是实测曲线或现场截图。

## 2. 最小实现与输入条件

按单任务测量加载、首次推理与稳定推理，再加入并发。输入分辨率与队列上限作为发布条件，避免未验证的大图直接进入。

```text
memory budget = model + intermediate + input/output + runtime
load -> first inference -> steady state
then bounded concurrency
record temperature, memory peak, latency and failures
```

从单设备单图片开始，保存事件身份和所有输入输出。再逐项加入队列、重试和告警，检查重启后的归属与恢复；外部写入或控制需要明确规则与权限。

## 3. 用对照区分原因

下表列出需要主动改变的条件。预期行为来自机制分析，复现时还需记录运行环境和原始输出，不能将预期当作已经测得的结果。

| 改变的条件 | 需要验证的行为 |
| --- | --- |
| 只统计权重文件大小 | 会遗漏大量运行时占用 |
| 持续运行后变慢 | 可能涉及温度或资源积累 |
| 并发翻倍导致内存不足 | 需要有限任务容量 |

### 对照 1：只统计权重文件大小

会遗漏大量运行时占用。观察时记录进程峰值与中间缓冲。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 2：持续运行后变慢

可能涉及温度或资源积累。观察时记录温度频率与延迟趋势。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 3：并发翻倍导致内存不足

需要有限任务容量。观察时记录各阶段峰值和队列上限。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。

## 4. 适用条件与取舍

不同硬件性能不能仅靠参数量换算。部署结论必须带具体设备、模型、分辨率和计时范围，不给未经测试的帧率。

一次正常运行只覆盖了这组输入。继续扩展前，应把上面的异常对照保留下来，尤其关注“并发翻倍导致内存不足”这一分支。后续方案若改变了图中任意一处依赖，原来的判断就要重新验证，不能仅凭界面相似或返回值相同沿用结论。

## 同月延伸

- [视觉服务性能：解码、预处理和推理分别计时](/tech/2019/09/15/vision-latency-stage-measurement/)
- [物联网告警：触发、持续、恢复要有完整状态](/tech/2019/09/25/iot-alert-dedup-clear/)

## 参考资料

1. [MQTT 3.1.1](https://docs.oasis-open.org/mqtt/mqtt/v3.1.1/os/mqtt-v3.1.1-os.html)
2. [Darknet 2018 源码](https://github.com/pjreddie/darknet/tree/f6d861736038da22c9eb0739dca84003c5a5e275)
3. [Node-RED 0.19](https://nodered.org/blog/2018/08/14/version-0-19-released)
