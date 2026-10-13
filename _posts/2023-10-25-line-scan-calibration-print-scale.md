---
layout: post
title: 线扫标定板：排查打印尺寸与采样比例
subtitle: 为了判断线扫图像清晰度，我制作可打印并卷成圆筒的测试图，实体上 100mm 校验线却只有约 96mm。
date: 2023-10-25 08:00:00 +0800
author: edyang
header-style: text
catalog: true
tags:
- 工业相机
- 标定
- 打印
tech_note: true
note_id: line-scan-calibration-print-scale
source_date: '2026-10-08'
source_dates:
- '2026-10-08'
published_at: '2026-10-12T12:51:43+08:00'
updated_at: '2026-10-13T17:59:15+08:00'
verification: observed
privacy_reviewed: true
permalink: /tech/2026/10/08/line-scan-calibration-print-scale/
excerpt: 为了判断线扫图像清晰度，我制作可打印并卷成圆筒的测试图，实体上 100mm 校验线却只有约 96mm。
archive_date: '2023-10-25'
date_basis: simulated_weekly_archive
content_revision: 2
images:
- /img/tech-notes/line-scan-calibration-print-scale.svg
---

为了判断线扫图像清晰度，我制作可打印并卷成圆筒的测试图，实体上 100mm 校验线却只有约 96mm。这时首先要确认打印链路，否则拿错误尺寸的目标标定相机，会把缩放误差带入后续结论。

## 研究与排查过程

研究先对照 PDF 页面尺寸与打印驱动选项，检查是否使用适合页面或自动缩小。拟按实际大小打印，并分别量水平和垂直校验线。100 到 96 对应该尺段约 0.96 的比例，但不能直接证明两个方向都一样，更不能跳过设置排查永久放大所有图纸。

![线扫标定板：排查打印尺寸与采样比例研究路径示意](/img/tech-notes/line-scan-calibration-print-scale.svg)

## 涉及的技术与取舍

技术涉及矢量物理尺寸、打印缩放和线扫相对运动。单线相机在静止状态只获得一条线，圆筒转动或目标平移才形成二维展开；运动方向采样密度由速度与行频决定。顺序应是验证实体尺寸、固定运动采样，再测像素比例与边缘清晰度，保留打印和采集设置。

清晰度测试可以同时保留不同方向的边缘和细条纹，观察传感器横向与运动展开方向是否有不同模糊。若实体尺寸准确而展开比例不对，再检查行频与速度；若两向打印尺段已不准确，则先回到打印链路。

## 这轮研究的结论

已有记录确认打印缩小，未提供设置修正后的实测。结论是标定目标也需要先校验，不能把全部比例异常算给相机。后续需同时保存 PDF、打印设置、实体尺寸与图像，才能判断问题发生在哪一步。
