---
layout: post
title: Docker Compose 只有 Web 启动失败：先看宿主机端口冲突
subtitle: 数据库、缓存和后端都正常时，Web 端口占用不应被当成整套系统故障。
date: 2026-08-01 08:00:00 +0800
author: edyang
header-style: text
catalog: true
tags:
- Docker
- 故障排查
tech_note: true
note_id: compose-port-collision
source_date: '2026-08-01'
source_dates:
- '2026-08-01'
published_at: '2026-10-12T12:51:43+08:00'
updated_at: '2026-10-12T12:51:43+08:00'
verification: observed
privacy_reviewed: true
permalink: /tech/2026/08/01/compose-port-collision/
excerpt: 数据库、缓存和后端都正常时，Web 端口占用不应被当成整套系统故障。
---

一次 Compose 部署中，网络、数据库、缓存和后端都已启动，Web 单独失败。日志提示宿主机端口已经被占用。这类问题先查端口归属，比重新部署整套环境更快。

## 左边是宿主机端口，右边是容器端口

例如 `18002:8002` 表示访问宿主机 18002 转发到容器 8002。调整左侧映射，不一定需要修改应用在容器内的监听端口。

```yaml
services:
  web:
    ports:
      - "127.0.0.1:18002:8002"
```

这里的回环绑定只是本机反向代理场景的示例。若需要局域网直接访问，应按实际网络策略选择监听地址，不能照搬后认为其它设备也能访问。

## 确认谁正在使用端口

```bash
sudo ss -lntp 'sport = :8002'
docker compose ps
```

确认已有进程的用途后，再决定更换映射或停止冲突服务。不要随手杀掉占用端口的进程。映射变更还要同步反向代理、前端访问地址和健康检查。

## 警告与启动失败分开看

当时 Compose 也提示顶层 `version` 已过时，但它是警告；真正导致 Web 失败的是端口冲突。排查时优先寻找明确的失败位置，并检查其它服务是否受影响。

历史记录确认了端口冲突，提出了更换映射方案；没有后续访问验证。因此最终应补查 Web 响应以及前端到后端的请求，而不只看容器状态是 running。

## 参考资料

- [Docker 端口发布](https://docs.docker.com/engine/network/port-publishing/)
