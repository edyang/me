---
layout: post
title: Spring Boot 异步方法：线程边界会带走哪些上下文
subtitle: 把慢操作标为异步后，请求很快返回，但任务仍可能失败，而且原事务不会自动随线程移动。
date: 2016-06-15 08:00:00 +0800
author: edyang
header-style: text
catalog: true
tags:
- Spring Boot
- 后端工程
tech_note: true
note_id: boot13-async-context
permalink: /tech/2016/06/15/boot13-async-context/
excerpt: 把慢操作标为异步后，请求很快返回，但任务仍可能失败，而且原事务不会自动随线程移动。
privacy_reviewed: true
content_revision: 3
images:
- /img/tech-notes/boot13-async-context.svg
technology_since: '2015-11-16'
---

把慢操作标为异步后，请求很快返回，但任务仍可能失败，而且原事务不会自动随线程移动。

本文使用Spring Boot 1.3、JDK 8 与关系数据库，片段需要补齐工程配置。框架提供装配和运行入口，容量、任务归属与故障恢复仍需要应用明确设计。本文采用一代 Spring Boot 配置，相关默认值只在给定版本范围内讨论。

## 1. 从现象推到机制

@Async 依赖代理调用与执行器，异步线程有自己的执行环境。请求线程局部变量、认证信息和事务上下文不能假定自动继承。返回成功接收与任务最终成功，需要不同状态表达。

![Spring Boot 异步方法：线程边界会带走哪些上下文的处理、反馈与观察关系](/img/tech-notes/boot13-async-context.svg)

图中的四个节点分别表示请求事务、执行队列、后台线程、任务查询。顺着实线检查输入如何变成输出，再沿虚线核对反馈条件。图示表达的是本文讨论的关系，不是实测曲线或现场截图。

## 2. 最小实现与输入条件

把任务必要身份与输入显式封装，使用受控有界线程池。持久任务先保存任务记录，再由后台更新状态，避免只依赖内存 Future。

```text
request -> validate -> save task record
executor -> load explicit task input
worker -> update RUNNING / SUCCEEDED / FAILED
client -> query task state by task id
```

先在单实例演示环境固定依赖和配置，再观察线程、连接与请求状态。组件参数需要结合任务耗时验证，不能只根据 CPU 核数填写所有并发配置。

## 3. 用对照区分原因

下表列出需要主动改变的条件。预期行为来自机制分析，复现时还需记录运行环境和原始输出，不能将预期当作已经测得的结果。

| 改变的条件 | 需要验证的行为 |
| --- | --- |
| 请求立即返回任务号 | 只表示任务已被受理 |
| 工作线程发生异常 | 调用方需要可查询失败状态 |
| 入口事务尚未提交 | 异步读取可能找不到数据 |

### 对照 1：请求立即返回任务号

只表示任务已被受理。观察时记录持久任务记录是否已提交。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 2：工作线程发生异常

调用方需要可查询失败状态。观察时记录异常处理与任务状态更新。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 3：入口事务尚未提交

异步读取可能找不到数据。观察时记录提交时刻与任务开始时刻。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。

## 4. 适用条件与取舍

异步不是无限后台执行许可。任务应有取消、超时与重复处理策略，线程池满时也需要明确拒绝而非默默丢弃。

一次正常运行只覆盖了这组输入。继续扩展前，应把上面的异常对照保留下来，尤其关注“入口事务尚未提交”这一分支。后续方案若改变了图中任意一处依赖，原来的判断就要重新验证，不能仅凭界面相似或返回值相同沿用结论。

## 同月延伸

- [Spring Boot 性能：连接池大不等于数据库更快](/tech/2016/06/05/boot13-connection-pool-budget/)
- [Spring Boot 定时任务：多实例会不会重复执行](/tech/2016/06/25/boot13-scheduled-multi-instance/)

## 参考资料

1. [Spring Boot 1.3 参考文档](https://docs.spring.io/spring-boot/docs/1.3.0.RELEASE/reference/htmlsingle/)
2. [Spring Framework 4.2 参考文档](https://docs.spring.io/spring-framework/docs/4.2.0.RELEASE/spring-framework-reference/htmlsingle/)
