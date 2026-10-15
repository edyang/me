---
layout: post
title: Spring Boot 数据访问：事务要放在业务边界
subtitle: 一个服务方法先写订单再写明细，需要作为整体成功或整体失败。
date: 2015-05-15 08:00:00 +0800
author: edyang
header-style: text
catalog: true
tags:
- Spring Boot
- Java
tech_note: true
note_id: boot12-jdbc-transaction
permalink: /tech/2015/05/15/boot12-jdbc-transaction/
excerpt: 一个服务方法先写订单再写明细，需要作为整体成功或整体失败。
privacy_reviewed: true
content_revision: 3
images:
- /img/tech-notes/boot12-jdbc-transaction.svg
technology_since: '2015-02-27'
---

一个服务方法先写订单再写明细，需要作为整体成功或整体失败。自动数据源不会替你判断事务范围。

本文使用JDK 7、Maven 与 Spring Boot 1.2.2.RELEASE，代码为工程片段。Spring Boot（约定化应用框架）减少常见装配代码，但自动配置仍有条件和来源。本文使用一代框架的属性与接口，不混入后续版本的配置名称。

## 1. 从现象推到机制

事务管理器围绕受管方法维护数据库事务。默认回滚规则对运行时异常和受检异常有区别，捕获异常后正常返回也会改变拦截器看到的结果。远程接口调用则不属于本地数据库事务。

![Spring Boot 数据访问：事务要放在业务边界的处理、反馈与观察关系](/img/tech-notes/boot12-jdbc-transaction.svg)

图中的四个节点分别表示业务入口、事务拦截、多次写入、提交回滚。顺着实线检查输入如何变成输出，再沿虚线核对反馈条件。图示表达的是本文讨论的关系，不是实测曲线或现场截图。

## 2. 最小实现与输入条件

用同一数据源的两次写入制造第二次失败，分别检查回滚规则和异常传播。通过容器代理调用服务，不要手工 new。

```java
@Transactional(rollbackFor = Exception.class)
public void createOrder(CreateOrderRequest request) throws Exception {
    orderDao.insert(request);
    lineDao.insert(request);
}
```

工程需要声明匹配版本的 parent、starter 与 Maven 插件。运行时保留依赖树和实际生效配置，在控制台日志与真实请求之间建立对应，不能只根据启动横幅判断服务可用。

## 3. 用对照区分原因

下表列出需要主动改变的条件。预期行为来自机制分析，复现时还需记录运行环境和原始输出，不能将预期当作已经测得的结果。

| 改变的条件 | 需要验证的行为 |
| --- | --- |
| 第二条写入违反约束 | 同一事务中的第一条也应回滚 |
| 异常被捕获并正常返回 | 可能导致事务按成功路径提交 |
| 方法内调用外部服务 | 数据库回滚不能撤销远端动作 |

### 对照 1：第二条写入违反约束

同一事务中的第一条也应回滚。观察时记录最终数据库行而非执行过的 SQL。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 2：异常被捕获并正常返回

可能导致事务按成功路径提交。观察时记录异常传播到拦截器的情况。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 3：方法内调用外部服务

数据库回滚不能撤销远端动作。观察时记录外部请求的独立结果。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。

## 4. 适用条件与取舍

事务应尽量短，避免持锁期间等待慢外部依赖。需要跨服务协调时，应明确采用恢复和补偿方案，不把本地注解当成分布式事务。

一次正常运行只覆盖了这组输入。继续扩展前，应把上面的异常对照保留下来，尤其关注“方法内调用外部服务”这一分支。后续方案若改变了图中任意一处依赖，原来的判断就要重新验证，不能仅凭界面相似或返回值相同沿用结论。

## 同月延伸

- [Spring Boot Web：表单校验与业务校验分层](/tech/2015/05/05/boot12-request-validation/)
- [Spring Boot Actuator：健康响应要说明检查了什么](/tech/2015/05/25/boot12-health-endpoint/)

## 参考资料

1. [Spring Boot 1.2.2 参考指南](https://docs.spring.io/spring-boot/docs/1.2.2.RELEASE/reference/htmlsingle/)
2. [Spring Boot 1.0 正式发布](https://spring.io/blog/2014/04/01/spring-boot-1-0-ga-released/)
