---
layout: post
title: Spring Boot 部署：可执行 jar 与外部配置
subtitle: 可执行 jar 简化交付，但部署仍需要明确运行身份、工作目录、配置来源和日志位置。
date: 2015-06-15 08:00:00 +0800
author: edyang
header-style: text
catalog: true
tags:
- Spring Boot
- Java
tech_note: true
note_id: boot12-executable-jar-deployment
permalink: /tech/2015/06/15/boot12-executable-jar-deployment/
excerpt: 可执行 jar 简化交付，但部署仍需要明确运行身份、工作目录、配置来源和日志位置。
privacy_reviewed: true
content_revision: 3
images:
- /img/tech-notes/boot12-executable-jar-deployment.svg
technology_since: '2015-02-27'
---

可执行 jar 简化交付，但部署仍需要明确运行身份、工作目录、配置来源和日志位置。

本文使用JDK 7、Maven 与 Spring Boot 1.2.2.RELEASE，代码为工程片段。Spring Boot（约定化应用框架）减少常见装配代码，但自动配置仍有条件和来源。本文使用一代框架的属性与接口，不混入后续版本的配置名称。

## 1. 从现象推到机制

重新打包的 jar 包含启动器与依赖布局，普通 java -jar 通过启动器加载应用。环境配置放在外部可避免为不同环境重新编译，但配置必须与程序版本兼容。直接覆盖运行文件不能提供可靠回退依据。

![Spring Boot 部署：可执行 jar 与外部配置的处理、反馈与观察关系](/img/tech-notes/boot12-executable-jar-deployment.svg)

图中的四个节点分别表示构建产物、外部配置、受控启动、回退依据。顺着实线检查输入如何变成输出，再沿虚线核对反馈条件。图示表达的是本文讨论的关系，不是实测曲线或现场截图。

## 2. 最小实现与输入条件

给每次交付保留版本文件名与校验值，在独立演示目录运行。实际服务管理交给明确的进程管理机制，不依赖终端会话存活。

```bash
mvn clean package
java -jar target/demo.jar --spring.profiles.active=demo
# 记录产物、配置版本与启动参数
```

工程需要声明匹配版本的 parent、starter 与 Maven 插件。运行时保留依赖树和实际生效配置，在控制台日志与真实请求之间建立对应，不能只根据启动横幅判断服务可用。

## 3. 用对照区分原因

下表列出需要主动改变的条件。预期行为来自机制分析，复现时还需记录运行环境和原始输出，不能将预期当作已经测得的结果。

| 改变的条件 | 需要验证的行为 |
| --- | --- |
| 从另一目录启动 | 外部相对配置路径可能变化 |
| 程序换版但配置未同步 | 可能启动失败或行为改变 |
| 进程仍活着但业务失败 | 仍需要真实请求和依赖验证 |

### 对照 1：从另一目录启动

外部相对配置路径可能变化。观察时记录实际工作目录与配置来源。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 2：程序换版但配置未同步

可能启动失败或行为改变。观察时记录版本要求与生效属性。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 3：进程仍活着但业务失败

仍需要真实请求和依赖验证。观察时记录启动状态与业务结果。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。

## 4. 适用条件与取舍

旧 jar 能启动不代表可以回退数据库结构。涉及迁移时，先设计新旧程序与数据兼容窗口，再制定程序回退步骤。

一次正常运行只覆盖了这组输入。继续扩展前，应把上面的异常对照保留下来，尤其关注“进程仍活着但业务失败”这一分支。后续方案若改变了图中任意一处依赖，原来的判断就要重新验证，不能仅凭界面相似或返回值相同沿用结论。

## 同月延伸

- [Spring Boot：把零散配置收敛成有类型的对象](/tech/2015/06/05/boot12-configuration-properties/)
- [Spring Boot 测试：不要每个规则都启动整个容器](/tech/2015/06/25/boot12-test-layering/)

## 参考资料

1. [Spring Boot 1.2.2 参考指南](https://docs.spring.io/spring-boot/docs/1.2.2.RELEASE/reference/htmlsingle/)
2. [Spring Boot 1.0 正式发布](https://spring.io/blog/2014/04/01/spring-boot-1-0-ga-released/)
