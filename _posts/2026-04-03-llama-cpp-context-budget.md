---
layout: post
title: 双 V100 跑本地大模型：上下文长度要按服务端预算算
subtitle: 客户端标出的上下文上限，与本地推理服务实际能接收的长度是两回事。一次 33951 tokens 请求说明了这个区别。
date: 2026-04-03 08:00:00 +0800
author: edyang
header-style: text
catalog: true
tags:
- 大模型
- llama.cpp
- GPU
tech_note: true
note_id: llama-cpp-context-budget
source_date: '2026-04-03'
source_dates:
- '2026-04-03'
- '2026-04-15'
published_at: '2026-10-12T12:51:43+08:00'
updated_at: '2026-10-12T12:51:43+08:00'
verification: observed
privacy_reviewed: true
permalink: /tech/2026/04/03/llama-cpp-context-budget/
excerpt: 客户端标出的上下文上限，与本地推理服务实际能接收的长度是两回事。一次 33951 tokens 请求说明了这个区别。
---

把本地模型接入编程助手后，模型已经成功加载，两张卡也能工作，却仍然收到请求超长错误。问题出在请求预算：客户端把工具定义、历史消息、代码片段一起提交，服务端并没有为这些内容预留足够的上下文。

## 一次实际出现的错误

当时环境是两张 16GB V100，服务端设置 `--ctx-size 16384`。客户端提交了 33951 tokens，返回的错误明确写出了请求长度超过 16384。这里能够确认的是上下文超限，不能凭这个错误推断 CUDA 或模型文件损坏。

```text
request (33951 tokens) exceeds the available context size (16384 tokens)
```

## 我会先核对这三项

第一项是服务启动日志中的实际上下文容量。第二项是客户端最终请求的总长度，而不是输入框里那一句话的长度。第三项是并发配置：不同版本的 llama.cpp 对 KV 池和 slot 的分配方式可能不同，需要看当前版本文档和启动日志。

显存预算至少包括权重、KV cache、计算缓冲和并发开销。量化权重能降低权重占用，但不意味着 KV cache 按相同比例缩小。模型的层数、KV heads、缓存精度也会改变结果，所以不能用另一模型的“每千 token 显存”直接套算。

## 比直接调到超大上下文更可控的做法

先让单请求以较小上下文稳定运行，再逐级增大容量；每一步记录空闲显存、长输入能否完成、首 token 延迟和生成速度。同时限制工具返回长度，给历史消息做摘要，并为模型输出预留空间。每次扩容都用真实长请求测试，避免只用短问答证明配置可用。

这次记录证明了超限原因，没有证明某个更大配置可以长期稳定运行。对工程助手来说，稳定的可用预算比客户端宣称的最大窗口更有用。

## 参考资料

- [llama.cpp server 文档](https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md)
