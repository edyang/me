---
layout: post
title: Spring Boot 入门：从一个可执行 Web 工程开始
subtitle: Spring Boot 的方便之处，是把常见 Web 依赖和启动方式组织起来。
date: 2015-04-05 08:00:00 +0800
author: edyang
header-style: text
catalog: true
tags:
- Spring Boot
- Java
tech_note: true
note_id: boot12-minimal-web-project
permalink: /tech/2015/04/05/boot12-minimal-web-project/
excerpt: Spring Boot 的方便之处，是把常见 Web 依赖和启动方式组织起来。
privacy_reviewed: true
content_revision: 3
images:
- /img/tech-notes/boot12-minimal-web-project.svg
technology_since: '2015-02-27'
---

Spring Boot 的方便之处，是把常见 Web 依赖和启动方式组织起来。先做最小工程，才能看清自动装配边界。

本文使用JDK 7、Maven 与 Spring Boot 1.2.2.RELEASE，代码为工程片段。Spring Boot（约定化应用框架）减少常见装配代码，但自动配置仍有条件和来源。本文使用一代框架的属性与接口，不混入后续版本的配置名称。

## 1. 从现象推到机制

starter（依赖集合）引入常见组件，自动配置根据类路径和已有 Bean 判断是否提供默认实现。入口注解组合了配置与扫描，不代表任何目录里的类都会自动被发现。主类的位置会影响默认扫描范围。

![Spring Boot 入门：从一个可执行 Web 工程开始的处理、反馈与观察关系](/img/tech-notes/boot12-minimal-web-project.svg)

图中的四个节点分别表示依赖声明、应用入口、嵌入容器、请求验证。顺着实线检查输入如何变成输出，再沿虚线核对反馈条件。图示表达的是本文讨论的关系，不是实测曲线或现场截图。

## 2. 最小实现与输入条件

在 demo 包下放入口和控制器，Maven 插件负责重新打包可执行 jar。示例只返回演示文本，不连接数据库。

```java
@SpringBootApplication
@RestController
public class DemoApplication {
  @RequestMapping("/hello")
  public String hello() { return "hello"; }
  public static void main(String[] args) {
    SpringApplication.run(DemoApplication.class, args);
  }
}
```

工程需要声明匹配版本的 parent、starter 与 Maven 插件。运行时保留依赖树和实际生效配置，在控制台日志与真实请求之间建立对应，不能只根据启动横幅判断服务可用。

## 3. 用对照区分原因

下表列出需要主动改变的条件。预期行为来自机制分析，复现时还需记录运行环境和原始输出，不能将预期当作已经测得的结果。

| 改变的条件 | 需要验证的行为 |
| --- | --- |
| 控制器放在扫描范围外 | 服务启动也可能找不到路径 |
| 只运行普通 jar 打包 | 未必具备可执行依赖布局 |
| 端口已经被占用 | 启动应有明确绑定错误 |

### 对照 1：控制器放在扫描范围外

服务启动也可能找不到路径。观察时记录扫描基包与 Bean 注册结果。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 2：只运行普通 jar 打包

未必具备可执行依赖布局。观察时记录插件是否执行 repackage。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 3：端口已经被占用

启动应有明确绑定错误。观察时记录实际监听进程与启动异常。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。

## 4. 适用条件与取舍

最小接口正常只是第一步。数据源、配置和管理端点加入后，都需要分别定义就绪条件，不能把 hello 接口等同整套系统验收。

一次正常运行只覆盖了这组输入。继续扩展前，应把上面的异常对照保留下来，尤其关注“端口已经被占用”这一分支。后续方案若改变了图中任意一处依赖，原来的判断就要重新验证，不能仅凭界面相似或返回值相同沿用结论。

## 同月延伸

- [Spring Boot 深入：自动配置为何会生效或退让](/tech/2015/04/15/boot12-auto-configuration/)
- [Spring Boot 配置：同一个端口为什么读取了另一个值](/tech/2015/04/25/boot12-configuration-precedence/)

## 参考资料

1. [Spring Boot 1.2.2 参考指南](https://docs.spring.io/spring-boot/docs/1.2.2.RELEASE/reference/htmlsingle/)
2. [Spring Boot 1.0 正式发布](https://spring.io/blog/2014/04/01/spring-boot-1-0-ga-released/)
