---
layout: post
title: Docker Compose Web 启动失败：定位端口冲突
subtitle: 一次部署里数据库、缓存与后端已经启动，只有 Web 起不来。
date: 2023-06-21 08:00:00 +0800
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
updated_at: '2026-10-13T17:59:15+08:00'
verification: observed
privacy_reviewed: true
permalink: /tech/2026/08/01/compose-port-collision/
excerpt: 一次部署里数据库、缓存与后端已经启动，只有 Web 起不来。
archive_date: '2023-06-21'
date_basis: simulated_weekly_archive
content_revision: 2
images:
- /img/tech-notes/compose-port-collision.svg
---

一次部署里数据库、缓存与后端已经启动，只有 Web 起不来。日志同时出现 Compose version 警告与端口占用错误，我需要先判断哪条才是真正阻止服务启动的原因。

## 研究与排查过程

排查先用 ss 查询宿主机端口归属，再对照 compose ps 中的服务状态。冲突定位后，方案考虑调整宿主机侧映射，而不直接改变容器内应用端口。已有占用进程也要核对用途，不能为了新服务启动就随手结束另一个正常服务。

![Docker Compose Web 启动失败：定位端口冲突研究路径示意](/img/tech-notes/compose-port-collision.svg)

## 涉及的技术与取舍

技术核心是 Docker 端口发布的两端含义：映射左侧属于宿主机，右侧属于容器。修改发布端口后还要同步反向代理、前端入口与健康检查。回环绑定适合由本机代理转发，局域网直接访问则需要不同的监听规划。顶层 version 过时只是警告，应与实际失败分开记录。

### 辅助检查示例

以下为通用示例，用于理解上述检查；变量、设备和参数需对应实际环境。

```yaml
services:
  web:
    ports:
      - "127.0.0.1:18002:8002"
```

```bash
sudo ss -lntp 'sport = :8002'
docker compose ps
```

## 这轮研究的结论

已有证据支持端口冲突，换映射仍属于处理方案，没有随后访问结果。结论是查清资源归属再修改，并通过 Web 响应和前后端请求验证，不能只以容器 running 判断业务恢复。

## 参考资料

- [Docker 端口发布](https://docs.docker.com/engine/network/port-publishing/)
