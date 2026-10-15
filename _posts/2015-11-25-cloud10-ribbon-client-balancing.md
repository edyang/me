---
layout: post
title: Spring Cloud Ribbon：负载均衡选中实例以后仍可能失败
subtitle: 客户端负载均衡把请求分配给实例，不会自动消除单个实例的故障和请求副作用。
date: 2015-11-25 08:00:00 +0800
author: edyang
header-style: text
catalog: true
tags:
- Spring Cloud
- 分布式系统
tech_note: true
note_id: cloud10-ribbon-client-balancing
permalink: /tech/2015/11/25/cloud10-ribbon-client-balancing/
excerpt: 客户端负载均衡把请求分配给实例，不会自动消除单个实例的故障和请求副作用。
privacy_reviewed: true
content_revision: 3
images:
- /img/tech-notes/cloud10-ribbon-client-balancing.svg
technology_since: '2015-03-04'
---

客户端负载均衡把请求分配给实例，不会自动消除单个实例的故障和请求副作用。

本文使用Spring Cloud 1.0 系列与其匹配的 Spring Boot 1.2，配置为结构片段。Spring Cloud（分布式应用工具集）把配置、注册、调用和容错连接起来，但远程调用依然会超时或产生不确定结果。服务拆分之前先明确每个数据的归属。

## 1. 从现象推到机制

Ribbon（客户端负载均衡）从实例列表选择目标，连接与读取仍有独立超时。重试其他实例对只读查询通常较容易，但对写请求可能造成重复执行。实例列表陈旧时，也可能选到已经不可用的地址。

![Spring Cloud Ribbon：负载均衡选中实例以后仍可能失败的处理、反馈与观察关系](/img/tech-notes/cloud10-ribbon-client-balancing.svg)

图中的四个节点分别表示逻辑服务名、实例视图、选择策略、失败分类。顺着实线检查输入如何变成输出，再沿虚线核对反馈条件。图示表达的是本文讨论的关系，不是实测曲线或现场截图。

## 2. 最小实现与输入条件

以只读商品查询演示两个实例，分别返回实例标识。关闭一个实例后记录选择、连接失败与重试行为，避免用写入接口测试自动重试。

```text
logical service name
 -> available instance view
 -> choose instance
 -> connect / read with bounded timeouts
 -> classify failure before retry
```

从两个演示服务开始，先直连验证业务，再逐项加入基础设施。固定依赖版本组合，记录调用方与被调方日志；基础设施正常不等于每个业务接口都可用。

## 3. 用对照区分原因

下表列出需要主动改变的条件。预期行为来自机制分析，复现时还需记录运行环境和原始输出，不能将预期当作已经测得的结果。

| 改变的条件 | 需要验证的行为 |
| --- | --- |
| 两个实例都可用 | 请求分布应按实际策略观察 |
| 一个实例连接失败 | 失败处理受超时和重试配置影响 |
| 写操作已执行但响应丢失 | 换实例重试可能重复写入 |

### 对照 1：两个实例都可用

请求分布应按实际策略观察。观察时记录每次响应的实例标识。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 2：一个实例连接失败

失败处理受超时和重试配置影响。观察时记录尝试次数与总耗时。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 3：写操作已执行但响应丢失

换实例重试可能重复写入。观察时记录业务幂等键与原执行结果。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。

## 4. 适用条件与取舍

平均分配不是唯一目标。慢实例、连接复用与请求耗时分布都会影响体验，应看尾部延迟与错误率，而非只看实例请求数。

一次正常运行只覆盖了这组输入。继续扩展前，应把上面的异常对照保留下来，尤其关注“写操作已执行但响应丢失”这一分支。后续方案若改变了图中任意一处依赖，原来的判断就要重新验证，不能仅凭界面相似或返回值相同沿用结论。

## 同月延伸

- [Spring Cloud 学习：先划服务边界，再接注册中心](/tech/2015/11/05/cloud10-service-boundary/)
- [Spring Cloud Eureka：注册成功不等于所有调用方立刻可见](/tech/2015/11/15/cloud10-eureka-eventual-view/)

## 参考资料

1. [Spring Cloud 1.0 正式发布](https://spring.io/blog/2015/03/04/spring-cloud-1-0-0-available-now/)
2. [Spring Cloud Netflix 1.0 源码](https://github.com/spring-cloud/spring-cloud-netflix/tree/v1.0.0.RELEASE)
