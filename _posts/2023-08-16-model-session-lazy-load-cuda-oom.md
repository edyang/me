---
layout: post
title: 多模态服务首个会话显存不足的排查
subtitle: 服务健康检查可以返回，但建立首个视频会话时出现 cudaMalloc failed，并提前关闭。
date: 2023-08-16 08:00:00 +0800
author: edyang
header-style: text
catalog: true
tags:
- CUDA
- 模型部署
- 故障排查
tech_note: true
note_id: model-session-lazy-load-cuda-oom
source_date: '2026-09-14'
source_dates:
- '2026-09-14'
published_at: '2026-10-13T08:02:56+08:00'
updated_at: '2026-10-13T17:59:15+08:00'
verification: partial
privacy_reviewed: true
permalink: /tech/2026/09/14/model-session-lazy-load-cuda-oom/
excerpt: 服务健康检查可以返回，但建立首个视频会话时出现 cudaMalloc failed，并提前关闭。
archive_date: '2023-08-16'
date_basis: simulated_weekly_archive
content_revision: 2
images:
- /img/tech-notes/model-session-lazy-load-cuda-oom.svg
---

服务健康检查可以返回，但建立首个视频会话时出现 cudaMalloc failed，并提前关闭。这个现象让我意识到，进程能响应和目标模式能运行之间，还隔着资源初始化与真实请求验证。

## 研究与排查过程

排查先对齐会话开始、模型加载、申请失败和显存占用的时间。此前讨论将它解释为首会话触发额外加载，但没有完整初始化实现，因此这只是分析方向。随后检查同一块 GPU 的进程占用，区分本服务峰值与并行负载，不根据另一块卡有空闲显存就推断会自动分摊。

![多模态服务首个会话显存不足的排查研究路径示意](/img/tech-notes/model-session-lazy-load-cuda-oom.svg)

## 涉及的技术与取舍

采用 nvidia-smi 查询设备和进程显存，并对照容器状态。确认可暂停负载后才释放资源复测；若主要由本服务消耗，则按实现支持的参数调整上下文、并发或 GPU 装载范围。每次只改一项，同时检查主机内存和延迟，避免把 GPU 压力移到另一资源后误认成功。

### 辅助检查示例

以下为通用示例，用于理解上述检查；变量、设备和参数需对应实际环境。

```bash
nvidia-smi --query-gpu=index,name,memory.total,memory.used,memory.free --format=csv
nvidia-smi --query-compute-apps=pid,process_name,used_memory --format=csv
docker ps
```

## 这轮研究的结论

现有证据确认显存分配失败，没有最终成功会话。结论是就绪验证要覆盖真实目标模式，而非只返回 HTTP 200；冷启动首会话和第二次会话都应检查，才能判断资源准备、释放与复用是否符合预期。

## 参考资料

- [NVIDIA CUDA Runtime：设备内存分配](https://docs.nvidia.com/cuda/cuda-runtime-api/group__CUDART__MEMORY.html)
