---
layout: post
title: 深入 PostgreSQL：pg_dump 成功后还要验证恢复
subtitle: 备份文件生成并不说明能恢复应用。
date: 2017-03-25 08:00:00 +0800
author: edyang
header-style: text
catalog: true
tags:
- PostgreSQL
- 数据库
tech_note: true
note_id: postgres96-backup-restore
permalink: /tech/2017/03/25/postgres96-backup-restore/
excerpt: 备份文件生成并不说明能恢复应用。
privacy_reviewed: true
content_revision: 3
images:
- /img/tech-notes/postgres96-backup-restore.svg
technology_since: '2016-09-29'
---

备份文件生成并不说明能恢复应用。角色、扩展和依赖同样影响还原结果。

本文使用PostgreSQL 9.6 与独立演示库。PostgreSQL（关系数据库）的类型、事务和执行计划需要按版本理解。本文使用九点六时期已经存在的能力，不把后续大版本的 SQL 语法提前放入示例。

## 1. 从现象推到机制

逻辑备份保存对象定义与数据，格式决定使用 psql 还是 pg_restore。单库备份不会自动包含集群全部全局对象。目标服务器版本、扩展与权限需要提前准备，不能等故障发生才发现缺少依赖。

![深入 PostgreSQL：pg_dump 成功后还要验证恢复的处理、反馈与观察关系](/img/tech-notes/postgres96-backup-restore.svg)

图中的四个节点分别表示逻辑导出、依赖准备、独立还原、业务校验。顺着实线检查输入如何变成输出，再沿虚线核对反馈条件。图示表达的是本文讨论的关系，不是实测曲线或现场截图。

## 2. 最小实现与输入条件

在测试库生成自定义格式备份，先查看目录，再还原到独立空库。检查表数、约束和少量业务不变量，不覆盖原库。

```bash
pg_dump -Fc -d demo -f demo.dump
pg_restore --list demo.dump
# 目标 demo_restore 需事先独立创建
pg_restore -d demo_restore demo.dump
```

先确认服务器版本、连接身份和 schema（模式），再在演示表中执行。涉及并发时使用两个独立会话；执行计划可能真正运行语句，写操作应在可回滚的测试事务内观察。

## 3. 用对照区分原因

下表列出需要主动改变的条件。预期行为来自机制分析，复现时还需记录运行环境和原始输出，不能将预期当作已经测得的结果。

| 改变的条件 | 需要验证的行为 |
| --- | --- |
| 备份文件非空 | 仍不证明对象和数据完整 |
| 目标缺少扩展或角色 | 部分对象可能无法建立 |
| 表行数一致 | 还需检查约束与业务关联 |

### 对照 1：备份文件非空

仍不证明对象和数据完整。观察时记录还原日志与错误。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 2：目标缺少扩展或角色

部分对象可能无法建立。观察时记录依赖清单和权限映射。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 3：表行数一致

还需检查约束与业务关联。观察时记录关键查询与完整性规则。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。

## 4. 适用条件与取舍

备份应保留在独立故障域并控制访问。恢复演练使用脱敏或受控数据，不能把备份文件直接放到公开下载目录。

一次正常运行只覆盖了这组输入。继续扩展前，应把上面的异常对照保留下来，尤其关注“表行数一致”这一分支。后续方案若改变了图中任意一处依赖，原来的判断就要重新验证，不能仅凭界面相似或返回值相同沿用结论。

## 同月延伸

- [深入 PostgreSQL：先确认连到哪台库和哪个 schema](/tech/2017/03/05/postgres96-connection-schema/)
- [深入 PostgreSQL：编码、时区与时间字段语义](/tech/2017/03/15/postgres96-encoding-timezone/)

## 参考资料

1. [PostgreSQL 9.6 文档](https://www.postgresql.org/docs/9.6/)
2. [PostgreSQL 9.6 发布记录](https://www.postgresql.org/about/news/postgresql-96-released-1703/)
