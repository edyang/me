---
layout: post
title: 离线补传队列：重试次数很大，不一定是死循环
subtitle: 判断队列是否正常，要同时看状态、时间、任务年龄和处理耗时。
date: 2026-09-29 08:00:00 +0800
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
updated_at: '2026-10-12T12:51:43+08:00'
verification: partial
privacy_reviewed: true
permalink: /tech/2026/09/29/offline-outbox-retry-observation/
excerpt: 判断队列是否正常，要同时看状态、时间、任务年龄和处理耗时。
---

离线队列里一条任务重试很多次，状态仍是 uploading，容易让人以为程序失控。但累计重试次数不能单独判断。任务已存在多天、连接持续失败时，次数本身可能符合退避间隔。

## next_retry_at 是开始重试的条件

如果任务到达 `next_retry_at` 后已被 worker 领取，查询时看到当前时间晚于这个字段并不异常。应结合 `updated_at`、日志和下一次失败后的时间判断。

```sql
SELECT status, retry_count, next_retry_at, created_at, updated_at
FROM offline_outbox
ORDER BY created_at;
```

这是只读查询示例；真实排查时还要限制范围，并避免把含内部地址的错误内容复制到公开日志。

## 一段时间里的变化比单次截图更有价值

观察领取、上传、失败、次数增加和下一次时间更新是否连贯。若长时间停在 uploading，检查连接超时、进程存活与任务租约。重启时如何回收中断任务，也要有明确策略。

## 队列饥饿是另一类问题

历史排查还出现过长耗时任务排在前面，后面的注册或关键任务迟迟得不到处理。worker 存活不代表所有任务都在进展。可按任务类型和优先级分配处理能力，并记录最老等待时间。

![离线任务领取、失败与补传流程](/img/tech-notes/outbox.svg)

## 成功补传也要考虑幂等

服务端可能已经受理，客户端却没收到回执。重试需要稳定的业务幂等键，避免重复生成数据。成功后的索引保留、文件清理和保留周期，也要分别定义。

记录确认了持续重试与队列等待现象，但没有所有建议修复后的验收结果。因此不能仅靠修改一个重试字段就宣称完成离线同步。

## 参考资料

- [SQLite 事务说明](https://www.sqlite.org/lang_transaction.html)
