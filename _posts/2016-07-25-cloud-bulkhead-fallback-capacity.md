---
layout: post
title: Spring Cloud 隔离：慢服务不能占满全部请求容量
subtitle: 多个接口共享一个执行池，一个非关键依赖变慢后，也可能挤占关键业务的线程。
date: 2016-07-25 08:00:00 +0800
author: edyang
header-style: text
catalog: true
tags:
- Spring Cloud
- 服务治理
tech_note: true
note_id: cloud-bulkhead-fallback-capacity
permalink: /tech/2016/07/25/cloud-bulkhead-fallback-capacity/
excerpt: 多个接口共享一个执行池，一个非关键依赖变慢后，也可能挤占关键业务的线程。
privacy_reviewed: true
content_revision: 3
images:
- /img/tech-notes/cloud-bulkhead-fallback-capacity.svg
technology_since: '2016-05-11'
---

多个接口共享一个执行池，一个非关键依赖变慢后，也可能挤占关键业务的线程。

本文使用Spring Cloud Brixton 与匹配的 Spring Boot 1.3，示例为调用流程。服务治理需要同时考虑入口、调用链和下游容量。本文讨论 Zuul、Ribbon 与 Hystrix 这一时期的技术组合，不引入后续的网关和容错框架。

## 1. 从现象推到机制

舱壁式隔离把不同依赖的并发资源分开，限制故障影响面。隔离池过小会过早拒绝，过大则让故障占用更多资源。降级路径也可能调用慢资源，若没有独立预算，降级本身仍会拖住系统。

![Spring Cloud 隔离：慢服务不能占满全部请求容量的处理、反馈与观察关系](/img/tech-notes/cloud-bulkhead-fallback-capacity.svg)

图中的四个节点分别表示依赖分类、有限执行池、故障隔离、廉价降级。顺着实线检查输入如何变成输出，再沿虚线核对反馈条件。图示表达的是本文讨论的关系，不是实测曲线或现场截图。

## 2. 最小实现与输入条件

用推荐查询和核心订单查询两组演示流量，分别观察池占用。让推荐依赖变慢，核对订单链路是否仍在自身容量内运行。

```text
recommendation -> bounded pool A
order lookup -> bounded pool B
fallback -> cheap local result or explicit unavailable
measure each pool: active, queued, rejected
```

用两个无真实业务数据的服务复现故障，分别记录入口等待、每次下游尝试与最终响应。配置在版本间可能变化，应核对依赖组合与实际生效值。

## 3. 用对照区分原因

下表列出需要主动改变的条件。预期行为来自机制分析，复现时还需记录运行环境和原始输出，不能将预期当作已经测得的结果。

| 改变的条件 | 需要验证的行为 |
| --- | --- |
| 推荐依赖持续阻塞 | 应主要影响它所属隔离容量 |
| 降级还访问同一故障资源 | 可能继续失败或排队 |
| 核心池设置过小 | 正常业务也可能被拒绝 |

### 对照 1：推荐依赖持续阻塞

应主要影响它所属隔离容量。观察时记录各池活动数与拒绝数。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 2：降级还访问同一故障资源

可能继续失败或排队。观察时记录fallback 的依赖路径。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 3：核心池设置过小

正常业务也可能被拒绝。观察时记录正常负载下的容量与延迟。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。

## 4. 适用条件与取舍

隔离不能创造处理能力，只能限制共享损害。需要把资源总预算与依赖容量同时考虑，避免无限增加线程池。

一次正常运行只覆盖了这组输入。继续扩展前，应把上面的异常对照保留下来，尤其关注“核心池设置过小”这一分支。后续方案若改变了图中任意一处依赖，原来的判断就要重新验证，不能仅凭界面相似或返回值相同沿用结论。

## 同月延伸

- [Spring Cloud Zuul：路径转发与业务权限的边界](/tech/2016/07/05/cloud-brixton-zuul-routing/)
- [Spring Cloud 调用链：每层超时要服从总预算](/tech/2016/07/15/cloud-timeout-total-budget/)

## 参考资料

1. [Spring Cloud Brixton 发布说明](https://spring.io/blog/2016/05/11/spring-cloud-brixton-release-is-available/)
2. [Spring Cloud Netflix 历史源码](https://github.com/spring-cloud/spring-cloud-netflix/tree/v1.1.0.RELEASE)
