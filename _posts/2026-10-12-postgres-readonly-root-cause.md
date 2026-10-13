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
updated_at: '2026-10-13T08:02:56+08:00'
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

## 10 月 12 日补充：代理节点重新接入已有反馈

后续操作反馈确认：PCP 工具安装后，执行节点重新接入操作成功，`SHOW POOL_NODES` 中两个后端均显示 up。这个结果证明 Pgpool 的节点接入状态恢复了，仍需要从应用入口验证读写和复制状态，不能仅凭 up 宣布业务故障彻底解决。

当时助手根据排查材料将直接触发描述为主库连接连续超时后被代理摘除。本文没有重新取得完整原日志，因此保留为此前的排查结论；超时为什么发生，仍不能在网络、防火墙和主库资源等可能因素中定案。

Pgpool-II 4.6.3 文档说明，摘除的节点在默认设置下不会自动重新接入，恢复接入前应确认流复制情况。`pcp_attach_node` 是节点接入操作；它并不替代数据恢复或拓扑核验。还要检查本机 `failback_command`，因为接入可能触发配置的回调脚本，不能认为命令必然没有其它副作用。

自动巡检当时只形成了方案：确认主库可写、备库复制正常、角色符合预期且没有维护锁后，才考虑接入；异常时记录并停止修复动作。没有自动巡检部署与故障演练回执，不应标成已经实现。本文不公开实际拓扑地址、认证信息、巡检参数和运维脚本。

## 参考资料

- [PostgreSQL 事务参数](https://www.postgresql.org/docs/current/runtime-config-client.html)
- [PostgreSQL 恢复状态函数](https://www.postgresql.org/docs/current/functions-admin.html)
- [Pgpool-II 4.6.3：节点接入命令](https://www.pgpool.net/docs/pgpool-II-4.6.3/en/html/pcp-attach-node.html)
- [Pgpool-II 4.6.3：故障转移与重新接入](https://www.pgpool.net/docs/pgpool-II-4.6.3/en/html/runtime-config-failover.html)
