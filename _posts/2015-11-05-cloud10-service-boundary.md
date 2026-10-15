---
layout: post
title: Spring Cloud 学习：先划服务边界，再接注册中心
subtitle: 把单体每个模块都拆成服务，可能只增加远程调用和部署成本。
date: 2015-11-05 08:00:00 +0800
author: edyang
header-style: text
catalog: true
tags:
- Spring Cloud
- 分布式系统
tech_note: true
note_id: cloud10-service-boundary
permalink: /tech/2015/11/05/cloud10-service-boundary/
excerpt: 把单体每个模块都拆成服务，可能只增加远程调用和部署成本。
privacy_reviewed: true
content_revision: 3
images:
- /img/tech-notes/cloud10-service-boundary.svg
technology_since: '2015-03-04'
---

把单体每个模块都拆成服务，可能只增加远程调用和部署成本。边界应来自业务与数据责任。

本文使用Spring Cloud 1.0 系列与其匹配的 Spring Boot 1.2，配置为结构片段。Spring Cloud（分布式应用工具集）把配置、注册、调用和容错连接起来，但远程调用依然会超时或产生不确定结果。服务拆分之前先明确每个数据的归属。

## 1. 从现象推到机制

服务需要有相对独立的规则和数据所有权。订单服务若直接写库存库，会破坏边界并制造隐式耦合。跨服务读取与写入不再共享本地事务，超时、重试和补偿成为显式问题。

![Spring Cloud 学习：先划服务边界，再接注册中心的处理、反馈与观察关系](/img/tech-notes/cloud10-service-boundary.svg)

图中的四个节点分别表示业务能力、数据所有权、远程契约、独立交付。顺着实线检查输入如何变成输出，再沿虚线核对反馈条件。图示表达的是本文讨论的关系，不是实测曲线或现场截图。

## 2. 最小实现与输入条件

从订单和商品两个演示服务开始，商品仅提供只读目录查询。先保留订单成交快照，再讨论库存协调，避免一次引入所有分布式问题。

```text
catalog service -> owns current offers
order service -> owns orders and sold snapshots
order -> catalog: read contract
no direct cross-service database writes
```

从两个演示服务开始，先直连验证业务，再逐项加入基础设施。固定依赖版本组合，记录调用方与被调方日志；基础设施正常不等于每个业务接口都可用。

## 3. 用对照区分原因

下表列出需要主动改变的条件。预期行为来自机制分析，复现时还需记录运行环境和原始输出，不能将预期当作已经测得的结果。

| 改变的条件 | 需要验证的行为 |
| --- | --- |
| 只按代码目录机械拆分 | 容易保留跨库强耦合 |
| 商品服务临时不可达 | 订单入口需明确失败或降级 |
| 历史订单展示商品信息 | 应依赖成交事实而非当前详情 |

### 对照 1：只按代码目录机械拆分

容易保留跨库强耦合。观察时记录业务规则与数据写入归属。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 2：商品服务临时不可达

订单入口需明确失败或降级。观察时记录远程依赖超时后的行为。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 3：历史订单展示商品信息

应依赖成交事实而非当前详情。观察时记录快照字段与数据所有权。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。

## 4. 适用条件与取舍

服务拆分会增加运行和协作成本。小团队可以先在单体内建立模块与接口边界，等独立部署需求明确后再拆分。

一次正常运行只覆盖了这组输入。继续扩展前，应把上面的异常对照保留下来，尤其关注“历史订单展示商品信息”这一分支。后续方案若改变了图中任意一处依赖，原来的判断就要重新验证，不能仅凭界面相似或返回值相同沿用结论。

## 同月延伸

- [Spring Cloud Eureka：注册成功不等于所有调用方立刻可见](/tech/2015/11/15/cloud10-eureka-eventual-view/)
- [Spring Cloud Ribbon：负载均衡选中实例以后仍可能失败](/tech/2015/11/25/cloud10-ribbon-client-balancing/)

## 参考资料

1. [Spring Cloud 1.0 正式发布](https://spring.io/blog/2015/03/04/spring-cloud-1-0-0-available-now/)
2. [Spring Cloud Netflix 1.0 源码](https://github.com/spring-cloud/spring-cloud-netflix/tree/v1.0.0.RELEASE)
