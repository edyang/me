---
layout: post
title: Spring Boot 测试：不要每个规则都启动整个容器
subtitle: 业务判断很简单，却每次都启动完整应用，反馈速度会被环境成本拖慢。
date: 2015-06-25 08:00:00 +0800
author: edyang
header-style: text
catalog: true
tags:
- Spring Boot
- Java
tech_note: true
note_id: boot12-test-layering
permalink: /tech/2015/06/25/boot12-test-layering/
excerpt: 业务判断很简单，却每次都启动完整应用，反馈速度会被环境成本拖慢。
privacy_reviewed: true
content_revision: 3
images:
- /img/tech-notes/boot12-test-layering.svg
technology_since: '2015-02-27'
---

业务判断很简单，却每次都启动完整应用，反馈速度会被环境成本拖慢。测试需要按边界选择层级。

本文使用JDK 7、Maven 与 Spring Boot 1.2.2.RELEASE，代码为工程片段。Spring Boot（约定化应用框架）减少常见装配代码，但自动配置仍有条件和来源。本文使用一代框架的属性与接口，不混入后续版本的配置名称。

## 1. 从现象推到机制

纯规则适合普通单元测试，组件装配和事务行为需要相应集成环境，完整 HTTP 路径再由端到端场景覆盖。单元测试不能证明代理事务，容器启动成功也不能证明价格规则正确。

![Spring Boot 测试：不要每个规则都启动整个容器的处理、反馈与观察关系](/img/tech-notes/boot12-test-layering.svg)

图中的四个节点分别表示业务规则、组件边界、HTTP 路径、反馈成本。顺着实线检查输入如何变成输出，再沿虚线核对反馈条件。图示表达的是本文讨论的关系，不是实测曲线或现场截图。

## 2. 最小实现与输入条件

把计价函数从控制器中提取出来，先用普通 JUnit 检查边界。涉及 Spring Boot 1.2 的上下文测试时，使用该版本提供的注解，避免照搬后续测试 API。

```java
@Test
public void zeroQuantityIsRejected() {
    // 直接构造纯业务对象，提供演示输入
    // 断言明确的规则结果或异常
}
```

工程需要声明匹配版本的 parent、starter 与 Maven 插件。运行时保留依赖树和实际生效配置，在控制台日志与真实请求之间建立对应，不能只根据启动横幅判断服务可用。

## 3. 用对照区分原因

下表列出需要主动改变的条件。预期行为来自机制分析，复现时还需记录运行环境和原始输出，不能将预期当作已经测得的结果。

| 改变的条件 | 需要验证的行为 |
| --- | --- |
| 验证纯金额规则 | 普通单元测试即可快速反馈 |
| 验证事务回滚 | 需要真实事务与代理调用路径 |
| 验证 JSON 绑定和状态码 | 需要包含 Web 边界的检查 |

### 对照 1：验证纯金额规则

普通单元测试即可快速反馈。观察时记录输入与规则输出。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 2：验证事务回滚

需要真实事务与代理调用路径。观察时记录提交后数据库状态。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 3：验证 JSON 绑定和状态码

需要包含 Web 边界的检查。观察时记录实际 HTTP 请求响应。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。

## 4. 适用条件与取舍

测试数量不是唯一目标。优先覆盖高影响边界和过去容易出错的行为，避免为每个简单 getter 编写只镜像实现的断言。

一次正常运行只覆盖了这组输入。继续扩展前，应把上面的异常对照保留下来，尤其关注“验证 JSON 绑定和状态码”这一分支。后续方案若改变了图中任意一处依赖，原来的判断就要重新验证，不能仅凭界面相似或返回值相同沿用结论。

## 同月延伸

- [Spring Boot：把零散配置收敛成有类型的对象](/tech/2015/06/05/boot12-configuration-properties/)
- [Spring Boot 部署：可执行 jar 与外部配置](/tech/2015/06/15/boot12-executable-jar-deployment/)

## 参考资料

1. [Spring Boot 1.2.2 参考指南](https://docs.spring.io/spring-boot/docs/1.2.2.RELEASE/reference/htmlsingle/)
2. [Spring Boot 1.0 正式发布](https://spring.io/blog/2014/04/01/spring-boot-1-0-ga-released/)
