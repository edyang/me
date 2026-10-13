---
layout: post
title: 相机窄条拼接：研究颜色转换与处理吞吐
subtitle: 在特定运动条件下，面阵相机截取窄条也能拼出展开图。
date: 2023-07-05 08:00:00 +0800
author: edyang
header-style: text
catalog: true
tags:
- 工业相机
- OpenCV
- 性能优化
tech_note: true
note_id: bayer-strip-panorama-pipeline
source_date: '2026-08-19'
source_dates:
- '2026-08-19'
published_at: '2026-10-12T12:51:43+08:00'
updated_at: '2026-10-13T17:59:15+08:00'
verification: partial
privacy_reviewed: true
permalink: /tech/2026/08/19/bayer-strip-panorama-pipeline/
excerpt: 在特定运动条件下，面阵相机截取窄条也能拼出展开图。
archive_date: '2023-07-05'
date_basis: simulated_weekly_archive
content_revision: 2
images:
- /img/tech-notes/bayer-strip-panorama-pipeline.svg
---

在特定运动条件下，面阵相机截取窄条也能拼出展开图。实际讨论却遇到红蓝反转和处理速度跟不上采集，因此我把问题分成像素格式、处理节奏和运动同步三个部分。

## 研究与排查过程

先对照相机 Bayer 排列、SDK 输出、OpenCV 去马赛克以及显示组件的 RGB/BGR 约定，用已知红绿蓝色块检查颜色链。再记录每帧时间戳与处理耗时，看是否超过采集间隔。如果积压持续增长，单纯加大队列只会增加延迟和内存，不能提高处理能力。

![相机窄条拼接：研究颜色转换与处理吞吐研究路径示意](/img/tech-notes/bayer-strip-panorama-pipeline.svg)

## 涉及的技术与取舍

技术方案涉及颜色转换、裁条、有限队列与受控采样。根据应用要求选择跳过或排队，并分别记录接收、处理、主动跳过和异常丢弃。几何拼接还需要条宽、速度、帧率与曝光配合；出现重复纹理、缺口或拉伸时，结合有效位移判断是否需要编码器同步。

### 辅助检查示例

以下为通用示例，用于理解上述检查；变量、设备和参数需对应实际环境。

```text
相机原始格式 → 去马赛克 → 内部颜色约定 → 裁条 → 拼接 → 显示/保存
```

## 这轮研究的结论

记录确认了颜色和吞吐现象，没有最终稳定运行验收。结论是正确的展开图来自颜色、时间和位移同时一致。后续应保存原始帧、转换结果、队列统计与拼图，逐层证明改动有效，而不能只看某一次拼接预览。

## 参考资料

- [OpenCV 颜色转换](https://docs.opencv.org/4.x/d8/d01/group__imgproc__color__conversions.html)
