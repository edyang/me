---
layout: post
title: Spring Cloud 调用链：每层超时要服从总预算
subtitle: 三层服务各自超时一秒，加上重试后，用户可能等待远超一秒。
date: 2016-07-15 08:00:00 +0800
author: edyang
header-style: text
catalog: true
tags:
- Spring Cloud
- 服务治理
tech_note: true
note_id: cloud-timeout-total-budget
permalink: /tech/2016/07/15/cloud-timeout-total-budget/
excerpt: 三层服务各自超时一秒，加上重试后，用户可能等待远超一秒。
privacy_reviewed: true
content_revision: 3
images:
- /img/tech-notes/cloud-timeout-total-budget.svg
technology_since: '2016-05-11'
---

三层服务各自超时一秒，加上重试后，用户可能等待远超一秒。调用预算必须沿链路分配。

本文使用Spring Cloud Brixton 与匹配的 Spring Boot 1.3，示例为调用流程。服务治理需要同时考虑入口、调用链和下游容量。本文讨论 Zuul、Ribbon 与 Hystrix 这一时期的技术组合，不引入后续的网关和容错框架。

## 1. 从现象推到机制

入口截止时间需要覆盖排队、连接、读取和可能的重试。下游每次尝试都消耗剩余预算，不能在接近截止时再启动完整长请求。外层先返回超时后，内层操作还可能继续执行。

![Spring Cloud 调用链：每层超时要服从总预算的处理、反馈与观察关系](/img/tech-notes/cloud-timeout-total-budget.svg)

图中的四个节点分别表示入口截止、阶段分配、重试决策、最终响应。顺着实线检查输入如何变成输出，再沿虚线核对反馈条件。图示表达的是本文讨论的关系，不是实测曲线或现场截图。

## 2. 最小实现与输入条件

为演示链路写时间表，分别记录每次尝试开始和结束。重试只用于协议允许且具幂等语义的操作。

```text
total_budget = 1200 ms  # 演算值
remaining = deadline - now
if remaining <= minimal_attempt_budget:
    stop starting new attempts
else:
    call with bounded connect and read timeouts
```

用两个无真实业务数据的服务复现故障，分别记录入口等待、每次下游尝试与最终响应。配置在版本间可能变化，应核对依赖组合与实际生效值。

## 3. 用对照区分原因

下表列出需要主动改变的条件。预期行为来自机制分析，复现时还需记录运行环境和原始输出，不能将预期当作已经测得的结果。

| 改变的条件 | 需要验证的行为 |
| --- | --- |
| 每层都独立重试两次 | 总尝试数可能成倍放大 |
| 外层已超时而内层仍执行 | 需要观察残留资源与副作用 |
| 剩余预算不足再重试 | 可能只增加无效负载 |

### 对照 1：每层都独立重试两次

总尝试数可能成倍放大。观察时记录各层尝试次数的组合。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 2：外层已超时而内层仍执行

需要观察残留资源与副作用。观察时记录请求返回与后台结束时刻。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 3：剩余预算不足再重试

可能只增加无效负载。观察时记录截止时间与最小可用尝试时间。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。

## 4. 适用条件与取舍

预算数字需要业务体验和实测支持。不能把示例值直接当生产标准，慢操作可能更适合异步任务与结果查询。

一次正常运行只覆盖了这组输入。继续扩展前，应把上面的异常对照保留下来，尤其关注“剩余预算不足再重试”这一分支。后续方案若改变了图中任意一处依赖，原来的判断就要重新验证，不能仅凭界面相似或返回值相同沿用结论。

## 同月延伸

- [Spring Cloud Zuul：路径转发与业务权限的边界](/tech/2016/07/05/cloud-brixton-zuul-routing/)
- [Spring Cloud 隔离：慢服务不能占满全部请求容量](/tech/2016/07/25/cloud-bulkhead-fallback-capacity/)

## 参考资料

1. [Spring Cloud Brixton 发布说明](https://spring.io/blog/2016/05/11/spring-cloud-brixton-release-is-available/)
2. [Spring Cloud Netflix 历史源码](https://github.com/spring-cloud/spring-cloud-netflix/tree/v1.1.0.RELEASE)
