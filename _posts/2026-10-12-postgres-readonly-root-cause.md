---
layout: post
title: PostgreSQL 突然变成只读：先检查连接到了哪里
subtitle: 只读事务可能来自备库、会话配置或应用事务设置，自动恢复前必须先确认原因。
date: 2026-10-12 08:00:00 +0800
author: edyang
header-style: text
catalog: true
tags:
- PostgreSQL
- 数据库
- 故障排查
tech_note: true
note_id: postgres-readonly-root-cause
source_date: '2026-10-12'
source_dates:
- '2026-10-12'
published_at: '2026-10-12T12:51:43+08:00'
updated_at: '2026-10-12T12:51:43+08:00'
verification: partial
privacy_reviewed: true
permalink: /tech/2026/10/12/postgres-readonly-root-cause/
excerpt: 只读事务可能来自备库、会话配置或应用事务设置，自动恢复前必须先确认原因。
---

应用反复遇到只读事务时，只重启服务可能暂时恢复，却不会说明根因。首先应从实际出错的连接查询服务器身份和只读状态，避免只检查另一台数据库主机。

## 一条只读查询收集基础证据

```sql
SELECT inet_server_addr(), inet_server_port(),
       pg_is_in_recovery(),
       current_setting('transaction_read_only'),
       current_setting('default_transaction_read_only');
```

输出中的服务器地址属于内部信息，不应出现在公开报告。这些结果应与应用使用的连接、角色、数据库和时间对应。

## 分清不同层次

`pg_is_in_recovery()` 可帮助判断服务器是否处于恢复状态。`transaction_read_only` 描述当前事务，而默认设置影响新事务。应用也可能显式开启只读事务，连接池可能复用了带状态的会话。

查询默认参数的来源，还应核对会话、角色、数据库和服务器配置。若连接经过代理或高可用入口，需要记录实际落到哪台实例，而不是只看连接字符串。

## 自动恢复不能盲目切换数据库角色

检测可以持续记录实际后端身份、读写探针与错误，但修复动作必须对应确认的原因。刷新失效连接与改变数据库主备角色是不同操作。没有明确的高可用拓扑和故障证据，不能自动 promote 或强行改写只读状态。

截至整理时只有故障现象和初步检查，完整日志尚未核验，根因未定。这篇公开的是诊断路径，不披露业务库名、内部地址和运维账号。

## 参考资料

- [PostgreSQL 事务参数](https://www.postgresql.org/docs/current/runtime-config-client.html)
- [PostgreSQL 恢复状态函数](https://www.postgresql.org/docs/current/functions-admin.html)
