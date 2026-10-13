---
layout: post
title: PostgreSQL 只读故障：研究代理节点与恢复
subtitle: 应用遇到只读事务时，重启可能暂时恢复，却解释不了为何连到不可写后端。
date: 2023-11-29 08:00:00 +0800
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
updated_at: '2026-10-13T17:59:15+08:00'
verification: partial
privacy_reviewed: true
permalink: /tech/2026/10/12/postgres-readonly-root-cause/
excerpt: 应用遇到只读事务时，重启可能暂时恢复，却解释不了为何连到不可写后端。
archive_date: '2023-11-29'
date_basis: simulated_weekly_archive
content_revision: 2
images:
- /img/tech-notes/postgres-readonly-root-cause.svg
---

应用遇到只读事务时，重启可能暂时恢复，却解释不了为何连到不可写后端。我先研究如何从实际出错的连接确认服务器与事务状态，再对照 Pgpool 节点接入信息，而不是只检查数据库主机本身。

## 研究与排查过程

过程先查询 pg_is_in_recovery、transaction_read_only 与默认只读设置，并核对当前连接落点。后续反馈确认 PCP 工具安装、节点重新接入成功，SHOW POOL_NODES 两个后端显示 up。这证明接入状态恢复，仍需验证应用入口写入和复制。此前分析认为主库连接超时后被摘除，但完整原日志未重新取得，超时根因不能定案。

![PostgreSQL 只读故障：研究代理节点与恢复研究路径示意](/img/tech-notes/postgres-readonly-root-cause.svg)

## 涉及的技术与取舍

技术涉及 PostgreSQL 恢复状态、会话事务参数、Pgpool 后端状态与 pcp_attach_node。自动巡检方案先核对主库可写、角色、复制与维护状态，再决定是否接入；它不替代数据恢复，也可能触发配置的 failback_command。刷新连接与 promote 改角色不同，不能把自动恢复写成无条件主备切换。

### 辅助检查示例

以下为通用示例，用于理解上述检查；变量、设备和参数需对应实际环境。

```sql
SELECT inet_server_addr(), inet_server_port(),
       pg_is_in_recovery(),
       current_setting('transaction_read_only'),
       current_setting('default_transaction_read_only');
```

## 这轮研究的结论

结论是代理节点 up、数据库角色正确和业务写入恢复是三个检查点。人工接入已有反馈，自动巡检仍只有方案，没有部署和故障演练结果。后续应同时验证复制、应用读写以及异常时停止修复，确认故障原因后再固化恢复策略。

## 参考资料

- [PostgreSQL 事务参数](https://www.postgresql.org/docs/current/runtime-config-client.html)
- [PostgreSQL 恢复状态函数](https://www.postgresql.org/docs/current/functions-admin.html)
- [Pgpool-II 4.6.3：节点接入命令](https://www.pgpool.net/docs/pgpool-II-4.6.3/en/html/pcp-attach-node.html)
- [Pgpool-II 4.6.3：故障转移与重新接入](https://www.pgpool.net/docs/pgpool-II-4.6.3/en/html/runtime-config-failover.html)
