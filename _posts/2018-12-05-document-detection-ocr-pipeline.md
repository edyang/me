---
layout: post
title: 文档应用：标题定位、裁剪与 OCR 怎样衔接
subtitle: 标题检测框可以减少 OCR 输入范围，但缩放和坐标还原错误会让裁剪漏字。
date: 2018-12-05 08:00:00 +0800
author: edyang
header-style: text
catalog: true
tags:
- 文档检测
- 数据集
tech_note: true
note_id: document-detection-ocr-pipeline
permalink: /tech/2018/12/05/document-detection-ocr-pipeline/
excerpt: 标题检测框可以减少 OCR 输入范围，但缩放和坐标还原错误会让裁剪漏字。
privacy_reviewed: true
content_revision: 3
images:
- /img/tech-notes/document-detection-ocr-pipeline.svg
technology_since: '2018-05-06'
---

标题检测框可以减少 OCR 输入范围，但缩放和坐标还原错误会让裁剪漏字。

本文使用合成文档图、YOLO 标注格式与 OpenCV 3.4。文档标题与印章定位先是数据定义问题，再是模型问题。框代表什么、哪些情况不标以及如何处理多页，都会改变训练目标和评估含义。

## 1. 从现象推到机制

检测器输入可能经过缩放与补边，输出需还原到原图坐标，再按边界约定裁剪。OCR（光学字符识别）给出文本及其不确定性，不应把模型类别 title 直接当作标题内容。

![文档应用：标题定位、裁剪与 OCR 怎样衔接的处理、反馈与观察关系](/img/tech-notes/document-detection-ocr-pipeline.svg)

图中的四个节点分别表示原图输入、模型坐标、逆向裁剪、文字结果。顺着实线检查输入如何变成输出，再沿虚线核对反馈条件。图示表达的是本文讨论的关系，不是实测曲线或现场截图。

## 2. 最小实现与输入条件

保存原图尺寸、缩放比例和补边偏移，用合成标尺图验证坐标链。裁剪略扩边时仍需限制图像边界，避免负坐标。

```text
original -> resize / pad -> detector
box -> inverse transform -> original coordinates
crop -> OCR -> text with review status
store source page and processing versions
```

先建立少量人工可复核的合成样本，保留原图、标注和处理版本。按文档来源或模板拆分集合，禁止同一原件的不同裁剪分别进入训练与测试形成泄漏。

## 3. 用对照区分原因

下表列出需要主动改变的条件。预期行为来自机制分析，复现时还需记录运行环境和原始输出，不能将预期当作已经测得的结果。

| 改变的条件 | 需要验证的行为 |
| --- | --- |
| 输入做过等比例补边 | 还原时必须扣除偏移 |
| 标题框贴近图像边缘 | 裁剪需要限制有效边界 |
| OCR 返回空文本 | 不能仍显示识别成功 |

### 对照 1：输入做过等比例补边

还原时必须扣除偏移。观察时记录缩放与补边的真实参数。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 2：标题框贴近图像边缘

裁剪需要限制有效边界。观察时记录最终像素范围。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 3：OCR 返回空文本

不能仍显示识别成功。观察时记录定位成功与转录结果分开。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。

## 4. 适用条件与取舍

检测与 OCR 错误会串联，评估应分别测量再看端到端任务。只报告检测召回率，无法说明标题文本提取是否可用。

一次正常运行只覆盖了这组输入。继续扩展前，应把上面的异常对照保留下来，尤其关注“OCR 返回空文本”这一分支。后续方案若改变了图中任意一处依赖，原来的判断就要重新验证，不能仅凭界面相似或返回值相同沿用结论。

## 同月延伸

- [Darknet 应用服务：输入、任务状态与结果文件](/tech/2018/12/15/darknet-document-api-contract/)
- [视觉模型交付：权重、阈值和数据口径一起版本化](/tech/2018/12/25/vision-model-release-record/)

## 参考资料

1. [YOLOv3 训练资料](https://pjreddie.com/darknet/yolo/)
2. [OpenCV 3.4.0 文档](https://docs.opencv.org/3.4.0/)
