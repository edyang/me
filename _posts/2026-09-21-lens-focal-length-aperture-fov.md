---
layout: post
title: 工业镜头选型：焦距、光圈和工作距离分别决定什么
subtitle: 焦距更大并不等于视野更宽；光圈也不是镜头覆盖范围的直接指标。
date: 2026-09-21 08:00:00 +0800
author: edyang
header-style: text
catalog: true
tags:
- 工业相机
- 光学
tech_note: true
note_id: lens-focal-length-aperture-fov
source_date: '2026-09-21'
source_dates:
- '2026-09-21'
- '2026-10-08'
published_at: '2026-10-12T12:51:43+08:00'
updated_at: '2026-10-12T12:51:43+08:00'
verification: notes
privacy_reviewed: true
permalink: /tech/2026/09/21/lens-focal-length-aperture-fov/
excerpt: 焦距更大并不等于视野更宽；光圈也不是镜头覆盖范围的直接指标。
---

镜头参数里经常同时出现焦距和 F 值，但它们回答不同问题。能否拍下目标宽度，主要需要先看传感器尺寸、工作距离和焦距；光圈主要参与曝光、景深和成像质量的取舍。

## 先估算视野，再查实际镜头条件

对近似薄透镜模型，如果物距从主平面量起，可以用 `FOV ≈ sensor_width × (distance - focal_length) / focal_length` 做初步估算。物距远大于焦距时，常简化为传感器宽度乘以距离再除以焦距。

工业镜头标注的工作距离通常有自己的测量基准；广角、近距离和复杂镜组也会偏离简化模型。因此估算后必须核对厂家视野资料、最近对焦距离、像圈和接口，并用实际目标测试。

## F 值与清晰范围

F 值约等于焦距除以入瞳直径。F 值越大，光圈通常越小，进光减少，景深一般增加；但继续收小可能受到衍射和曝光时间限制。旋转物体若曝光变长，还可能产生运动模糊。

## 两个旋钮分别验证

手动镜头通常有调焦与光圈控制。先在固定距离对焦，再比较不同光圈下的中心、边缘和不同深度位置。不要一边移动相机、一边改光圈，最后只留下一个“看起来清楚”的结果。

原交流包含选型讨论，没有统一镜头方案的现场验收。本文保留通用原理；实际可检出的缺陷尺寸仍应通过目标成像和检测试验确认。

## 参考资料

- [Edmund Optics 视野与焦距](https://www.edmundoptics.com/knowledge-center/application-notes/imaging/understanding-focal-length-and-field-of-view/)
