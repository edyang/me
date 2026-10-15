---
layout: post
title: Spring Boot：把零散配置收敛成有类型的对象
subtitle: 配置散落在多个字符串读取语句中，字段拼错和单位不一致都难以及时发现。
date: 2015-06-05 08:00:00 +0800
author: edyang
header-style: text
catalog: true
tags:
- Spring Boot
- Java
tech_note: true
note_id: boot12-configuration-properties
permalink: /tech/2015/06/05/boot12-configuration-properties/
excerpt: 配置散落在多个字符串读取语句中，字段拼错和单位不一致都难以及时发现。
privacy_reviewed: true
content_revision: 3
images:
- /img/tech-notes/boot12-configuration-properties.svg
technology_since: '2015-02-27'
---

配置散落在多个字符串读取语句中，字段拼错和单位不一致都难以及时发现。

本文使用JDK 7、Maven 与 Spring Boot 1.2.2.RELEASE，代码为工程片段。Spring Boot（约定化应用框架）减少常见装配代码，但自动配置仍有条件和来源。本文使用一代框架的属性与接口，不混入后续版本的配置名称。

## 1. 从现象推到机制

ConfigurationProperties（配置属性绑定）把同一前缀的参数绑定到对象，便于集中声明和校验。字段类型能发现部分格式问题，但不能自动识别业务单位，例如超时值究竟是毫秒还是秒。

![Spring Boot：把零散配置收敛成有类型的对象的处理、反馈与观察关系](/img/tech-notes/boot12-configuration-properties.svg)

图中的四个节点分别表示属性前缀、类型绑定、条件校验、组件使用。顺着实线检查输入如何变成输出，再沿虚线核对反馈条件。图示表达的是本文讨论的关系，不是实测曲线或现场截图。

## 2. 最小实现与输入条件

给演示通道配置单独前缀与类型，按一代框架方式注册 Bean。设置默认值的同时，关键字段缺失应在启动时失败。

```java
@Component
@ConfigurationProperties(prefix="demo.channel")
public class ChannelProperties {
  private int timeoutMillis = 1000;
  // getter / setter
}
```

工程需要声明匹配版本的 parent、starter 与 Maven 插件。运行时保留依赖树和实际生效配置，在控制台日志与真实请求之间建立对应，不能只根据启动横幅判断服务可用。

## 3. 用对照区分原因

下表列出需要主动改变的条件。预期行为来自机制分析，复现时还需记录运行环境和原始输出，不能将预期当作已经测得的结果。

| 改变的条件 | 需要验证的行为 |
| --- | --- |
| 数字字段填写非数字 | 应尽早发现绑定错误 |
| 单位被误解为秒 | 类型正确仍会形成错误等待 |
| 关键地址没有设置 | 不能悄悄使用不可控默认值 |

### 对照 1：数字字段填写非数字

应尽早发现绑定错误。观察时记录启动异常与目标字段。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 2：单位被误解为秒

类型正确仍会形成错误等待。观察时记录字段命名与实际单位。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 3：关键地址没有设置

不能悄悄使用不可控默认值。观察时记录必填校验与最终配置。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。

## 4. 适用条件与取舍

配置对象不应通过公开接口完整序列化。含凭据的属性应限制访问与日志展示，配置集中也不等于可以公开。

一次正常运行只覆盖了这组输入。继续扩展前，应把上面的异常对照保留下来，尤其关注“关键地址没有设置”这一分支。后续方案若改变了图中任意一处依赖，原来的判断就要重新验证，不能仅凭界面相似或返回值相同沿用结论。

## 同月延伸

- [Spring Boot 部署：可执行 jar 与外部配置](/tech/2015/06/15/boot12-executable-jar-deployment/)
- [Spring Boot 测试：不要每个规则都启动整个容器](/tech/2015/06/25/boot12-test-layering/)

## 参考资料

1. [Spring Boot 1.2.2 参考指南](https://docs.spring.io/spring-boot/docs/1.2.2.RELEASE/reference/htmlsingle/)
2. [Spring Boot 1.0 正式发布](https://spring.io/blog/2014/04/01/spring-boot-1-0-ga-released/)
