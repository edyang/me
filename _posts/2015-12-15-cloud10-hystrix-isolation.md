---
layout: post
title: Spring Cloud Hystrix：隔离和降级不能伪造成功
subtitle: 一个慢依赖占满线程后，可能拖垮原本不依赖它的请求。
date: 2015-12-15 08:00:00 +0800
author: edyang
header-style: text
catalog: true
tags:
- Spring Cloud
- 分布式系统
tech_note: true
note_id: cloud10-hystrix-isolation
permalink: /tech/2015/12/15/cloud10-hystrix-isolation/
excerpt: 一个慢依赖占满线程后，可能拖垮原本不依赖它的请求。
privacy_reviewed: true
content_revision: 3
images:
- /img/tech-notes/cloud10-hystrix-isolation.svg
technology_since: '2015-03-04'
---

一个慢依赖占满线程后，可能拖垮原本不依赖它的请求。隔离限制故障传播范围。

本文使用Spring Cloud 1.0 系列与其匹配的 Spring Boot 1.2，配置为结构片段。Spring Cloud（分布式应用工具集）把配置、注册、调用和容错连接起来，但远程调用依然会超时或产生不确定结果。服务拆分之前先明确每个数据的归属。

## 1. 从现象推到机制

Hystrix（容错隔离组件）围绕命令提供超时、隔离和熔断等机制。fallback（降级返回）应表达有限能力或暂不可用，而不是返回一份假成功订单。超时后底层操作是否停止，仍取决于执行实现。

![Spring Cloud Hystrix：隔离和降级不能伪造成功的处理、反馈与观察关系](/img/tech-notes/cloud10-hystrix-isolation.svg)

图中的四个节点分别表示远程命令、资源隔离、熔断判断、降级结果。顺着实线检查输入如何变成输出，再沿虚线核对反馈条件。图示表达的是本文讨论的关系，不是实测曲线或现场截图。

## 2. 最小实现与输入条件

用只读推荐列表做演示，依赖失败时返回明确空推荐或缓存标记。支付、扣库存等写操作不能靠固定默认值假装完成。

```text
normal: fetch recommendations within budget
fallback: return empty recommendations with degraded flag
critical write: return pending / unavailable by business contract
```

从两个演示服务开始，先直连验证业务，再逐项加入基础设施。固定依赖版本组合，记录调用方与被调方日志；基础设施正常不等于每个业务接口都可用。

## 3. 用对照区分原因

下表列出需要主动改变的条件。预期行为来自机制分析，复现时还需记录运行环境和原始输出，不能将预期当作已经测得的结果。

| 改变的条件 | 需要验证的行为 |
| --- | --- |
| 依赖持续变慢 | 隔离容量与超时限制占用 |
| 熔断打开 | 部分请求不再访问故障依赖 |
| 关键写入进入降级 | 不能伪装成已完成 |

### 对照 1：依赖持续变慢

隔离容量与超时限制占用。观察时记录命令耗时和线程池占用。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 2：熔断打开

部分请求不再访问故障依赖。观察时记录短路次数与恢复试探。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 3：关键写入进入降级

不能伪装成已完成。观察时记录真实业务状态与返回语义。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。

## 4. 适用条件与取舍

熔断阈值需要实际负载支持。过低会误伤短暂波动，过高则无法及时限制传播；还要监控恢复试探是否真的改善。

一次正常运行只覆盖了这组输入。继续扩展前，应把上面的异常对照保留下来，尤其关注“关键写入进入降级”这一分支。后续方案若改变了图中任意一处依赖，原来的判断就要重新验证，不能仅凭界面相似或返回值相同沿用结论。

## 同月延伸

- [Spring Cloud Config：配置仓库也要有版本依据](/tech/2015/12/05/cloud10-config-version/)
- [Spring Cloud 学习：跨服务排查先打通请求身份](/tech/2015/12/25/cloud10-distributed-request-trace/)

## 参考资料

1. [Spring Cloud 1.0 正式发布](https://spring.io/blog/2015/03/04/spring-cloud-1-0-0-available-now/)
2. [Spring Cloud Netflix 1.0 源码](https://github.com/spring-cloud/spring-cloud-netflix/tree/v1.0.0.RELEASE)
