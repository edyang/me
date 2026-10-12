---
layout: post
title: 在 V100 上部署 vLLM：先过架构兼容，再谈显存容量
subtitle: 一次双卡 GPTQ 部署同时遇到 attention 后端限制和视觉编码器显存不足，二者要分开处理。
date: 2026-04-15 08:00:00 +0800
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
updated_at: '2026-10-12T12:51:43+08:00'
verification: partial
privacy_reviewed: true
permalink: /tech/2026/04/15/v100-vllm-attention-compatibility/
excerpt: 一次双卡 GPTQ 部署同时遇到 attention 后端限制和视觉编码器显存不足，二者要分开处理。
---

同样是 CUDA 显卡，能否运行一个推理方案还取决于 GPU 架构、算子实现和模型结构。双 V100 部署量化模型时，日志同时出现了 attention 后端不兼容和显存不足；只看总显存容易把两个问题混在一起。

## 两类错误分别说明什么

V100 属于 Volta，算力为 7.0。当时部署日志提示选用的 FlashAttention 后端不支持该架构。另一处错误发生在视觉编码器的 profile 阶段：权重已占用大量显存，后续缓冲分配失败。这是不同阶段的故障。

| 现象 | 优先检查 |
| --- | --- |
| attention 后端拒绝设备 | 当前 vLLM、CUDA、PyTorch 与 GPU 架构组合 |
| 权重加载后仍 OOM | 编码器、KV cache、profile、并发与输入规模 |
| 多卡未达到预期 | 分片支持、卡间通信与每卡独立显存预算 |

## 量化格式也要配套

GGUF 与 GPTQ 面向不同加载和执行路径。不能拿原来 llama.cpp 的启动参数，直接当成 vLLM 的配置。需要核对模型架构、量化后端和当前版本是否共同支持目标设备；环境变量名称也以安装版本为准。

## 最小可用配置怎么验证

我会先固定环境版本，减小上下文和并发，用单条短文本请求验证启动及生成。涉及图像时，再加一张尺寸受控的图片，观察编码器阶段的显存峰值。最后才逐级扩展输入和吞吐，每次只改一个主要变量。

历史交流中有真实报错，也讨论过兼容的 attention 方案，但没有足够证据证明任意新版本都能复用当时配置。保留日志、依赖版本和完整启动命令，是后续复现的关键。

## 参考资料

- [vLLM attention 后端文档](https://docs.vllm.ai/en/latest/design/attention_backends/)
