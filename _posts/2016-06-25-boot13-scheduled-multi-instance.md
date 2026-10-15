---
layout: post
title: Spring Boot 定时任务：多实例会不会重复执行
subtitle: 单机时每天运行一次，部署两个实例后可能运行两次。
date: 2016-06-25 08:00:00 +0800
author: edyang
header-style: text
catalog: true
tags:
- Spring Boot
- 后端工程
tech_note: true
note_id: boot13-scheduled-multi-instance
permalink: /tech/2016/06/25/boot13-scheduled-multi-instance/
excerpt: 单机时每天运行一次，部署两个实例后可能运行两次。
privacy_reviewed: true
content_revision: 3
images:
- /img/tech-notes/boot13-scheduled-multi-instance.svg
technology_since: '2015-11-16'
---

单机时每天运行一次，部署两个实例后可能运行两次。调度注解只描述本实例的触发。

本文使用Spring Boot 1.3、JDK 8 与关系数据库，片段需要补齐工程配置。框架提供装配和运行入口，容量、任务归属与故障恢复仍需要应用明确设计。本文采用一代 Spring Boot 配置，相关默认值只在给定版本范围内讨论。

## 1. 从现象推到机制

每个应用实例都可能建立自己的定时器。需要全局只执行一次的业务，应有数据库任务身份、租约或外部协调。任务周期短于执行时长时，还要区分固定频率、固定延迟和并发执行约定。

![Spring Boot 定时任务：多实例会不会重复执行的处理、反馈与观察关系](/img/tech-notes/boot13-scheduled-multi-instance.svg)

图中的四个节点分别表示本地调度、全局身份、执行归属、恢复重试。顺着实线检查输入如何变成输出，再沿虚线核对反馈条件。图示表达的是本文讨论的关系，不是实测曲线或现场截图。

## 2. 最小实现与输入条件

以日报为演示任务，使用业务日期与任务类型建立唯一记录。任务取得执行权后记录状态，失败重试复用同一业务身份。

```text
unique task key = report_type + business_date
try acquire execution ownership
if acquired: run and record result
else: inspect existing task state
```

先在单实例演示环境固定依赖和配置，再观察线程、连接与请求状态。组件参数需要结合任务耗时验证，不能只根据 CPU 核数填写所有并发配置。

## 3. 用对照区分原因

下表列出需要主动改变的条件。预期行为来自机制分析，复现时还需记录运行环境和原始输出，不能将预期当作已经测得的结果。

| 改变的条件 | 需要验证的行为 |
| --- | --- |
| 两个实例同时触发 | 只有取得执行权者处理同一任务 |
| 任务超过预期周期 | 不能无限重叠产生重复工作 |
| 执行中实例退出 | 需要明确接管和幂等恢复 |

### 对照 1：两个实例同时触发

只有取得执行权者处理同一任务。观察时记录唯一键或租约的裁决结果。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 2：任务超过预期周期

不能无限重叠产生重复工作。观察时记录触发语义与实际运行区间。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 3：执行中实例退出

需要明确接管和幂等恢复。观察时记录租约状态与已产生的业务结果。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。

## 4. 适用条件与取舍

锁住任务不等于外部副作用只发生一次。发送、导出或结算仍要有业务幂等依据，恢复时先核对已完成步骤。

一次正常运行只覆盖了这组输入。继续扩展前，应把上面的异常对照保留下来，尤其关注“执行中实例退出”这一分支。后续方案若改变了图中任意一处依赖，原来的判断就要重新验证，不能仅凭界面相似或返回值相同沿用结论。

## 同月延伸

- [Spring Boot 性能：连接池大不等于数据库更快](/tech/2016/06/05/boot13-connection-pool-budget/)
- [Spring Boot 异步方法：线程边界会带走哪些上下文](/tech/2016/06/15/boot13-async-context/)

## 参考资料

1. [Spring Boot 1.3 参考文档](https://docs.spring.io/spring-boot/docs/1.3.0.RELEASE/reference/htmlsingle/)
2. [Spring Framework 4.2 参考文档](https://docs.spring.io/spring-framework/docs/4.2.0.RELEASE/spring-framework-reference/htmlsingle/)
