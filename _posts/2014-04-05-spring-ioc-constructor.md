---
layout: post
title: Spring 学习：用构造依赖说明 IoC 的价值
subtitle: 对象自己创建数据库访问对象时，业务规则和基础设施容易绑在一起。
date: 2014-04-05 08:00:00 +0800
author: edyang
header-style: text
catalog: true
tags:
- Spring
- Java Web
tech_note: true
note_id: spring-ioc-constructor
permalink: /tech/2014/04/05/spring-ioc-constructor/
excerpt: 对象自己创建数据库访问对象时，业务规则和基础设施容易绑在一起。
privacy_reviewed: true
content_revision: 3
images:
- /img/tech-notes/spring-ioc-constructor.svg
technology_since: '2013-12-12'
---

对象自己创建数据库访问对象时，业务规则和基础设施容易绑在一起。依赖注入让这条关系变得显式。

本文使用JDK 7、Spring Framework 3.2.6 与 Servlet 容器，代码为结构片段。把请求入口、业务服务和数据访问拆开，是为了明确依赖与事务归属。容器能够装配对象，但应用仍须负责业务规则、异常含义和外部资源生命周期。

## 1. 从现象推到机制

IoC（控制反转）把对象装配交给容器，依赖注入则把需要的协作者提供给对象。构造器可以表达必须依赖，便于在不启动整个 Web 容器时替换演示实现。容器管理单例不意味着对象天然线程安全。

![Spring 学习：用构造依赖说明 IoC 的价值的处理、反馈与观察关系](/img/tech-notes/spring-ioc-constructor.svg)

图中的四个节点分别表示业务接口、容器装配、服务实例、替换验证。顺着实线检查输入如何变成输出，再沿虚线核对反馈条件。图示表达的是本文讨论的关系，不是实测曲线或现场截图。

## 2. 最小实现与输入条件

先定义仓储接口，让业务服务通过构造器接收。使用 XML 明确装配，避免把注解扫描范围问题混进基本概念。

```xml
<bean id="repo" class="demo.JdbcOrderRepository"/>
<bean id="service" class="demo.OrderService">
  <constructor-arg ref="repo"/>
</bean>
```

将片段放入匹配版本的 Maven 工程，补齐组件扫描、数据库连接及依赖。验证时通过容器取得对象，区分普通对象调用和代理调用，避免绕过要研究的机制。

## 3. 用对照区分原因

下表列出需要主动改变的条件。预期行为来自机制分析，复现时还需记录运行环境和原始输出，不能将预期当作已经测得的结果。

| 改变的条件 | 需要验证的行为 |
| --- | --- |
| 替换为内存仓储实现 | 服务规则可在相同接口下运行 |
| 遗漏必须依赖 | 应在装配阶段尽早失败 |
| 单例服务保存请求字段 | 不同请求可能互相覆盖 |

### 对照 1：替换为内存仓储实现

服务规则可在相同接口下运行。观察时记录构造依赖是否仍指向接口。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 2：遗漏必须依赖

应在装配阶段尽早失败。观察时记录容器启动异常的真实原因。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 3：单例服务保存请求字段

不同请求可能互相覆盖。观察时记录实例字段是否含用户临时状态。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。

## 4. 适用条件与取舍

依赖注入不会自动改善混乱职责。若服务需要十几个不相关协作者，应重新检查业务边界，而不是只把 new 替换成容器获取。

一次正常运行只覆盖了这组输入。继续扩展前，应把上面的异常对照保留下来，尤其关注“单例服务保存请求字段”这一分支。后续方案若改变了图中任意一处依赖，原来的判断就要重新验证，不能仅凭界面相似或返回值相同沿用结论。

## 同月延伸

- [Spring AOP 学习：同类内部调用为何绕过事务](/tech/2014/04/15/spring-aop-proxy-boundary/)
- [Spring 学习：Bean 生命周期与资源释放](/tech/2014/04/25/spring-bean-lifecycle/)

## 参考资料

1. [Spring Framework 3.2.6 参考文档](https://docs.spring.io/spring-framework/docs/3.2.6.RELEASE/spring-framework-reference/htmlsingle/)
2. [Servlet 3.0 规范](https://jcp.org/en/jsr/detail?id=315)
