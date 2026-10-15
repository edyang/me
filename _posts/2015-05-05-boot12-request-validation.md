---
layout: post
title: Spring Boot Web：表单校验与业务校验分层
subtitle: 接口接受了 JSON，并不表示其中所有值都能用于业务写入。
date: 2015-05-05 08:00:00 +0800
author: edyang
header-style: text
catalog: true
tags:
- Spring Boot
- Java
tech_note: true
note_id: boot12-request-validation
permalink: /tech/2015/05/05/boot12-request-validation/
excerpt: 接口接受了 JSON，并不表示其中所有值都能用于业务写入。
privacy_reviewed: true
content_revision: 3
images:
- /img/tech-notes/boot12-request-validation.svg
technology_since: '2015-02-27'
---

接口接受了 JSON，并不表示其中所有值都能用于业务写入。输入结构和业务规则需要分别验证。

本文使用JDK 7、Maven 与 Spring Boot 1.2.2.RELEASE，代码为工程片段。Spring Boot（约定化应用框架）减少常见装配代码，但自动配置仍有条件和来源。本文使用一代框架的属性与接口，不混入后续版本的配置名称。

## 1. 从现象推到机制

反序列化负责数据类型，Bean Validation（对象校验）负责声明性约束，服务层负责跨字段规则与对象权限。控制器直接使用持久化实体，会扩大外部可写字段范围。

![Spring Boot Web：表单校验与业务校验分层的处理、反馈与观察关系](/img/tech-notes/boot12-request-validation.svg)

图中的四个节点分别表示JSON 输入、请求校验、业务规则、事务写入。顺着实线检查输入如何变成输出，再沿虚线核对反馈条件。图示表达的是本文讨论的关系，不是实测曲线或现场截图。

## 2. 最小实现与输入条件

为创建订单建立专用请求类，只接受商品和数量。价格由服务端查询，不能把客户端金额当作可信成交价。

```java
public class CreateOrderRequest {
  @NotNull private Long itemId;
  @NotNull @Min(1) private Integer quantity;
  // getters / setters
}
```

工程需要声明匹配版本的 parent、starter 与 Maven 插件。运行时保留依赖树和实际生效配置，在控制台日志与真实请求之间建立对应，不能只根据启动横幅判断服务可用。

## 3. 用对照区分原因

下表列出需要主动改变的条件。预期行为来自机制分析，复现时还需记录运行环境和原始输出，不能将预期当作已经测得的结果。

| 改变的条件 | 需要验证的行为 |
| --- | --- |
| 数量小于一 | 应返回输入错误而非写入订单 |
| 客户端提交折后金额 | 不能直接覆盖服务端计价 |
| 商品不属于可售范围 | 需要业务规则拒绝 |

### 对照 1：数量小于一

应返回输入错误而非写入订单。观察时记录约束校验结果。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 2：客户端提交折后金额

不能直接覆盖服务端计价。观察时记录价格来源与计算路径。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 3：商品不属于可售范围

需要业务规则拒绝。观察时记录查询可见性和销售状态。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。

## 4. 适用条件与取舍

声明性校验无法表达所有一致性条件。库存和重复创建等并发规则，还应由数据库条件与唯一约束兜底。

一次正常运行只覆盖了这组输入。继续扩展前，应把上面的异常对照保留下来，尤其关注“商品不属于可售范围”这一分支。后续方案若改变了图中任意一处依赖，原来的判断就要重新验证，不能仅凭界面相似或返回值相同沿用结论。

## 同月延伸

- [Spring Boot 数据访问：事务要放在业务边界](/tech/2015/05/15/boot12-jdbc-transaction/)
- [Spring Boot Actuator：健康响应要说明检查了什么](/tech/2015/05/25/boot12-health-endpoint/)

## 参考资料

1. [Spring Boot 1.2.2 参考指南](https://docs.spring.io/spring-boot/docs/1.2.2.RELEASE/reference/htmlsingle/)
2. [Spring Boot 1.0 正式发布](https://spring.io/blog/2014/04/01/spring-boot-1-0-ga-released/)
