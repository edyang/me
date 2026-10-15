---
layout: post
title: 物联网与视觉融合：事件、图片和设备状态如何对齐
subtitle: 一张图和一条传感器消息时间接近，不足以证明它们来自同一次业务事件。
date: 2019-11-05 08:00:00 +0800
author: edyang
header-style: text
catalog: true
tags:
- 边缘计算
- 物联网视觉
tech_note: true
note_id: iot-vision-event-correlation
permalink: /tech/2019/11/05/iot-vision-event-correlation/
excerpt: 一张图和一条传感器消息时间接近，不足以证明它们来自同一次业务事件。
privacy_reviewed: true
content_revision: 3
images:
- /img/tech-notes/iot-vision-event-correlation.svg
technology_since: '2018-05-06'
---

一张图和一条传感器消息时间接近，不足以证明它们来自同一次业务事件。

本文使用树莓派网关、独立视觉工作进程与合成业务事件。物联网与视觉结合后，数据采集、推理和业务动作有不同速率与可靠性。本文以可停止的演示链路研究状态归属，不把接口成功等同于物理动作完成。

## 1. 从现象推到机制

触发事件应有稳定身份，图片保存触发编号、采集设备与时间质量。仅靠跨设备墙上时间关联会受时钟偏差影响，必要时使用控制流程传递身份。一个事件多张图和重拍也应有明确顺序。

![物联网与视觉融合：事件、图片和设备状态如何对齐的处理、反馈与观察关系](/img/tech-notes/iot-vision-event-correlation.svg)

图中的四个节点分别表示触发事件、采集请求、视觉结果、完整报告。顺着实线检查输入如何变成输出，再沿虚线核对反馈条件。图示表达的是本文讨论的关系，不是实测曲线或现场截图。

## 2. 最小实现与输入条件

先模拟一次触发对应两张图片，再故意让第二张延迟。结果按事件归并，不按文件名或到达顺序猜测。

```text
event_id -> sensor trigger
capture_request -> same event_id
image -> event_id, camera_id, sequence, captured_at
inference_result -> event_id + image identity
report -> completeness per expected inputs
```

从单设备单图片开始，保存事件身份和所有输入输出。再逐项加入队列、重试和告警，检查重启后的归属与恢复；外部写入或控制需要明确规则与权限。

## 3. 用对照区分原因

下表列出需要主动改变的条件。预期行为来自机制分析，复现时还需记录运行环境和原始输出，不能将预期当作已经测得的结果。

| 改变的条件 | 需要验证的行为 |
| --- | --- |
| 图片晚于下一事件到达 | 仍应归属原触发事件 |
| 一个事件缺少预期图片 | 报告应显示不完整 |
| 两台设备时钟有偏差 | 不能仅凭毫秒时间硬配对 |

### 对照 1：图片晚于下一事件到达

仍应归属原触发事件。观察时记录显式事件号与图片身份。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 2：一个事件缺少预期图片

报告应显示不完整。观察时记录预期数量与实际输入。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 3：两台设备时钟有偏差

不能仅凭毫秒时间硬配对。观察时记录时间质量与流程身份。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。

## 4. 适用条件与取舍

关联正确不代表模型结果正确，两层需要独立验收。事件超时后迟到图片怎么处理，也应有明确规则。

一次正常运行只覆盖了这组输入。继续扩展前，应把上面的异常对照保留下来，尤其关注“两台设备时钟有偏差”这一分支。后续方案若改变了图中任意一处依赖，原来的判断就要重新验证，不能仅凭界面相似或返回值相同沿用结论。

## 同月延伸

- [边缘视觉队列：图像处理慢时不要无限堆内存](/tech/2019/11/15/edge-queue-backpressure-images/)
- [物联网视觉联动：识别到了不代表动作完成](/tech/2019/11/25/iot-vision-command-result-boundary/)

## 参考资料

1. [MQTT 3.1.1](https://docs.oasis-open.org/mqtt/mqtt/v3.1.1/os/mqtt-v3.1.1-os.html)
2. [Darknet 2018 源码](https://github.com/pjreddie/darknet/tree/f6d861736038da22c9eb0739dca84003c5a5e275)
3. [Node-RED 0.19](https://nodered.org/blog/2018/08/14/version-0-19-released)
