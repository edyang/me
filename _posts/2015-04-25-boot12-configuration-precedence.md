---
layout: post
title: Spring Boot 配置：同一个端口为什么读取了另一个值
subtitle: 配置文件写了端口，启动后却用了别的值，通常需要查看属性来源与优先级。
date: 2015-04-25 08:00:00 +0800
author: edyang
header-style: text
catalog: true
tags:
- Spring Boot
- Java
tech_note: true
note_id: boot12-configuration-precedence
permalink: /tech/2015/04/25/boot12-configuration-precedence/
excerpt: 配置文件写了端口，启动后却用了别的值，通常需要查看属性来源与优先级。
privacy_reviewed: true
content_revision: 3
images:
- /img/tech-notes/boot12-configuration-precedence.svg
technology_since: '2015-02-27'
---

配置文件写了端口，启动后却用了别的值，通常需要查看属性来源与优先级。

本文使用JDK 7、Maven 与 Spring Boot 1.2.2.RELEASE，代码为工程片段。Spring Boot（约定化应用框架）减少常见装配代码，但自动配置仍有条件和来源。本文使用一代框架的属性与接口，不混入后续版本的配置名称。

## 1. 从现象推到机制

配置可以来自应用文件、外部文件、环境变量和命令行等来源。profile（配置环境）决定装载哪些配置，优先级再决定同名键最终取值。只搜索一个 application.properties 文件不足以解释运行结果。

![Spring Boot 配置：同一个端口为什么读取了另一个值的处理、反馈与观察关系](/img/tech-notes/boot12-configuration-precedence.svg)

图中的四个节点分别表示属性来源、配置环境、优先级合并、组件读取。顺着实线检查输入如何变成输出，再沿虚线核对反馈条件。图示表达的是本文讨论的关系，不是实测曲线或现场截图。

## 2. 最小实现与输入条件

用端口这个无敏感字段演示覆盖，分别记录启动参数和生效值。密码等内容不要通过命令行或调试输出展示。

```properties
server.port=8080
spring.profiles.active=demo
# 命令行可演示覆盖：--server.port=8081
```

工程需要声明匹配版本的 parent、starter 与 Maven 插件。运行时保留依赖树和实际生效配置，在控制台日志与真实请求之间建立对应，不能只根据启动横幅判断服务可用。

## 3. 用对照区分原因

下表列出需要主动改变的条件。预期行为来自机制分析，复现时还需记录运行环境和原始输出，不能将预期当作已经测得的结果。

| 改变的条件 | 需要验证的行为 |
| --- | --- |
| 命令行指定另一端口 | 需要按来源优先级检查最终值 |
| 激活另一配置环境 | 可能加载对应环境文件 |
| 文件在错误目录 | 可能没有进入默认搜索位置 |

### 对照 1：命令行指定另一端口

需要按来源优先级检查最终值。观察时记录完整启动参数与监听结果。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 2：激活另一配置环境

可能加载对应环境文件。观察时记录实际 active profiles。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 3：文件在错误目录

可能没有进入默认搜索位置。观察时记录配置文件路径与启动工作目录。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。

## 4. 适用条件与取舍

配置可覆盖不代表可以随意动态修改。很多组件只在启动时读取属性，修改文件后是否生效必须看组件生命周期。

一次正常运行只覆盖了这组输入。继续扩展前，应把上面的异常对照保留下来，尤其关注“文件在错误目录”这一分支。后续方案若改变了图中任意一处依赖，原来的判断就要重新验证，不能仅凭界面相似或返回值相同沿用结论。

## 同月延伸

- [Spring Boot 入门：从一个可执行 Web 工程开始](/tech/2015/04/05/boot12-minimal-web-project/)
- [Spring Boot 深入：自动配置为何会生效或退让](/tech/2015/04/15/boot12-auto-configuration/)

## 参考资料

1. [Spring Boot 1.2.2 参考指南](https://docs.spring.io/spring-boot/docs/1.2.2.RELEASE/reference/htmlsingle/)
2. [Spring Boot 1.0 正式发布](https://spring.io/blog/2014/04/01/spring-boot-1-0-ga-released/)
