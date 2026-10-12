---
layout: post
title: 批量推理的数据隔离：别让上一条结果进入下一条
subtitle: 批处理统计和单条业务上下文，应在生命周期和归属上保持清楚。
date: 2026-10-09 08:00:00 +0800
author: edyang
header-style: text
catalog: true
tags:
- Python
- 数据质量
- 软件设计
tech_note: true
note_id: batch-inference-case-isolation
source_date: '2026-10-09'
source_dates:
- '2026-10-09'
published_at: '2026-10-12T12:51:43+08:00'
updated_at: '2026-10-12T12:51:43+08:00'
verification: notes
privacy_reviewed: true
permalink: /tech/2026/10/09/batch-inference-case-isolation/
excerpt: 批处理统计和单条业务上下文，应在生命周期和归属上保持清楚。
---

多个案例组成一批进行推理时，单条结果可能看起来正确，但合并报告里的目标、计数或证据却错位。这类错误常出在共享可变对象与生命周期。

## 每条案例创建自己的上下文

案例 ID、输入图像列表、中间结果和最终结论应归属同一案例。下一条开始时创建新对象，不复用上一次的字典、列表或缓存容器。需要复用的是只读模型和明确设计的缓存。

```python
for item in items:
    context = {
        "case_id": item["id"],
        "inputs": list(item["inputs"]),
        "results": [],
    }
    process(context)
```

这只是对象生命周期示例，`process` 代表待实现的业务处理，并非可直接运行的完整推理程序。

## 全批统计在外部汇总

吞吐、平均耗时、失败数和类别分布属于批次报告。不要把这些可变字段写进单条案例上下文，再让后续模块误当成当前案例的证据。

## 验证要专门制造相邻差异

连续放入目标、输入张数和预期结果差异很大的两条样本，再交换顺序重复测试。检查单跑和批跑结果是否一致、案例 ID 是否串联、最终报告与单条结果是否一致。

本文是从历史排查抽出的通用软件经验，不公开原始案例和内部模块。批处理“全部完成”与“每条结果归属正确”，必须分别检查。
