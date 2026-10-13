---
layout: post
title: 图像异常检测提速：分析 FAISS 与完整链路
subtitle: 图像检测一次仍需几秒时，我想知道继续提速的空间在哪里。
date: 2023-03-22 08:00:00 +0800
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
updated_at: '2026-10-13T17:59:15+08:00'
verification: notes
privacy_reviewed: true
permalink: /tech/2026/05/08/faiss-inference-timing-budget/
excerpt: 图像检测一次仍需几秒时，我想知道继续提速的空间在哪里。
archive_date: '2023-03-22'
date_basis: simulated_weekly_archive
content_revision: 2
images:
- /img/tech-notes/faiss-inference-timing-budget.svg
---

图像检测一次仍需几秒时，我想知道继续提速的空间在哪里。直觉上容易先换更快的网络，但整个流程还有读图、预处理、传输、特征检索和结果保存，单看模型前向不足以做决定。

## 研究与排查过程

研究先制定分段计时方法，分别记录预处理、GPU 前向、设备间传输、FAISS 查询和可视化。随后区分首次加载、warmup 和连续推理，并使用固定批次观察中位耗时与尾部耗时。GPU 操作异步执行，测量必须使用同步或 CUDA event，否则统计的可能只是入队时间。

![图像异常检测提速：分析 FAISS 与完整链路研究路径示意](/img/tech-notes/faiss-inference-timing-budget.svg)

## 涉及的技术与取舍

检索阶段重点讨论 FAISS 的索引类型、记忆库大小、批量查询和线程数。CPU 检索是否值得搬到 GPU，要把传输开销和与模型争用一起算；近似索引虽然可能更快，也可能改变异常分数。减少分辨率、特征或记忆库都需要重新对照小缺陷检出与误报，不能只报告速度。

### 辅助检查示例

以下为通用示例，用于理解上述检查；变量、设备和参数需对应实际环境。

```text
read → preprocess → features → transfer → search → merge → save
每段记录：耗时、输入规模、线程数、设备与峰值内存
```

## 这轮研究的结论

结论是先定位占比最大的阶段，再选择优化方向。已有交流包含提速目标与方案讨论，没有统一条件下的前后性能验收。下一轮应保存输入集、环境、分段时间及检测结果，用同一批样本判断收益，而不是用最快一张图代表系统性能。

## 参考资料

- [FAISS 性能优化说明](https://github.com/facebookresearch/faiss/wiki/Faster-search)
