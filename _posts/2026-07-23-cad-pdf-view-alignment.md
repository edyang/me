---
layout: post
title: DWG 与 PDF 图纸对齐：匹配点多不等于已经对齐
subtitle: 工程图匹配需要看内点、覆盖范围和输出质量，不能只看总匹配数。
date: 2026-07-23 08:00:00 +0800
author: edyang
header-style: text
catalog: true
tags:
- CAD
- OpenCV
- 故障排查
tech_note: true
note_id: cad-pdf-view-alignment
source_date: '2026-07-23'
source_dates:
- '2026-07-23'
- '2026-07-24'
published_at: '2026-10-12T12:51:43+08:00'
updated_at: '2026-10-12T12:51:43+08:00'
verification: partial
privacy_reviewed: true
permalink: /tech/2026/07/23/cad-pdf-view-alignment/
excerpt: 工程图匹配需要看内点、覆盖范围和输出质量，不能只看总匹配数。
---

比较两份工程图时，第一阶段可以先做对应视图对齐，再逐步加入尺寸和构件校验。一次测试读图成功，也找到了匹配点，但输出目录仍为空；另一个线索是有效内点较少。

## 先让两个视图可比

先确定对应视图，裁掉标题栏、说明文字和无关边框。统一栅格化分辨率，再选择适合线图的特征或轮廓方法。不同视角的图纸不能仅靠一个二维变换强行当作相同视图。

## RANSAC 内点和空间分布都要看

原测试曾出现总匹配数明显多于内点的情况。即使内点数够计算变换，若全部挤在一个角落，也可能在其它区域严重漂移。应该保存匹配图、内点分布和变换后的叠加图。

## 输出为空先验证写文件

```python
from pathlib import Path
import cv2

output = Path("output/aligned.png")
output.parent.mkdir(parents=True, exist_ok=True)
ok = cv2.imwrite(str(output), aligned_image)
if not ok:
    raise RuntimeError("image write failed")
```

`aligned_image` 在这里代表前序计算得到的有效图像。除了返回值，还要检查图像是否为空、输出路径实际指向哪里，以及程序是否在保存前已经异常退出。

原记录没有最终对齐成功回执。算法调参之前，先把裁剪、匹配、变换和保存四个阶段的中间产物保留下来，更容易判断真正的问题。

## 参考资料

- [OpenCV 特征匹配与 Homography](https://docs.opencv.org/4.x/d1/de0/tutorial_py_feature_homography.html)
