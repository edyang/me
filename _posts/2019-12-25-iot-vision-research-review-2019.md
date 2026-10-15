---
layout: post
title: 物联网与视觉研究复盘：把能力边界写进交付清单
subtitle: 研究成果如果只剩演示视频，下一次接手很难知道环境、输入和失败条件。
date: 2019-12-25 08:00:00 +0800
author: edyang
header-style: text
catalog: true
tags:
- 边缘计算
- 物联网视觉
tech_note: true
note_id: iot-vision-research-review-2019
permalink: /tech/2019/12/25/iot-vision-research-review-2019/
excerpt: 研究成果如果只剩演示视频，下一次接手很难知道环境、输入和失败条件。
privacy_reviewed: true
content_revision: 3
images:
- /img/tech-notes/iot-vision-research-review-2019.svg
technology_since: '2018-05-06'
---

研究成果如果只剩演示视频，下一次接手很难知道环境、输入和失败条件。交付需要可复核材料。

本文使用树莓派网关、独立视觉工作进程与合成业务事件。物联网与视觉结合后，数据采集、推理和业务动作有不同速率与可靠性。本文以可停止的演示链路研究状态归属，不把接口成功等同于物理动作完成。

## 1. 从现象推到机制

按采集、通信、数据、模型、规则和执行分别描述能力。每项写明支持条件、已验证证据和未覆盖情况。计划、理论预期与实际结果分开，避免把“可以继续研究”写成“已经稳定交付”。

![物联网与视觉研究复盘：把能力边界写进交付清单的处理、反馈与观察关系](/img/tech-notes/iot-vision-research-review-2019.svg)

图中的四个节点分别表示能力范围、实现版本、实际证据、下一轮。顺着实线检查输入如何变成输出，再沿虚线核对反馈条件。图示表达的是本文讨论的关系，不是实测曲线或现场截图。

## 2. 最小实现与输入条件

为环境监测与文档检测演示各建一份清单，记录程序、固件、模型、配置、测试输入和恢复方法。未知指标保留待验证，不填估计成绩。

```text
capability -> supported inputs and constraints
implementation -> exact program / firmware / model bundle
evidence -> actual logs and reproducible fixtures
limitations -> unsupported and unverified cases
operation -> start, monitor, recover, stop
```

从单设备单图片开始，保存事件身份和所有输入输出。再逐项加入队列、重试和告警，检查重启后的归属与恢复；外部写入或控制需要明确规则与权限。

## 3. 用对照区分原因

下表列出需要主动改变的条件。预期行为来自机制分析，复现时还需记录运行环境和原始输出，不能将预期当作已经测得的结果。

| 改变的条件 | 需要验证的行为 |
| --- | --- |
| 只有模型权重没有配置 | 无法完整复现识别行为 |
| 流程正常但故障恢复未测 | 不能宣称稳定无损运行 |
| 目标指标尚无实际数据 | 保留为计划而非结果 |

### 对照 1：只有模型权重没有配置

无法完整复现识别行为。观察时记录模型发布组合是否齐全。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 2：流程正常但故障恢复未测

不能宣称稳定无损运行。观察时记录断网重启和恢复证据。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 3：目标指标尚无实际数据

保留为计划而非结果。观察时记录陈述类别与可核对来源。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。

## 4. 适用条件与取舍

清单的作用是让下一轮研究有确定起点。优先处理真实任务中的最大缺口，不用技术名词数量代替成熟度判断。

一次正常运行只覆盖了这组输入。继续扩展前，应把上面的异常对照保留下来，尤其关注“目标指标尚无实际数据”这一分支。后续方案若改变了图中任意一处依赖，原来的判断就要重新验证，不能仅凭界面相似或返回值相同沿用结论。

## 同月延伸

- [物联网小系统：把采样、上报、趋势和告警串起来](/tech/2019/12/05/iot-environment-monitoring-demo/)
- [文档视觉小应用：从上传到标题、印章与复核结果](/tech/2019/12/15/document-title-seal-demo-completion/)

## 参考资料

1. [MQTT 3.1.1](https://docs.oasis-open.org/mqtt/mqtt/v3.1.1/os/mqtt-v3.1.1-os.html)
2. [Darknet 2018 源码](https://github.com/pjreddie/darknet/tree/f6d861736038da22c9eb0739dca84003c5a5e275)
3. [Node-RED 0.19](https://nodered.org/blog/2018/08/14/version-0-19-released)
