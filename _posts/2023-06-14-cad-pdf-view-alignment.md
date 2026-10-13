---
layout: post
title: 工程图 PDF 对齐：研究匹配与输出异常
subtitle: 比较两份工程图时，我先尝试把对应视图对齐，再考虑尺寸与构件差异。
date: 2023-06-14 08:00:00 +0800
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
updated_at: '2026-10-13T17:59:15+08:00'
verification: partial
privacy_reviewed: true
permalink: /tech/2026/07/23/cad-pdf-view-alignment/
excerpt: 比较两份工程图时，我先尝试把对应视图对齐，再考虑尺寸与构件差异。
archive_date: '2023-06-14'
date_basis: simulated_weekly_archive
content_revision: 2
images:
- /img/tech-notes/cad-pdf-view-alignment.svg
---

比较两份工程图时，我先尝试把对应视图对齐，再考虑尺寸与构件差异。测试中图片能够读入，也出现匹配点，却没有输出文件；另一个问题是有效内点不够理想，需要把算法与文件链路拆开排查。

## 研究与排查过程

研究先确定可比视图，裁掉标题栏与无关边框，再统一栅格化分辨率。对应特征找到后，用 RANSAC 排除离群匹配，并查看内点是否覆盖整个视图。即使数目足够，全部集中在局部也可能让其它区域漂移，因此拟保存匹配图、内点图与变换后的叠加图。

![工程图 PDF 对齐：研究匹配与输出异常研究路径示意](/img/tech-notes/cad-pdf-view-alignment.svg)

## 涉及的技术与取舍

技术涉及 OpenCV 特征匹配、单应或其它合适的二维变换，以及图像写入验证。不同视角不能强行当作同一平面视图；保存阶段要确认目录、有效图像和 imwrite 返回值。输出为空并不自动说明匹配算法失败，也可能是计算前退出、路径不符或写文件失败。

### 辅助检查示例

以下为通用示例，用于理解上述检查；变量、设备和参数需对应实际环境。

```python
from pathlib import Path
import cv2

output = Path("output/aligned.png")
output.parent.mkdir(parents=True, exist_ok=True)
ok = cv2.imwrite(str(output), aligned_image)
if not ok:
    raise RuntimeError("image write failed")
```

## 这轮研究的结论

结论是先留下裁剪、匹配、变换、保存四个阶段的中间产物，再调整算法。原记录没有最后对齐成功的回执，所以不能称为完成了工程图自动比对。下一轮验证应同时检查整图对齐误差和输出文件，而不是只看匹配点数量。

## 参考资料

- [OpenCV 特征匹配与 Homography](https://docs.opencv.org/4.x/d1/de0/tutorial_py_feature_homography.html)
