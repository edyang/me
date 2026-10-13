---
layout: post
title: 双 V100 部署 llama.cpp：排查上下文超限
subtitle: 本地模型接上编程助手以后，两张显卡和模型加载都看起来正常，但一次请求直接被服务端拒绝。
date: 2023-02-15 08:00:00 +0800
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
updated_at: '2026-10-13T17:59:15+08:00'
verification: observed
privacy_reviewed: true
permalink: /tech/2026/04/03/llama-cpp-context-budget/
excerpt: 本地模型接上编程助手以后，两张显卡和模型加载都看起来正常，但一次请求直接被服务端拒绝。
archive_date: '2023-02-15'
date_basis: simulated_weekly_archive
content_revision: 2
images:
- /img/tech-notes/llama-cpp-context-budget.svg
---

本地模型接上编程助手以后，两张显卡和模型加载都看起来正常，但一次请求直接被服务端拒绝。报错说请求有 33951 tokens，而可用上下文只有 16384 tokens。这个数字对照，比反复猜显卡驱动问题更直接。

## 研究与排查过程

排查从服务启动参数与客户端最终请求组成入手。编程助手提交的内容不只是我输入的一句话，还包括历史消息、工具定义和代码片段。服务端设置的窗口必须容纳这些输入，并给输出留空间。随后再核对日志实际分配的上下文和并发 slot，避免只相信客户端界面显示的最大长度。

![双 V100 部署 llama.cpp：排查上下文超限研究路径示意](/img/tech-notes/llama-cpp-context-budget.svg)

## 涉及的技术与取舍

采用的技术是 llama.cpp 服务端上下文配置、KV cache 预算和真实长请求测试。两张 16GB V100 的显存要分别考虑权重、缓存和计算缓冲，量化权重不会让全部运行内存等比例减少。可控的优化路径是先限制工具返回与历史长度，再逐级调整窗口，记录每一步的显存峰值、首 token 延迟与生成速度。

### 辅助检查示例

以下为通用示例，用于理解上述检查；变量、设备和参数需对应实际环境。

```text
request (33951 tokens) exceeds the available context size (16384 tokens)
```

## 这轮研究的结论

现有证据已经确认这次失败属于请求超出服务窗口。它没有证明把窗口改得很大就一定稳定，也没有证明两卡会自动平分所有额外内存。我的结论是先建立可复现的请求预算，再扩容；能加载模型与能接住长工程请求，应分别验证。

## 参考资料

- [llama.cpp server 文档](https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md)
