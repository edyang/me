---
layout: post
title: V100 部署 vLLM：架构兼容与显存排查
subtitle: 尝试用双 V100 运行量化模型时，日志先出现 attention 后端不兼容，又在多模态 profiling 阶段遇到显存申请失败。
date: 2023-03-08 08:00:00 +0800
author: edyang
header-style: text
catalog: true
tags:
- 大模型
- vLLM
- GPU
tech_note: true
note_id: v100-vllm-attention-compatibility
source_date: '2026-04-15'
source_dates:
- '2026-04-15'
published_at: '2026-10-12T12:51:43+08:00'
updated_at: '2026-10-13T17:59:15+08:00'
verification: partial
privacy_reviewed: true
permalink: /tech/2026/04/15/v100-vllm-attention-compatibility/
excerpt: 尝试用双 V100 运行量化模型时，日志先出现 attention 后端不兼容，又在多模态 profiling 阶段遇到显存申请失败。
archive_date: '2023-03-08'
date_basis: simulated_weekly_archive
content_revision: 2
images:
- /img/tech-notes/v100-vllm-attention-compatibility.svg
---

尝试用双 V100 运行量化模型时，日志先出现 attention 后端不兼容，又在多模态 profiling 阶段遇到显存申请失败。总显存看起来够用，却不能解释这两类错误，因此研究需要按启动阶段拆开。

## 研究与排查过程

首先识别硬件条件：V100 属于 Volta，算力为 7.0，不能默认运行面向较新架构的注意力实现。随后把权重加载和后续视觉编码器 profiling 分开观察。模型已加载只证明前一阶段成功，图像编码、缓存和计算缓冲仍会产生额外峰值。

![V100 部署 vLLM：架构兼容与显存排查研究路径示意](/img/tech-notes/v100-vllm-attention-compatibility.svg)

## 涉及的技术与取舍

采用的检查涉及 vLLM、CUDA、PyTorch、模型结构、量化后端和 attention backend 的共同兼容性。GGUF 与 GPTQ 使用不同加载路径，原来的 llama.cpp 配置不能直接搬过来。拟验证时先固定依赖，用短文本、较小上下文和单请求打通生成，再加入受控图像，最后扩展并发，并记录每卡显存。

## 这轮研究的结论

结论是架构支持与容量预算必须分别通过。记录中有真实报错和替代后端的讨论，没有足够材料证明新的组合长期稳定。这篇保留失败阶段和验证顺序，最终可用配置仍需附版本、启动日志与目标模式的实际请求结果。

## 参考资料

- [vLLM attention 后端文档](https://docs.vllm.ai/en/latest/design/attention_backends/)
