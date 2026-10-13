---
layout: post
title: 人脸登录误识别：研究误放行与误拒绝
subtitle: 实测中，两个陌生人被匹配成同一个已注册对象；之后收紧条件，已注册人员又更难登录。
date: 2023-09-27 08:00:00 +0800
author: edyang
header-style: text
catalog: true
tags:
- 视觉检测
- 身份认证
- 测试
tech_note: true
note_id: face-match-false-accept-reject
source_date: '2026-09-29'
source_dates:
- '2026-09-29'
- '2026-10-08'
published_at: '2026-10-12T12:51:43+08:00'
updated_at: '2026-10-13T17:59:15+08:00'
verification: partial
privacy_reviewed: true
permalink: /tech/2026/09/29/face-match-false-accept-reject/
excerpt: 实测中，两个陌生人被匹配成同一个已注册对象；之后收紧条件，已注册人员又更难登录。
archive_date: '2023-09-27'
date_basis: simulated_weekly_archive
content_revision: 2
images:
- /img/tech-notes/face-match-false-accept-reject.svg
---

实测中，两个陌生人被匹配成同一个已注册对象；之后收紧条件，已注册人员又更难登录。我希望保留识别效果，因此研究不能只围绕提高或降低一个阈值，而要同时观察两种错误。

## 研究与排查过程

过程先澄清最近邻的含义：库中总有一个最接近的候选，但这不代表输入属于库内人员。接着讨论绝对匹配质量、候选间区分度与输入质量。验证集应同时覆盖注册对象的光照、姿态和遮挡，以及独立陌生人样本，分别记录误放行与误拒绝。

![人脸登录误识别：研究误放行与误拒绝研究路径示意](/img/tech-notes/face-match-false-accept-reject.svg)

## 涉及的技术与取舍

涉及技术是特征匹配、质量筛选与开放集身份核验。不同模型的距离或相似度不能直接互换，分数也不是天然概率。多帧确认可以减少波动，但相邻帧不完全独立，仍需排除旧帧、多人脸和候选跳变。公开笔记不包含真实特征库、图像或生产阈值。

评估时还要保留每次失败的输入条件和候选变化。若同一个注册对象只有特定光照下失败，可以先从图像质量与注册样本覆盖分析；若多名陌生人共同指向一个候选，则需要核对库内特征、匹配和拒绝规则。

## 这轮研究的结论

已有记录确认了两种错误，尚无最后验收结果。结论是建立固定测试集与工作点，再决定规则；不能用一次陌生人拒绝成功掩盖注册用户大量登不上的问题。性能优化也应在同样识别条件下比较，避免以减少验证换速度。
