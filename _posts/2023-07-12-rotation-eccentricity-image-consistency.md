---
layout: post
title: 转台偏心对视觉检测的影响研究
subtitle: 物体旋转时中心稍有偏移，图像既可能变形，也可能改变亮度。
date: 2023-07-12 08:00:00 +0800
author: edyang
header-style: text
catalog: true
tags:
- 视觉检测
- 机械
- 成像
tech_note: true
note_id: rotation-eccentricity-image-consistency
source_date: '2026-08-19'
source_dates:
- '2026-08-19'
published_at: '2026-10-12T12:51:43+08:00'
updated_at: '2026-10-13T17:59:15+08:00'
verification: notes
privacy_reviewed: true
permalink: /tech/2026/08/19/rotation-eccentricity-image-consistency/
excerpt: 物体旋转时中心稍有偏移，图像既可能变形，也可能改变亮度。
archive_date: '2023-07-12'
date_basis: simulated_weekly_archive
content_revision: 2
images:
- /img/tech-notes/rotation-eccentricity-image-consistency.svg
---

物体旋转时中心稍有偏移，图像既可能变形，也可能改变亮度。我希望弄清机械偏心是否能靠图像对齐处理，以及什么时候应优先改归中与光路。

## 研究与排查过程

研究提出用同一正常物体，在不同偏移位置重复拍摄，同时固定模型与阈值。比较展开宽度、边缘位置、亮度和异常热点，再看配准后哪些变化还存在。这样把机械误差转成图像误差，能够比只测中心偏移更直接地判断对检测的影响。

![转台偏心对视觉检测的影响研究研究路径示意](/img/tech-notes/rotation-eccentricity-image-consistency.svg)

## 涉及的技术与取舍

技术涉及重复定位测试、二维几何配准和成像一致性评价。平移或轮廓对齐能改善位置偏差，但无法保证恢复原先的反光、阴影与折射。若对齐后热点仍跟随光照变化，应研究归中、姿态、光源与曝光。机械重复性应进入视觉测试条件，与算法版本共同记录。

为了让试验可比较，应在每组偏移下重复拍摄，而不是正常位置拍一张、偏移位置也拍一张。若变化随机且不重复，先检查夹持和运动；若热点稳定随偏移移动，再研究图像配准与照明关系。

## 这轮研究的结论

结论是配准只能解决一部分几何变化，不能代替稳定成像。现有交流属于影响分析，没有统一的允许偏心范围或验收指标。下一轮应在受控偏移条件下比较正常误报与缺陷检出，再确定机械容差。
