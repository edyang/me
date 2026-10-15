---
layout: post
title: Spring Boot Actuator：健康响应要说明检查了什么
subtitle: 一个进程能响应 HTTP，不表示数据库和关键依赖已经可用。
date: 2015-05-25 08:00:00 +0800
author: edyang
header-style: text
catalog: true
tags:
- Spring Boot
- Java
tech_note: true
note_id: boot12-health-endpoint
permalink: /tech/2015/05/25/boot12-health-endpoint/
excerpt: 一个进程能响应 HTTP，不表示数据库和关键依赖已经可用。
privacy_reviewed: true
content_revision: 3
images:
- /img/tech-notes/boot12-health-endpoint.svg
technology_since: '2015-02-27'
---

一个进程能响应 HTTP，不表示数据库和关键依赖已经可用。健康接口的含义需要与使用场景匹配。

本文使用JDK 7、Maven 与 Spring Boot 1.2.2.RELEASE，代码为工程片段。Spring Boot（约定化应用框架）减少常见装配代码，但自动配置仍有条件和来源。本文使用一代框架的属性与接口，不混入后续版本的配置名称。

## 1. 从现象推到机制

Actuator（运行管理组件）提供健康与运行信息等端点。不同检查器反映不同依赖，返回内容与访问范围也受安全配置影响。健康检查若执行昂贵查询，反而会在故障时增加压力。

![Spring Boot Actuator：健康响应要说明检查了什么的处理、反馈与观察关系](/img/tech-notes/boot12-health-endpoint.svg)

图中的四个节点分别表示进程响应、依赖检查、健康结果、运维动作。顺着实线检查输入如何变成输出，再沿虚线核对反馈条件。图示表达的是本文讨论的关系，不是实测曲线或现场截图。

## 2. 最小实现与输入条件

在演示环境加入 actuator starter，先从本机请求 /health，再断开一个非生产依赖观察。管理端点应绑定受控入口，不暴露完整环境信息。

```bash
curl -i http://127.0.0.1:8080/health
# Spring Boot 1.2 使用一代管理端点路径
# 不要直接套用后续版本的 /actuator/health
```

工程需要声明匹配版本的 parent、starter 与 Maven 插件。运行时保留依赖树和实际生效配置，在控制台日志与真实请求之间建立对应，不能只根据启动横幅判断服务可用。

## 3. 用对照区分原因

下表列出需要主动改变的条件。预期行为来自机制分析，复现时还需记录运行环境和原始输出，不能将预期当作已经测得的结果。

| 改变的条件 | 需要验证的行为 |
| --- | --- |
| HTTP 正常但数据库不可达 | 含数据库检查时应反映依赖故障 |
| 检查只返回固定字符串 | 只能证明该处理器还在响应 |
| 频繁执行重查询 | 监测本身可能形成额外负载 |

### 对照 1：HTTP 正常但数据库不可达

含数据库检查时应反映依赖故障。观察时记录检查器范围与响应结果。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 2：检查只返回固定字符串

只能证明该处理器还在响应。观察时记录是否真实访问关键依赖。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 3：频繁执行重查询

监测本身可能形成额外负载。观察时记录检查耗时与调用频率。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。

## 4. 适用条件与取舍

存活和业务就绪可以有不同标准。缓存故障是否使服务下线，需要按可降级能力决定，不能套用统一的一票否决规则。

一次正常运行只覆盖了这组输入。继续扩展前，应把上面的异常对照保留下来，尤其关注“频繁执行重查询”这一分支。后续方案若改变了图中任意一处依赖，原来的判断就要重新验证，不能仅凭界面相似或返回值相同沿用结论。

## 同月延伸

- [Spring Boot Web：表单校验与业务校验分层](/tech/2015/05/05/boot12-request-validation/)
- [Spring Boot 数据访问：事务要放在业务边界](/tech/2015/05/15/boot12-jdbc-transaction/)

## 参考资料

1. [Spring Boot 1.2.2 参考指南](https://docs.spring.io/spring-boot/docs/1.2.2.RELEASE/reference/htmlsingle/)
2. [Spring Boot 1.0 正式发布](https://spring.io/blog/2014/04/01/spring-boot-1-0-ga-released/)
