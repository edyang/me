---
layout: post
title: Docker 双网络方案：研究 bridge 与 macvlan
subtitle: 容器既需要独立出现在局域网里，又需要按服务名访问消息服务，于是我研究了 bridge 与 macvlan 的双网络方案。
date: 2023-04-05 08:00:00 +0800
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
updated_at: '2026-10-13T17:59:15+08:00'
verification: partial
privacy_reviewed: true
permalink: /tech/2026/05/13/docker-macvlan-bridge-dual-network/
excerpt: 容器既需要独立出现在局域网里，又需要按服务名访问消息服务，于是我研究了 bridge 与 macvlan 的双网络方案。
archive_date: '2023-04-05'
date_basis: simulated_weekly_archive
content_revision: 2
images:
- /img/tech-notes/docker-macvlan-bridge-dual-network.svg
---

容器既需要独立出现在局域网里，又需要按服务名访问消息服务，于是我研究了 bridge 与 macvlan 的双网络方案。部署中部分外部链路和容器互联可用，但访问宿主机地址仍失败，这正好说明网络可用不能用一个总状态表示。

## 研究与排查过程

研究先明确两张网络的职责：bridge 承担内部服务通信，macvlan 给容器独立的局域网身份。随后分别测试服务名、外部目标和宿主机三条路径，并核对出口路由。公网 ping 成功不能证明业务端口可达，服务名可达也不能解释宿主机回流。

![Docker 双网络方案：研究 bridge 与 macvlan研究路径示意](/img/tech-notes/docker-macvlan-bridge-dual-network.svg)

## 涉及的技术与取舍

技术上需要处理多网卡默认路由、物理网络允许的 MAC 数量和地址分配。Docker 官方说明 macvlan 容器与宿主机直接通信存在内核侧限制，因此可研究通过 bridge 访问或配置专门的宿主机 macvlan 接口。是否涉及公网地址回流，还需独立核对网关的 hairpin NAT，不能靠增加网络自动解决。

## 这轮研究的结论

已有记录确认部分通信成功，宿主机相关链路仍未解决。结论是独立 IP 与容器服务名通信是两个需求，双网络可以分别承载，但每条路径仍须验证。简单端口映射能满足的场景优先保持简单，独立局域网身份有实际需要时再引入 macvlan。

## 参考资料

- [Docker macvlan](https://docs.docker.com/engine/network/drivers/macvlan/)
- [Docker 多网络与网关](https://docs.docker.com/engine/network/)
