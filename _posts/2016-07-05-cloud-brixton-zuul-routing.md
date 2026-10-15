---
layout: post
title: Spring Cloud Zuul：路径转发与业务权限的边界
subtitle: 网关能把请求转到服务，不代表被调接口就可以省略数据权限检查。
date: 2016-07-05 08:00:00 +0800
author: edyang
header-style: text
catalog: true
tags:
- Spring Cloud
- 服务治理
tech_note: true
note_id: cloud-brixton-zuul-routing
permalink: /tech/2016/07/05/cloud-brixton-zuul-routing/
excerpt: 网关能把请求转到服务，不代表被调接口就可以省略数据权限检查。
privacy_reviewed: true
content_revision: 3
images:
- /img/tech-notes/cloud-brixton-zuul-routing.svg
technology_since: '2016-05-11'
---

网关能把请求转到服务，不代表被调接口就可以省略数据权限检查。

本文使用Spring Cloud Brixton 与匹配的 Spring Boot 1.3，示例为调用流程。服务治理需要同时考虑入口、调用链和下游容量。本文讨论 Zuul、Ribbon 与 Hystrix 这一时期的技术组合，不引入后续的网关和容错框架。

## 1. 从现象推到机制

Zuul（入口路由组件）根据路径等规则选择后端，可能改变前缀和头信息。认证信息需要通过可信方式传递，不能让外部任意伪造内部身份头。网关路由错误与业务服务拒绝应分别记录。

![Spring Cloud Zuul：路径转发与业务权限的边界的处理、反馈与观察关系](/img/tech-notes/cloud-brixton-zuul-routing.svg)

图中的四个节点分别表示外部请求、路由规则、内部请求、服务权限。顺着实线检查输入如何变成输出，再沿虚线核对反馈条件。图示表达的是本文讨论的关系，不是实测曲线或现场截图。

## 2. 最小实现与输入条件

先用两个只读演示路径核对转发后的真实 URL。让后端输出受控请求信息，验证路径前缀和可信身份来源。

```text
external /api/orders/*
 -> gateway route and prefix rule
 -> internal order service path
 -> service authorization and query scope
```

用两个无真实业务数据的服务复现故障，分别记录入口等待、每次下游尝试与最终响应。配置在版本间可能变化，应核对依赖组合与实际生效值。

## 3. 用对照区分原因

下表列出需要主动改变的条件。预期行为来自机制分析，复现时还需记录运行环境和原始输出，不能将预期当作已经测得的结果。

| 改变的条件 | 需要验证的行为 |
| --- | --- |
| 路由前缀被移除 | 后端实际路径可能不同 |
| 客户端伪造身份头 | 网关应清理或重新生成可信字段 |
| 后端返回权限错误 | 不能误报为网关不可达 |

### 对照 1：路由前缀被移除

后端实际路径可能不同。观察时记录网关转发日志与服务入口日志。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 2：客户端伪造身份头

网关应清理或重新生成可信字段。观察时记录外部原始头与内部接收头。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 3：后端返回权限错误

不能误报为网关不可达。观察时记录状态码来源与关联日志。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。

## 4. 适用条件与取舍

网关集中入口有运行价值，也会成为共享依赖。核心服务仍要保持明确接口契约，避免把所有业务逻辑塞进入口过滤器。

一次正常运行只覆盖了这组输入。继续扩展前，应把上面的异常对照保留下来，尤其关注“后端返回权限错误”这一分支。后续方案若改变了图中任意一处依赖，原来的判断就要重新验证，不能仅凭界面相似或返回值相同沿用结论。

## 同月延伸

- [Spring Cloud 调用链：每层超时要服从总预算](/tech/2016/07/15/cloud-timeout-total-budget/)
- [Spring Cloud 隔离：慢服务不能占满全部请求容量](/tech/2016/07/25/cloud-bulkhead-fallback-capacity/)

## 参考资料

1. [Spring Cloud Brixton 发布说明](https://spring.io/blog/2016/05/11/spring-cloud-brixton-release-is-available/)
2. [Spring Cloud Netflix 历史源码](https://github.com/spring-cloud/spring-cloud-netflix/tree/v1.1.0.RELEASE)
