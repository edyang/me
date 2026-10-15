---
layout: post
title: Spring Cloud Config：配置仓库也要有版本依据
subtitle: 配置中心把文件集中起来，但程序究竟读取了哪一版配置，仍需要可追踪。
date: 2015-12-05 08:00:00 +0800
author: edyang
header-style: text
catalog: true
tags:
- Spring Cloud
- 分布式系统
tech_note: true
note_id: cloud10-config-version
permalink: /tech/2015/12/05/cloud10-config-version/
excerpt: 配置中心把文件集中起来，但程序究竟读取了哪一版配置，仍需要可追踪。
privacy_reviewed: true
content_revision: 3
images:
- /img/tech-notes/cloud10-config-version.svg
technology_since: '2015-03-04'
---

配置中心把文件集中起来，但程序究竟读取了哪一版配置，仍需要可追踪。

本文使用Spring Cloud 1.0 系列与其匹配的 Spring Boot 1.2，配置为结构片段。Spring Cloud（分布式应用工具集）把配置、注册、调用和容错连接起来，但远程调用依然会超时或产生不确定结果。服务拆分之前先明确每个数据的归属。

## 1. 从现象推到机制

Config Server（配置服务）按应用、环境与标签等条件提供配置。应用名写错或环境不匹配，可能得到默认集合或缺失内容。配置在仓库有版本，不表示所有运行实例已经同步加载同一版。

![Spring Cloud Config：配置仓库也要有版本依据的处理、反馈与观察关系](/img/tech-notes/cloud10-config-version.svg)

图中的四个节点分别表示配置仓库、选择条件、属性装载、生效验证。顺着实线检查输入如何变成输出，再沿虚线核对反馈条件。图示表达的是本文讨论的关系，不是实测曲线或现场截图。

## 2. 最小实现与输入条件

先用无敏感参数演示应用名与 profile 的选择。记录程序版本、配置来源版本和生效值；凭据不放进公开示例仓库。

```text
application = demo-order
profile = demo
label = reviewed-config-ref
record = application_sha + configuration_ref + effective_values
```

从两个演示服务开始，先直连验证业务，再逐项加入基础设施。固定依赖版本组合，记录调用方与被调方日志；基础设施正常不等于每个业务接口都可用。

## 3. 用对照区分原因

下表列出需要主动改变的条件。预期行为来自机制分析，复现时还需记录运行环境和原始输出，不能将预期当作已经测得的结果。

| 改变的条件 | 需要验证的行为 |
| --- | --- |
| 切换配置分支或标签 | 可能返回另一组属性 |
| 仓库更新但实例未重载 | 运行值可以仍是旧值 |
| 配置缺少必需字段 | 应在启动或绑定阶段失败 |

### 对照 1：切换配置分支或标签

可能返回另一组属性。观察时记录请求选择条件与配置来源。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 2：仓库更新但实例未重载

运行值可以仍是旧值。观察时记录加载时刻与组件生命周期。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 3：配置缺少必需字段

应在启动或绑定阶段失败。观察时记录必填校验与错误信息。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。

## 4. 适用条件与取舍

动态刷新有组件适用范围，不是任意属性都可无损改变。涉及连接池、端口和安全配置时，应明确重建或重启策略。

一次正常运行只覆盖了这组输入。继续扩展前，应把上面的异常对照保留下来，尤其关注“配置缺少必需字段”这一分支。后续方案若改变了图中任意一处依赖，原来的判断就要重新验证，不能仅凭界面相似或返回值相同沿用结论。

## 同月延伸

- [Spring Cloud Hystrix：隔离和降级不能伪造成功](/tech/2015/12/15/cloud10-hystrix-isolation/)
- [Spring Cloud 学习：跨服务排查先打通请求身份](/tech/2015/12/25/cloud10-distributed-request-trace/)

## 参考资料

1. [Spring Cloud 1.0 正式发布](https://spring.io/blog/2015/03/04/spring-cloud-1-0-0-available-now/)
2. [Spring Cloud Netflix 1.0 源码](https://github.com/spring-cloud/spring-cloud-netflix/tree/v1.0.0.RELEASE)
