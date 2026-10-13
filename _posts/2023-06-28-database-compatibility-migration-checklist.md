---
layout: post
title: 研究数据库迁移中的兼容改造与验证
subtitle: 数据库替换时，应用能连接、一个查询能返回，并不足以说明兼容。
date: 2023-06-28 08:00:00 +0800
author: edyang
header-style: text
catalog: true
tags:
- 数据库
- Java
- 软件设计
tech_note: true
note_id: database-compatibility-migration-checklist
source_date: '2026-08-04'
source_dates:
- '2026-08-04'
published_at: '2026-10-12T12:51:43+08:00'
updated_at: '2026-10-13T17:59:15+08:00'
verification: proposal
privacy_reviewed: true
permalink: /tech/2026/08/04/database-compatibility-migration-checklist/
excerpt: 数据库替换时，应用能连接、一个查询能返回，并不足以说明兼容。
archive_date: '2023-06-28'
date_basis: simulated_weekly_archive
content_revision: 2
images:
- /img/tech-notes/database-compatibility-migration-checklist.svg
---

数据库替换时，应用能连接、一个查询能返回，并不足以说明兼容。我研究的重点是如何把 SQL、数据类型、事务与迁移校验整理成可执行的检查范围，避免上线后才发现边界问题。

## 研究与排查过程

过程先分类盘点：精度、空值、时间和布尔类型；分页、函数、序列与关键字；索引、约束、触发器和存储过程。随后选择完整业务读写链路，固定输入与预期输出，对照迁移前后结果。ORM 可以减少部分方言差异，原生 SQL 和历史脚本仍需单独检查。

![研究数据库迁移中的兼容改造与验证研究路径示意](/img/tech-notes/database-compatibility-migration-checklist.svg)

## 涉及的技术与取舍

采用的技术方法是数据映射、SQL 兼容测试、事务并发验证与迁移核验。数据不仅核对总量，还要检查抽样、关联完整性、编码与边界值。并发场景验证隔离、锁与异常回滚；切换方案记录批次和时刻，明确并行写入与回退后的数据处理，先做演练。

例如金额的小数精度、日期的时区和空值排序，都可能让同一条业务查询返回不同结果。测试不只判断 SQL 是否执行，还要比较结果集合、异常回滚后是否留脏数据，以及关联约束是否仍有效。

## 这轮研究的结论

结论是迁移验收要覆盖完整业务行为及恢复条件，不能靠连接成功宣布完成。原交流形成了改造范围，没有特定数据库迁移验收记录。下一轮应将检查项落到真实脚本和结果，再决定是否允许切换。
