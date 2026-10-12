---
layout: post
title: 工业相机条带拼接：颜色顺序、队列和节流都要看
subtitle: 窄条拼接不是简单裁图。格式转换和处理吞吐会共同影响最终结果。
date: 2026-08-19 08:00:00 +0800
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
updated_at: '2026-10-12T12:51:43+08:00'
verification: partial
privacy_reviewed: true
permalink: /tech/2026/08/19/bayer-strip-panorama-pipeline/
excerpt: 窄条拼接不是简单裁图。格式转换和处理吞吐会共同影响最终结果。
---

面阵相机也可以在特定运动条件下截取窄条并拼接图像。但要得到可用结果，除了几何关系，还要保证像素格式转换正确、帧序稳定和处理速度跟得上。

## 红蓝反转先检查格式链

相机的 Bayer 排列、SDK 输出格式、OpenCV 转换常量以及显示组件期待的 RGB/BGR 顺序，要从头到尾核对。不同库的命名习惯容易造成误用，最直接的验证方法是拍摄已知红、绿、蓝色块。

```text
相机原始格式 → 去马赛克 → 内部颜色约定 → 裁条 → 拼接 → 显示/保存
```

## 处理不及时时不要只加大队列

若单帧处理耗时明显超过采集间隔，无限制缓存会增加延迟和内存。根据业务选择受控采样、忙时跳过或有限队列，并分别统计接收、处理、主动跳过与异常丢弃。

节流应在明确的位置执行，不能一个阶段已经减少输入，后面又重复丢弃。首次模型初始化也应与稳态处理分开测量。

## 拼接质量仍然依赖运动

条带宽度、运动速度、帧率和曝光需要共同匹配。出现横向拉伸、重复纹理或缺口时，先检查时间戳和有效位移，再判断是否需要编码器同步。

原交流出现过颜色反转和处理吞吐不足，并讨论了修正，但缺少最终稳定运行结果。本文记录的是链路检查点，不披露现场 SDK 配置和产品参数。

## 参考资料

- [OpenCV 颜色转换](https://docs.opencv.org/4.x/d8/d01/group__imgproc__color__conversions.html)
