---
layout: post
title: Spring Cloud 学习：跨服务排查先打通请求身份
subtitle: 一个请求经过多个服务，只靠各自本地时间搜索日志，很难还原完整路径。
date: 2015-12-25 08:00:00 +0800
author: edyang
header-style: text
catalog: true
tags:
- Spring Cloud
- 分布式系统
tech_note: true
note_id: cloud10-distributed-request-trace
permalink: /tech/2015/12/25/cloud10-distributed-request-trace/
excerpt: 一个请求经过多个服务，只靠各自本地时间搜索日志，很难还原完整路径。
privacy_reviewed: true
content_revision: 3
images:
- /img/tech-notes/cloud10-distributed-request-trace.svg
technology_since: '2015-03-04'
---

一个请求经过多个服务，只靠各自本地时间搜索日志，很难还原完整路径。

本文使用Spring Cloud 1.0 系列与其匹配的 Spring Boot 1.2，配置为结构片段。Spring Cloud（分布式应用工具集）把配置、注册、调用和容错连接起来，但远程调用依然会超时或产生不确定结果。服务拆分之前先明确每个数据的归属。

## 1. 从现象推到机制

入口生成关联身份，向下游显式传递，各服务记录本地阶段与耗时。业务订单号与技术请求号分别保留，重试还应有尝试序号。不同机器时钟可能有偏差，不能单靠时间戳排序推断严格因果。

![Spring Cloud 学习：跨服务排查先打通请求身份的处理、反馈与观察关系](/img/tech-notes/cloud10-distributed-request-trace.svg)

图中的四个节点分别表示入口身份、同步调用、异步任务、日志还原。顺着实线检查输入如何变成输出，再沿虚线核对反馈条件。图示表达的是本文讨论的关系，不是实测曲线或现场截图。

## 2. 最小实现与输入条件

先用自定义请求头和日志字段完成最小关联，不依赖尚未引入的后续追踪产品。异步线程需要显式传递并清理上下文。

```text
X-Request-Id: demo-request-42
service: order -> catalog
attempt: 1
record: start, duration, outcome
# 异步执行时显式复制必要上下文
```

从两个演示服务开始，先直连验证业务，再逐项加入基础设施。固定依赖版本组合，记录调用方与被调方日志；基础设施正常不等于每个业务接口都可用。

## 3. 用对照区分原因

下表列出需要主动改变的条件。预期行为来自机制分析，复现时还需记录运行环境和原始输出，不能将预期当作已经测得的结果。

| 改变的条件 | 需要验证的行为 |
| --- | --- |
| 同请求跨两个服务 | 日志应能用相同关联号串起 |
| 调用方发生重试 | 每次尝试要能分别识别 |
| 线程复用处理另一请求 | 不得沿用上一请求字段 |

### 对照 1：同请求跨两个服务

日志应能用相同关联号串起。观察时记录入口传入与下游记录。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 2：调用方发生重试

每次尝试要能分别识别。观察时记录相同请求号下的尝试序号。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 3：线程复用处理另一请求

不得沿用上一请求字段。观察时记录上下文清理与实际日志。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。

## 4. 适用条件与取舍

技术关联号不能作为权限凭据。外部传入值也应限制长度与字符范围，防止污染日志或制造无法检索的内容。

一次正常运行只覆盖了这组输入。继续扩展前，应把上面的异常对照保留下来，尤其关注“线程复用处理另一请求”这一分支。后续方案若改变了图中任意一处依赖，原来的判断就要重新验证，不能仅凭界面相似或返回值相同沿用结论。

## 同月延伸

- [Spring Cloud Config：配置仓库也要有版本依据](/tech/2015/12/05/cloud10-config-version/)
- [Spring Cloud Hystrix：隔离和降级不能伪造成功](/tech/2015/12/15/cloud10-hystrix-isolation/)

## 参考资料

1. [Spring Cloud 1.0 正式发布](https://spring.io/blog/2015/03/04/spring-cloud-1-0-0-available-now/)
2. [Spring Cloud Netflix 1.0 源码](https://github.com/spring-cloud/spring-cloud-netflix/tree/v1.0.0.RELEASE)
