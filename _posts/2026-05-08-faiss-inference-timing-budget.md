---
layout: post
title: 视觉推理从几秒继续提速：先量出时间花在哪里
subtitle: 特征提取在 GPU 上，不代表整条异常检测链路都在 GPU 上。
date: 2026-05-08 08:00:00 +0800
author: edyang
header-style: text
catalog: true
tags:
- 视觉检测
- 性能优化
- FAISS
tech_note: true
note_id: faiss-inference-timing-budget
source_date: '2026-05-08'
source_dates:
- '2026-05-08'
published_at: '2026-10-12T12:51:43+08:00'
updated_at: '2026-10-12T12:51:43+08:00'
verification: notes
privacy_reviewed: true
permalink: /tech/2026/05/08/faiss-inference-timing-budget/
excerpt: 特征提取在 GPU 上，不代表整条异常检测链路都在 GPU 上。
---

一条图像异常检测链路通常包含读图、前景处理、对齐、切块、特征提取、检索和结果绘制。模型前向很快，整张图仍然慢，瓶颈可能在 CPU 检索或数据传输。

## 分段计时比总耗时更有用

至少分别记录预处理、GPU 前向、CPU/GPU 数据传输、FAISS 检索和可视化。GPU 操作具有异步性，测量 GPU 阶段时需要同步或使用 CUDA event；否则计时可能只统计了任务入队。

```text
read → preprocess → features → transfer → search → merge → save
每段记录：耗时、输入规模、线程数、设备与峰值内存
```

## 先比较冷启动和热运行

模型加载、首次算子初始化与真正逐图推理应该分开。做 warmup 后再测试固定批次，报告中同时保留中位耗时和尾部耗时，不只挑最快一张图。

FAISS 的索引类型、记忆库规模、批量查询方式和线程配置都会影响速度。把特征逐条送入检索，与一次批量查询的成本不同。多线程也可能与其它库线程叠加，引起争用。

## GPU 不是默认最优答案

GPU 索引要同时考虑当前平台支持、显存、转换成本和与模型争用。若检索本来很小，把数据搬上 GPU 的额外开销可能抵消收益。若改用近似检索，需要重新评估异常分数和检出结果。

当时存在明确的提速目标，但目标不能写成已经达到的性能。优化记录应附固定样本、版本、参数和前后结果，让后续选择有据可查。

## 参考资料

- [FAISS 性能优化说明](https://github.com/facebookresearch/faiss/wiki/Faster-search)
