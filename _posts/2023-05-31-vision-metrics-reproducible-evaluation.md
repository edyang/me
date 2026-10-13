---
layout: post
title: 模型权重还在：如何重新建立可信评估
subtitle: 训练环境或旧评测记录丢失以后，手里只剩权重，很容易想给方案补几个预期精度。
date: 2023-05-31 08:00:00 +0800
author: edyang
header-style: text
catalog: true
tags:
- 视觉检测
- 测试
- 数据质量
tech_note: true
note_id: vision-metrics-reproducible-evaluation
source_date: '2026-07-06'
source_dates:
- '2026-07-06'
- '2026-10-08'
published_at: '2026-10-12T12:51:43+08:00'
updated_at: '2026-10-13T17:59:15+08:00'
verification: notes
privacy_reviewed: true
permalink: /tech/2026/07/06/vision-metrics-reproducible-evaluation/
excerpt: 训练环境或旧评测记录丢失以后，手里只剩权重，很容易想给方案补几个预期精度。
archive_date: '2023-05-31'
date_basis: simulated_weekly_archive
content_revision: 2
images:
- /img/tech-notes/vision-metrics-reproducible-evaluation.svg
---

训练环境或旧评测记录丢失以后，手里只剩权重，很容易想给方案补几个预期精度。我讨论的重点是怎样重新跑出可核验结果，让模型表现来自实际预测，而不是来自目标数字。

## 研究与排查过程

研究先固定权重哈希、类别表、输入尺寸、阈值和处理版本，然后准备未参与训练的数据，并明确标注规则。每条预测和错误样本都要保存，才能回看指标为什么变化。采集失败、损坏图片和标签争议也单独计数，不能在出现错误后临时从分母中删掉。

![模型权重还在：如何重新建立可信评估研究路径示意](/img/tech-notes/vision-metrics-reproducible-evaluation.svg)

## 涉及的技术与取舍

技术评价按任务分别选择：分类使用混淆矩阵、Precision/Recall 和准确率；检测使用明确 IoU 条件的 AP/mAP；异常检测观察固定阈值下的误报与漏检。图像级 AUROC 与现场工作点检出率表达不同，不能把多个百分比混用。版本与测试集应一起冻结，便于优化后比较。

## 这轮研究的结论

结论是权重可用不等于旧指标可追溯。没有实测时应写目标或待评估，再完成独立测试；有结果时给出样本量、定义与错误分布。这轮整理了评估方法，没有凭已有权重补造任何准确率，最终生产效果仍须由对应数据证明。
