---
layout: post
title: Spring Cloud Eureka：注册成功不等于所有调用方立刻可见
subtitle: 服务已经注册，另一端暂时找不到实例，可能是注册、缓存和拉取周期共同作用。
date: 2015-11-15 08:00:00 +0800
author: edyang
header-style: text
catalog: true
tags:
- Spring Cloud
- 分布式系统
tech_note: true
note_id: cloud10-eureka-eventual-view
permalink: /tech/2015/11/15/cloud10-eureka-eventual-view/
excerpt: 服务已经注册，另一端暂时找不到实例，可能是注册、缓存和拉取周期共同作用。
privacy_reviewed: true
content_revision: 3
images:
- /img/tech-notes/cloud10-eureka-eventual-view.svg
technology_since: '2015-03-04'
---

服务已经注册，另一端暂时找不到实例，可能是注册、缓存和拉取周期共同作用。

本文使用Spring Cloud 1.0 系列与其匹配的 Spring Boot 1.2，配置为结构片段。Spring Cloud（分布式应用工具集）把配置、注册、调用和容错连接起来，但远程调用依然会超时或产生不确定结果。服务拆分之前先明确每个数据的归属。

## 1. 从现象推到机制

Eureka（服务注册组件）维护实例信息，客户端还可能保留本地视图。心跳与租约用于判断存活，视图更新存在时间差。注册信息能帮助找到地址，却不能证明目标业务接口当前可用。

![Spring Cloud Eureka：注册成功不等于所有调用方立刻可见的处理、反馈与观察关系](/img/tech-notes/cloud10-eureka-eventual-view.svg)

图中的四个节点分别表示实例注册、注册视图、客户端列表、实际调用。顺着实线检查输入如何变成输出，再沿虚线核对反馈条件。图示表达的是本文讨论的关系，不是实测曲线或现场截图。

## 2. 最小实现与输入条件

启动注册中心和两个演示服务，记录实例身份、注册地址和客户端获取列表时刻。停掉实例后观察视图变化，不把短期缓存视作数据损坏。

```yaml
spring:
  application:
    name: demo-order
eureka:
  client:
    serviceUrl:
      defaultZone: http://127.0.0.1:8761/eureka/
```

从两个演示服务开始，先直连验证业务，再逐项加入基础设施。固定依赖版本组合，记录调用方与被调方日志；基础设施正常不等于每个业务接口都可用。

## 3. 用对照区分原因

下表列出需要主动改变的条件。预期行为来自机制分析，复现时还需记录运行环境和原始输出，不能将预期当作已经测得的结果。

| 改变的条件 | 需要验证的行为 |
| --- | --- |
| 新实例刚注册 | 调用方可能尚未刷新本地列表 |
| 实例心跳停止 | 剔除与客户端感知可能滞后 |
| 注册中心显示正常 | 业务接口仍可能报错 |

### 对照 1：新实例刚注册

调用方可能尚未刷新本地列表。观察时记录注册端与客户端视图时刻。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 2：实例心跳停止

剔除与客户端感知可能滞后。观察时记录租约及列表刷新过程。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 3：注册中心显示正常

业务接口仍可能报错。观察时记录目标端口与实际请求结果。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。

## 4. 适用条件与取舍

不要为了测试方便随意关闭保护机制再直接用于生产。超时和剔除策略要结合故障模型评估，注册中心也需要自己的可用性设计。

一次正常运行只覆盖了这组输入。继续扩展前，应把上面的异常对照保留下来，尤其关注“注册中心显示正常”这一分支。后续方案若改变了图中任意一处依赖，原来的判断就要重新验证，不能仅凭界面相似或返回值相同沿用结论。

## 同月延伸

- [Spring Cloud 学习：先划服务边界，再接注册中心](/tech/2015/11/05/cloud10-service-boundary/)
- [Spring Cloud Ribbon：负载均衡选中实例以后仍可能失败](/tech/2015/11/25/cloud10-ribbon-client-balancing/)

## 参考资料

1. [Spring Cloud 1.0 正式发布](https://spring.io/blog/2015/03/04/spring-cloud-1-0-0-available-now/)
2. [Spring Cloud Netflix 1.0 源码](https://github.com/spring-cloud/spring-cloud-netflix/tree/v1.0.0.RELEASE)
