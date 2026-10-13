---
layout: post
title: 大图切块异常检测：研究边界上下文处理
subtitle: 高分辨率图像直接缩小会损失小缺陷，切成小块又可能在块交界处产生伪异常。
date: 2023-03-29 08:00:00 +0800
author: edyang
header-style: text
catalog: true
tags:
- 视觉检测
- 图像处理
tech_note: true
note_id: tiled-anomaly-border-context
source_date: '2026-05-08'
source_dates:
- '2026-05-08'
- '2026-07-02'
published_at: '2026-10-12T12:51:43+08:00'
updated_at: '2026-10-13T17:59:15+08:00'
verification: notes
privacy_reviewed: true
permalink: /tech/2026/05/08/tiled-anomaly-border-context/
excerpt: 高分辨率图像直接缩小会损失小缺陷，切成小块又可能在块交界处产生伪异常。
archive_date: '2023-03-29'
date_basis: simulated_weekly_archive
content_revision: 2
images:
- /img/tech-notes/tiled-anomaly-border-context.svg
---

高分辨率图像直接缩小会损失小缺陷，切成小块又可能在块交界处产生伪异常。我希望保留细节，同时让边界区域也能得到合理判断，因此把切块方式本身当作一个独立研究问题。

## 研究与排查过程

先分析同一纹理在中心与边缘的区别：完整结构在切块边缘被截断，网络看到的上下文和填充条件发生变化。讨论随后转向对照试验，把缺陷分别放在块中心、边缘和交界处，比较固定切块、重叠切块与扩展上下文。训练和推理的裁剪规则必须保持一致。

![大图切块异常检测：研究边界上下文处理研究路径示意](/img/tech-notes/tiled-anomaly-border-context.svg)

## 涉及的技术与取舍

技术方案是扩大特征计算的输入范围，而只把中央有效区域映射回原图。扩展区提供上下文，不能在汇总中重复计数；边缘裁剪、坐标偏移和重叠合并需要明确规则。评价时同时保留边界正常样本与边界缺陷，并检查回写位置，避免图像看起来完整但热点发生错位。

## 这轮研究的结论

研究结论是上下文有可能改善边界条件，但收益必须由固定样本验证。原交流涉及不同方案分支，没有证明某一种裁剪能通用于所有成像条件。接下来应比较误报、召回和耗时，再决定如何组合全图与区域处理。

## 参考资料

- [PatchCore 原始论文](https://arxiv.org/abs/2106.08265)
