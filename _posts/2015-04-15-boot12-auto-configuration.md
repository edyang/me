---
layout: post
title: Spring Boot 深入：自动配置为何会生效或退让
subtitle: 添加一个依赖后行为变了，往往是自动配置条件被满足。
date: 2015-04-15 08:00:00 +0800
author: edyang
header-style: text
catalog: true
tags:
- Spring Boot
- Java
tech_note: true
note_id: boot12-auto-configuration
permalink: /tech/2015/04/15/boot12-auto-configuration/
excerpt: 添加一个依赖后行为变了，往往是自动配置条件被满足。
privacy_reviewed: true
content_revision: 3
images:
- /img/tech-notes/boot12-auto-configuration.svg
technology_since: '2015-02-27'
---

添加一个依赖后行为变了，往往是自动配置条件被满足。理解条件，比记住默认行为更可靠。

本文使用JDK 7、Maven 与 Spring Boot 1.2.2.RELEASE，代码为工程片段。Spring Boot（约定化应用框架）减少常见装配代码，但自动配置仍有条件和来源。本文使用一代框架的属性与接口，不混入后续版本的配置名称。

## 1. 从现象推到机制

自动配置可以根据类存在、属性值和已有 Bean 决定是否生效。用户显式提供的组件可能让默认配置退让，但具体规则要看对应配置类。排除一个自动配置之前，应先找出它为什么被匹配。

![Spring Boot 深入：自动配置为何会生效或退让的处理、反馈与观察关系](/img/tech-notes/boot12-auto-configuration.svg)

图中的四个节点分别表示类路径、条件判断、默认组件、用户配置。顺着实线检查输入如何变成输出，再沿虚线核对反馈条件。图示表达的是本文讨论的关系，不是实测曲线或现场截图。

## 2. 最小实现与输入条件

用 debug 启动演示工程查看条件报告，再分别添加依赖和自定义 Bean 比较。一次只改一项，避免同时变更多个前提。

```bash
java -jar target/demo.jar --debug
# 对照自动配置报告中的匹配与未匹配条件
# 再检查实际注册的目标 Bean
```

工程需要声明匹配版本的 parent、starter 与 Maven 插件。运行时保留依赖树和实际生效配置，在控制台日志与真实请求之间建立对应，不能只根据启动横幅判断服务可用。

## 3. 用对照区分原因

下表列出需要主动改变的条件。预期行为来自机制分析，复现时还需记录运行环境和原始输出，不能将预期当作已经测得的结果。

| 改变的条件 | 需要验证的行为 |
| --- | --- |
| 类路径增加数据库组件 | 相关自动配置可能开始匹配 |
| 显式声明同类基础设施 Bean | 默认实现可能按条件退让 |
| 排除配置但业务仍依赖它 | 可能出现缺少组件错误 |

### 对照 1：类路径增加数据库组件

相关自动配置可能开始匹配。观察时记录条件报告与依赖树。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 2：显式声明同类基础设施 Bean

默认实现可能按条件退让。观察时记录具体 Conditional 条件。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 3：排除配置但业务仍依赖它

可能出现缺少组件错误。观察时记录依赖链与启动异常。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。

## 4. 适用条件与取舍

自动配置不是隐藏魔法，也不意味着可以忽略框架版本。升级依赖后，条件和默认值可能变化，应保留有效配置的证据。

一次正常运行只覆盖了这组输入。继续扩展前，应把上面的异常对照保留下来，尤其关注“排除配置但业务仍依赖它”这一分支。后续方案若改变了图中任意一处依赖，原来的判断就要重新验证，不能仅凭界面相似或返回值相同沿用结论。

## 同月延伸

- [Spring Boot 入门：从一个可执行 Web 工程开始](/tech/2015/04/05/boot12-minimal-web-project/)
- [Spring Boot 配置：同一个端口为什么读取了另一个值](/tech/2015/04/25/boot12-configuration-precedence/)

## 参考资料

1. [Spring Boot 1.2.2 参考指南](https://docs.spring.io/spring-boot/docs/1.2.2.RELEASE/reference/htmlsingle/)
2. [Spring Boot 1.0 正式发布](https://spring.io/blog/2014/04/01/spring-boot-1-0-ga-released/)
