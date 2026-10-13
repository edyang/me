---
layout: post
title: 离线补传队列：研究重试、卡住与任务饥饿
subtitle: 离线队列中任务反复重试，状态仍显示 uploading，后面的关键任务也可能久等。
date: 2023-10-04 08:00:00 +0800
author: edyang
header-style: text
catalog: true
tags:
- SQLite
- 边缘计算
- 故障排查
tech_note: true
note_id: offline-outbox-retry-observation
source_date: '2026-09-29'
source_dates:
- '2026-09-29'
- '2026-09-30'
- '2026-10-08'
published_at: '2026-10-12T12:51:43+08:00'
updated_at: '2026-10-13T17:59:15+08:00'
verification: partial
privacy_reviewed: true
permalink: /tech/2026/09/29/offline-outbox-retry-observation/
excerpt: 离线队列中任务反复重试，状态仍显示 uploading，后面的关键任务也可能久等。
archive_date: '2023-10-04'
date_basis: simulated_weekly_archive
content_revision: 2
images:
- /img/tech-notes/offline-outbox-retry-observation.svg
---

离线队列中任务反复重试，状态仍显示 uploading，后面的关键任务也可能久等。我研究如何从状态与时间变化判断 worker 是否有进展，而不是仅凭累计重试次数认定程序失控。

## 研究与排查过程

先对照 created_at、updated_at、next_retry_at 与实际日志。任务到重试时间后已被领取，此时旧字段早于当前时间不一定异常；更重要的是失败后次数与下次时间是否更新。若长期停在 uploading，则检查连接超时、进程与租约。再观察慢任务是否持续占据前排，导致其它类型没有处理机会。

![离线补传队列：研究重试、卡住与任务饥饿研究路径示意](/img/tech-notes/offline-outbox-retry-observation.svg)

## 涉及的技术与取舍

技术方案讨论 SQLite 持久队列、领取状态、有限超时、退避、租约回收与任务优先级。服务端已受理但客户端未收回执时，需要稳定幂等键，避免重试产生重复数据。成功回执、业务索引保留与文件清理是不同步骤，应分别定义，不能上传刚返回就无条件删除全部记录。

### 辅助检查示例

以下为通用示例，用于理解上述检查；变量、设备和参数需对应实际环境。

```sql
SELECT status, retry_count, next_retry_at, created_at, updated_at
FROM offline_outbox
ORDER BY created_at;
```

## 这轮研究的结论

已有证据支持持续重试和等待现象，建议修复尚无完整验收。结论是观察队列随时间的变化与最老等待时间，区分离线退避、运行卡住和调度饥饿。故障恢复试验还应验证重启回收与重复受理，不能只修改一个重试字段。

## 参考资料

- [SQLite 事务说明](https://www.sqlite.org/lang_transaction.html)
