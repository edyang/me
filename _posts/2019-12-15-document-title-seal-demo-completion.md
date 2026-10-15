---
layout: post
title: 文档视觉小应用：从上传到标题、印章与复核结果
subtitle: 模型能画框之后，还要让用户找到原页、理解失败并保存确认结果，才能成为完整应用。
date: 2019-12-15 08:00:00 +0800
author: edyang
header-style: text
catalog: true
tags:
- 边缘计算
- 物联网视觉
tech_note: true
note_id: document-title-seal-demo-completion
permalink: /tech/2019/12/15/document-title-seal-demo-completion/
excerpt: 模型能画框之后，还要让用户找到原页、理解失败并保存确认结果，才能成为完整应用。
privacy_reviewed: true
content_revision: 3
images:
- /img/tech-notes/document-title-seal-demo-completion.svg
technology_since: '2018-05-06'
---

模型能画框之后，还要让用户找到原页、理解失败并保存确认结果，才能成为完整应用。

本文使用树莓派网关、独立视觉工作进程与合成业务事件。物联网与视觉结合后，数据采集、推理和业务动作有不同速率与可靠性。本文以可停止的演示链路研究状态归属，不把接口成功等同于物理动作完成。

## 1. 从现象推到机制

上传校验输入并生成任务，逐页预处理与检测，坐标还原后生成候选。标题 OCR 与印章定位分别保存，缺页和模型异常不能返回旧文件。人工确认结果关联原始输入和完整模型发布组合。

![文档视觉小应用：从上传到标题、印章与复核结果的处理、反馈与观察关系](/img/tech-notes/document-title-seal-demo-completion.svg)

图中的四个节点分别表示输入任务、逐页处理、候选复核、结果交付。顺着实线检查输入如何变成输出，再沿虚线核对反馈条件。图示表达的是本文讨论的关系，不是实测曲线或现场截图。

## 2. 最小实现与输入条件

先只支持合成单页图片，完成成功、无目标、失败与待复核四条路径，再扩展多页。输入格式范围清楚写在界面，不把未实现能力放进宣传。

```text
upload -> validated task identity
page processing -> detector and coordinate restoration
results -> title crop/OCR + seal candidates
review -> confirmed result linked to immutable raw output
download -> verified task-owned artifact
```

从单设备单图片开始，保存事件身份和所有输入输出。再逐项加入队列、重试和告警，检查重启后的归属与恢复；外部写入或控制需要明确规则与权限。

## 3. 用对照区分原因

下表列出需要主动改变的条件。预期行为来自机制分析，复现时还需记录运行环境和原始输出，不能将预期当作已经测得的结果。

| 改变的条件 | 需要验证的行为 |
| --- | --- |
| 页面没有目标 | 与推理失败采用不同结果 |
| 多页中一页处理失败 | 总任务要说明完整性 |
| 人工确认后再次下载 | 应获取已确认版本对应文件 |

### 对照 1：页面没有目标

与推理失败采用不同结果。观察时记录模型输出和进程状态。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 2：多页中一页处理失败

总任务要说明完整性。观察时记录每页状态与预期页数。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 3：人工确认后再次下载

应获取已确认版本对应文件。观察时记录结果版本与任务归属。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。

## 4. 适用条件与取舍

印章定位不包含真伪鉴定，OCR 也可能需要人工纠错。验收以明确输入范围和真实任务结果为准，不把框图效果替代完整流程。

一次正常运行只覆盖了这组输入。继续扩展前，应把上面的异常对照保留下来，尤其关注“人工确认后再次下载”这一分支。后续方案若改变了图中任意一处依赖，原来的判断就要重新验证，不能仅凭界面相似或返回值相同沿用结论。

## 同月延伸

- [物联网小系统：把采样、上报、趋势和告警串起来](/tech/2019/12/05/iot-environment-monitoring-demo/)
- [物联网与视觉研究复盘：把能力边界写进交付清单](/tech/2019/12/25/iot-vision-research-review-2019/)

## 参考资料

1. [MQTT 3.1.1](https://docs.oasis-open.org/mqtt/mqtt/v3.1.1/os/mqtt-v3.1.1-os.html)
2. [Darknet 2018 源码](https://github.com/pjreddie/darknet/tree/f6d861736038da22c9eb0739dca84003c5a5e275)
3. [Node-RED 0.19](https://nodered.org/blog/2018/08/14/version-0-19-released)
