---
layout: post
title: Docker 双网络实践：独立 IP 和服务名通信分别验证
subtitle: bridge 加 macvlan 可以服务不同通信需求，但外网可达不代表容器也能访问宿主机自身地址。
date: 2026-05-13 08:00:00 +0800
author: edyang
header-style: text
catalog: true
tags:
- Docker
- 网络
- 运维
tech_note: true
note_id: docker-macvlan-bridge-dual-network
source_date: '2026-05-13'
source_dates:
- '2026-05-13'
published_at: '2026-10-12T12:51:43+08:00'
updated_at: '2026-10-12T12:51:43+08:00'
verification: partial
privacy_reviewed: true
permalink: /tech/2026/05/13/docker-macvlan-bridge-dual-network/
excerpt: bridge 加 macvlan 可以服务不同通信需求，但外网可达不代表容器也能访问宿主机自身地址。
---

容器需要像局域网中的独立设备一样被访问，同时又要用服务名连接消息中间件。一次部署采用了 bridge 与 macvlan 双网络，实测外网基础连通和容器服务通信可用，但访问宿主机自身地址仍失败。

## 两张网络各自承担什么

bridge 用于容器之间的内部通信；macvlan 让容器以独立 MAC/IP 出现在物理网络里。需要提前确认交换网络允许多 MAC、地址不冲突，并核对默认路由。接了两张网络不代表出口选择一定符合预期。

![bridge 与 macvlan 的不同通信路径](/img/tech-notes/docker-dual-network.svg)

## 分别做三组测试

第一组测试容器之间的服务名和真实业务端口。第二组测试容器到外部目标的连接。第三组单独测试容器到宿主机。不能用 `ping` 公网成功替代其它两项，也不能用 TCP 连接建立替代业务请求成功。

Docker 官方文档明确说明，macvlan 容器与宿主机直接通信存在内核侧限制。可根据实际需求使用 bridge 路径，或单独设计宿主机 macvlan 接口；具体路由和地址规划应当经过现场验证。

## 保留正确的结果边界

当时已经确认部分链路可用，但宿主机地址回流问题仍存在。把它写成“所有网络问题解决”会误导后续部署。记录每组测试的源、目标、端口、协议和结果，比一张简单的网络拓扑更重要。

只为单机服务提供端口映射时，默认 bridge 可能已经足够。macvlan 应由独立 IP 的实际需求驱动，避免把普通部署变成额外的网络运维工作。

## 参考资料

- [Docker macvlan](https://docs.docker.com/engine/network/drivers/macvlan/)
- [Docker 多网络与网关](https://docs.docker.com/engine/network/)
