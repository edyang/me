---
layout: post
title: 健康检查正常，首次模型会话却 OOM：把就绪验证做到请求里
subtitle: 进程存活、模型加载完成和目标会话可用，需要不同的验证证据。
date: 2026-09-14 08:00:00 +0800
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
updated_at: '2026-10-13T08:02:56+08:00'
verification: partial
privacy_reviewed: true
permalink: /tech/2026/09/14/model-session-lazy-load-cuda-oom/
excerpt: 进程存活、模型加载完成和目标会话可用，需要不同的验证证据。
---

一次多模态服务排查里，基础健康检查能够返回，建立首个视频会话时却出现 `cudaMalloc failed` 和会话关闭。日志还记录了 GPU 缓冲区申请失败。这说明服务进程的响应与目标功能的可用性之间，仍有一段需要验证的路径。

## 错误出现在哪一步，比首页能否打开更有用

我把状态分成三层：服务进程可以响应、模型所需资源已经准备好、目标模式能够完成一轮实际请求。一个普通健康检查究竟证明哪层，要看该服务的实现，不能只看到 HTTP 200 就推断模型全部加载完成。

当时的助手将故障解释为首个完整会话触发额外加载，导致显存不足。现有记录支持 GPU 内存分配失败这一现象，但没有完整初始化代码和显存曲线，懒加载的具体范围仍待确认。也不能因为报错落在 GPU0，就认为其它 GPU 的空闲显存一定能被自动使用。

## 先查同一块 GPU 的实际占用

```bash
nvidia-smi --query-gpu=index,name,memory.total,memory.used,memory.free --format=csv
nvidia-smi --query-compute-apps=pid,process_name,used_memory --format=csv
docker ps
```

以上只读示例用于本机检查，公开记录时应泛化进程和容器名称。将会话开始、模型加载、失败和 GPU 占用的时间对齐，检查占用来自本服务还是其它任务。不要看到一个进程就直接停止它。

若确认有可暂停的并行负载，释放资源后复测同一请求；若资源主要由本服务消耗，再按当前实现支持的参数降低上下文、并发或 GPU 装载范围。每次只改一项并记录配置。降低 GPU 装载可能增加主机内存和延迟，不能只检查显存是否下降。

## 成功标准应覆盖冷启动和第二次会话

完成一次真实的目标模式请求，确认会话没有提前关闭、输出有效，再建立第二次会话检查资源是否释放或复用。把会话可用性加入就绪检查，是这里提炼的方法建议，不是声称原服务已经实现了这个检查。

本次记录没有最终成功会话，也没有性能实测。已观察到的是 GPU 分配失败；资源竞争、自身峰值需求以及初始化行为还需要后续证据区分。不能把“停止其它服务”或“降低上下文”的建议写成已经修复。

## 参考资料

- [NVIDIA CUDA Runtime：设备内存分配](https://docs.nvidia.com/cuda/cuda-runtime-api/group__CUDART__MEMORY.html)
