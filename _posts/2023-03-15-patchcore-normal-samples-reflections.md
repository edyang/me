---
layout: post
title: 研究 PatchCore 在反光物体上的异常误报
subtitle: 正常样本比较容易获得，微小缺陷却很难收齐，所以我研究了基于正常特征的异常检测。
date: 2023-03-15 08:00:00 +0800
author: edyang
header-style: text
catalog: true
tags:
- 视觉检测
- PatchCore
tech_note: true
note_id: patchcore-normal-samples-reflections
source_date: '2026-04-28'
source_dates:
- '2026-04-28'
- '2026-07-02'
- '2026-08-20'
published_at: '2026-10-12T12:51:43+08:00'
updated_at: '2026-10-13T17:59:15+08:00'
verification: notes
privacy_reviewed: true
permalink: /tech/2026/04/28/patchcore-normal-samples-reflections/
excerpt: 正常样本比较容易获得，微小缺陷却很难收齐，所以我研究了基于正常特征的异常检测。
archive_date: '2023-03-15'
date_basis: simulated_weekly_archive
content_revision: 2
images:
- /img/tech-notes/patchcore-normal-samples-reflections.svg
---

正常样本比较容易获得，微小缺陷却很难收齐，所以我研究了基于正常特征的异常检测。实际讨论中最困扰我的现象是反光和复杂纹理也会形成异常热点：热力图颜色很强，并不一定代表真的有缺陷。

## 研究与排查过程

研究先从算法机制展开。PatchCore 用正常局部特征建立记忆库，再计算新特征与正常库的距离；因此任何没有被正常库覆盖的成像变化都可能得高分。接下来提出用同一正常物体重复拍摄，并主动改变光照或姿态，观察热点是否跟着反光移动，分清成像扰动和缺陷。

![研究 PatchCore 在反光物体上的异常误报研究路径示意](/img/tech-notes/patchcore-normal-samples-reflections.svg)

## 涉及的技术与取舍

涉及的技术是局部特征、正常记忆库、最近邻距离和阈值评估。正常数据应覆盖允许的变化，同时排除混入的真实缺陷；验证集则独立包含小缺陷、反光和不同姿态。阈值选择需同时观察正常误报与缺陷漏检，不能只挑一张热力图调到视觉满意。这里不披露实际产品的数据和参数组合。

## 这轮研究的结论

初步结论是先稳定成像、完善正常数据，再评价阈值，不能把所有问题归给模型。已有记录支持反光误判这一现象，但没有统一验收指标。因此这轮属于方法研究，尚不能得出换模型或加样本已经解决误报的结论。

## 参考资料

- [PatchCore 原始论文](https://arxiv.org/abs/2106.08265)
