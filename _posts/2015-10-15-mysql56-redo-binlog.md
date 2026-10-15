---
layout: post
title: 深入 MySQL：redo log 与 binlog 各自解决什么
subtitle: 都叫日志，redo 与 binlog 却处在不同层次。
date: 2015-10-15 08:00:00 +0800
author: edyang
header-style: text
catalog: true
tags:
- MySQL
- 数据库原理
tech_note: true
note_id: mysql56-redo-binlog
permalink: /tech/2015/10/15/mysql56-redo-binlog/
excerpt: 都叫日志，redo 与 binlog 却处在不同层次。
privacy_reviewed: true
content_revision: 3
images:
- /img/tech-notes/mysql56-redo-binlog.svg
technology_since: '2015-02-02'
---

都叫日志，redo 与 binlog 却处在不同层次。备份、恢复和复制不能把它们当成可互换文件。

本文使用MySQL 5.6、InnoDB 与独立测试数据库。数据库研究要同时观察表结构、数据分布和实际语句。本文讨论 InnoDB（事务存储引擎），不把其他存储引擎或后续版本特性当作相同行为。

## 1. 从现象推到机制

redo（重做日志）支持存储引擎崩溃恢复，binlog（二进制日志）记录服务器层的逻辑变更信息，可用于复制与时间点恢复。刷盘策略影响持久性窗口，数据库进程正常返回不等于任意硬件故障下都零损失。

![深入 MySQL：redo log 与 binlog 各自解决什么的处理、反馈与观察关系](/img/tech-notes/mysql56-redo-binlog.svg)

图中的四个节点分别表示事务变化、重做日志、二进制日志、恢复演练。顺着实线检查输入如何变成输出，再沿虚线核对反馈条件。图示表达的是本文讨论的关系，不是实测曲线或现场截图。

## 2. 最小实现与输入条件

先查看演示实例的相关配置，再设计独立恢复演练。本文不提供断电测试指令，也不把日志文件存在当成恢复成功证据。

```sql
SHOW VARIABLES LIKE 'innodb_flush_log_at_trx_commit';
SHOW VARIABLES LIKE 'sync_binlog';
SHOW VARIABLES LIKE 'log_bin';
```

先保存建表语句、索引与隔离级别，再准备固定演示数据。并发行为使用两个独立连接按顺序执行；执行计划、锁等待和最终数据需要结合，单看查询耗时不足以解释原因。

## 3. 用对照区分原因

下表列出需要主动改变的条件。预期行为来自机制分析，复现时还需记录运行环境和原始输出，不能将预期当作已经测得的结果。

| 改变的条件 | 需要验证的行为 |
| --- | --- |
| 只有 binlog 没有可用基础备份 | 不能据此完整恢复所有历史数据 |
| 放宽同步策略 | 性能与故障丢失窗口存在取舍 |
| 备份文件能够生成 | 仍需独立还原验证 |

### 对照 1：只有 binlog 没有可用基础备份

不能据此完整恢复所有历史数据。观察时记录备份起点与日志连续性。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 2：放宽同步策略

性能与故障丢失窗口存在取舍。观察时记录生效配置与故障模型。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 3：备份文件能够生成

仍需独立还原验证。观察时记录还原后的数据一致性。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。

## 4. 适用条件与取舍

恢复能力取决于完整链路：一致备份、连续日志、保管与演练。配置值只能说明策略，无法替代对存储和故障行为的验证。

一次正常运行只覆盖了这组输入。继续扩展前，应把上面的异常对照保留下来，尤其关注“备份文件能够生成”这一分支。后续方案若改变了图中任意一处依赖，原来的判断就要重新验证，不能仅凭界面相似或返回值相同沿用结论。

## 同月延伸

- [深入 MySQL：EXPLAIN 的估计不能当成实测](/tech/2015/10/05/mysql56-explain-estimation/)
- [深入 MySQL：读写分离为什么会读到旧数据](/tech/2015/10/25/mysql56-replication-lag/)

## 参考资料

1. [MySQL 5.6.23 源码与文档](https://github.com/mysql/mysql-server/tree/mysql-5.6.23)
2. [MySQL 5.6 官方历史手册](https://docs.oracle.com/cd/E17952_01/mysql-5.6-en/index.html)
