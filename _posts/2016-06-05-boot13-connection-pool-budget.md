---
layout: post
title: Spring Boot 性能：连接池大不等于数据库更快
subtitle: 请求排队时把连接池翻倍，可能把等待从应用移到数据库，并增加锁竞争。
date: 2016-06-05 08:00:00 +0800
author: edyang
header-style: text
catalog: true
tags:
- Spring Boot
- 后端工程
tech_note: true
note_id: boot13-connection-pool-budget
permalink: /tech/2016/06/05/boot13-connection-pool-budget/
excerpt: 请求排队时把连接池翻倍，可能把等待从应用移到数据库，并增加锁竞争。
privacy_reviewed: true
content_revision: 3
images:
- /img/tech-notes/boot13-connection-pool-budget.svg
technology_since: '2015-11-16'
---

请求排队时把连接池翻倍，可能把等待从应用移到数据库，并增加锁竞争。

本文使用Spring Boot 1.3、JDK 8 与关系数据库，片段需要补齐工程配置。框架提供装配和运行入口，容量、任务归属与故障恢复仍需要应用明确设计。本文采用一代 Spring Boot 配置，相关默认值只在给定版本范围内讨论。

## 1. 从现象推到机制

数据库能有效处理的并发取决于查询成本、锁和资源。连接池是有限许可集合，借用等待、执行耗时和归还都要观察。一条慢事务长时间占用连接，会降低整体可用容量。

![Spring Boot 性能：连接池大不等于数据库更快的处理、反馈与观察关系](/img/tech-notes/boot13-connection-pool-budget.svg)

图中的四个节点分别表示入口请求、连接借用、数据库执行、及时归还。顺着实线检查输入如何变成输出，再沿虚线核对反馈条件。图示表达的是本文讨论的关系，不是实测曲线或现场截图。

## 2. 最小实现与输入条件

先分别记录连接借用时间和 SQL 执行时间，确认连接是否在所有路径释放。按一代框架实际使用的池核对配置，不套用后续默认连接池属性。

```text
request wait -> connection borrow
transaction start -> SQL work
commit / rollback -> return connection
measure: borrow_wait, active, idle, transaction_duration
```

先在单实例演示环境固定依赖和配置，再观察线程、连接与请求状态。组件参数需要结合任务耗时验证，不能只根据 CPU 核数填写所有并发配置。

## 3. 用对照区分原因

下表列出需要主动改变的条件。预期行为来自机制分析，复现时还需记录运行环境和原始输出，不能将预期当作已经测得的结果。

| 改变的条件 | 需要验证的行为 |
| --- | --- |
| 活动连接长期达到上限 | 可能是慢查询或连接未归还 |
| 增大池后数据库延迟上升 | 说明瓶颈可能转移到下游 |
| 请求已失败但连接未释放 | 会逐步侵蚀可用容量 |

### 对照 1：活动连接长期达到上限

可能是慢查询或连接未归还。观察时记录借用堆栈与事务耗时。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 2：增大池后数据库延迟上升

说明瓶颈可能转移到下游。观察时记录数据库等待与完成吞吐。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 3：请求已失败但连接未释放

会逐步侵蚀可用容量。观察时记录异常路径资源归还。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。

## 4. 适用条件与取舍

连接池大小应与应用实例总数一起计算。每实例配置合理，扩容多个实例后仍可能超过数据库总连接和并发预算。

一次正常运行只覆盖了这组输入。继续扩展前，应把上面的异常对照保留下来，尤其关注“请求已失败但连接未释放”这一分支。后续方案若改变了图中任意一处依赖，原来的判断就要重新验证，不能仅凭界面相似或返回值相同沿用结论。

## 同月延伸

- [Spring Boot 异步方法：线程边界会带走哪些上下文](/tech/2016/06/15/boot13-async-context/)
- [Spring Boot 定时任务：多实例会不会重复执行](/tech/2016/06/25/boot13-scheduled-multi-instance/)

## 参考资料

1. [Spring Boot 1.3 参考文档](https://docs.spring.io/spring-boot/docs/1.3.0.RELEASE/reference/htmlsingle/)
2. [Spring Framework 4.2 参考文档](https://docs.spring.io/spring-framework/docs/4.2.0.RELEASE/spring-framework-reference/htmlsingle/)
