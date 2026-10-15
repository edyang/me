---
layout: post
title: Spring AOP 学习：同类内部调用为何绕过事务
subtitle: 方法上有事务注解，运行时却没有预期事务行为，常见原因是调用没有经过代理边界。
date: 2014-04-15 08:00:00 +0800
author: edyang
header-style: text
catalog: true
tags:
- Spring
- Java Web
tech_note: true
note_id: spring-aop-proxy-boundary
permalink: /tech/2014/04/15/spring-aop-proxy-boundary/
excerpt: 方法上有事务注解，运行时却没有预期事务行为，常见原因是调用没有经过代理边界。
privacy_reviewed: true
content_revision: 3
images:
- /img/tech-notes/spring-aop-proxy-boundary.svg
technology_since: '2013-12-12'
---

方法上有事务注解，运行时却没有预期事务行为，常见原因是调用没有经过代理边界。

本文使用JDK 7、Spring Framework 3.2.6 与 Servlet 容器，代码为结构片段。把请求入口、业务服务和数据访问拆开，是为了明确依赖与事务归属。容器能够装配对象，但应用仍须负责业务规则、异常含义和外部资源生命周期。

## 1. 从现象推到机制

基于代理的 AOP（面向切面编程）在外部调用进入代理时织入拦截逻辑。对象内部通过 this 调用另一个方法，不会重新穿过外部代理。代理类型和可代理方法范围也受配置、接口及方法修饰符影响。

![Spring AOP 学习：同类内部调用为何绕过事务的处理、反馈与观察关系](/img/tech-notes/spring-aop-proxy-boundary.svg)

图中的四个节点分别表示外部调用、代理拦截、目标方法、内部调用。顺着实线检查输入如何变成输出，再沿虚线核对反馈条件。图示表达的是本文讨论的关系，不是实测曲线或现场截图。

## 2. 最小实现与输入条件

让控制器从容器取得业务服务，再比较外部调用和内部自调用。事务实际状态要在方法内部记录，不能只看注解存在。

```java
public void outer() {
    this.inner(); // 普通内部调用
}
@Transactional
public void inner() {
    // 数据库操作
}
```

将片段放入匹配版本的 Maven 工程，补齐组件扫描、数据库连接及依赖。验证时通过容器取得对象，区分普通对象调用和代理调用，避免绕过要研究的机制。

## 3. 用对照区分原因

下表列出需要主动改变的条件。预期行为来自机制分析，复现时还需记录运行环境和原始输出，不能将预期当作已经测得的结果。

| 改变的条件 | 需要验证的行为 |
| --- | --- |
| 从容器代理调用事务方法 | 事务拦截器有机会生效 |
| 同类方法用 this 调用 | 不会再次经过外部代理 |
| 手工 new 出服务对象 | 容器切面不会自动附着 |

### 对照 1：从容器代理调用事务方法

事务拦截器有机会生效。观察时记录入口对象是否为代理。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 2：同类方法用 this 调用

不会再次经过外部代理。观察时记录真实调用栈与事务状态。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 3：手工 new 出服务对象

容器切面不会自动附着。观察时记录对象创建来源。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。

## 4. 适用条件与取舍

可将需要独立事务的操作拆到另一个服务边界，但应按业务一致性决定，而不是为了让注解生效随意拆类。

一次正常运行只覆盖了这组输入。继续扩展前，应把上面的异常对照保留下来，尤其关注“手工 new 出服务对象”这一分支。后续方案若改变了图中任意一处依赖，原来的判断就要重新验证，不能仅凭界面相似或返回值相同沿用结论。

## 同月延伸

- [Spring 学习：用构造依赖说明 IoC 的价值](/tech/2014/04/05/spring-ioc-constructor/)
- [Spring 学习：Bean 生命周期与资源释放](/tech/2014/04/25/spring-bean-lifecycle/)

## 参考资料

1. [Spring Framework 3.2.6 参考文档](https://docs.spring.io/spring-framework/docs/3.2.6.RELEASE/spring-framework-reference/htmlsingle/)
2. [Servlet 3.0 规范](https://jcp.org/en/jsr/detail?id=315)
