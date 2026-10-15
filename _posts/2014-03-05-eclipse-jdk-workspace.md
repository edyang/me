---
layout: post
title: Eclipse 配置：工程 JDK、编译级别和运行时分开检查
subtitle: Eclipse 能启动，不代表工程使用了正确的 JDK。
date: 2014-03-05 08:00:00 +0800
author: edyang
header-style: text
catalog: true
tags:
- 软件工程
- 职场笔记
tech_note: true
note_id: eclipse-jdk-workspace
permalink: /tech/2014/03/05/eclipse-jdk-workspace/
excerpt: Eclipse 能启动，不代表工程使用了正确的 JDK。
privacy_reviewed: true
content_revision: 3
images:
- /img/tech-notes/eclipse-jdk-workspace.svg
technology_since: '2013-01-01'
---

Eclipse 能启动，不代表工程使用了正确的 JDK。编译通过而服务器报类版本错误，往往是环境不一致。

本文使用Java Web 小项目的演示工程与协作场景。初入团队时，重要的不只是写出功能，还包括让别人能够复现、审查和接手。本文使用匿名任务说明工作方法，不指代某家公司的内部流程或真实交付成绩。

## 1. 从现象推到机制

IDE 自身运行的虚拟机、工程构建路径、编译目标级别和应用服务器运行时可以分别配置。class 文件目标版本高于部署 JVM 支持范围，就无法加载。只修改系统 JAVA_HOME 未必改变工作区已有配置。

![Eclipse 配置：工程 JDK、编译级别和运行时分开检查的处理、反馈与观察关系](/img/tech-notes/eclipse-jdk-workspace.svg)

图中的四个节点分别表示IDE 虚拟机、工程配置、服务器运行时、版本对照。顺着实线检查输入如何变成输出，再沿虚线核对反馈条件。图示表达的是本文讨论的关系，不是实测曲线或现场截图。

## 2. 最小实现与输入条件

以 JDK 7 工程为例，核对 Installed JREs、Java Compiler 与服务器 Runtime。再查看命令行 java 和 javac 的实际版本。

```bash
java -version
javac -version
# Eclipse: Project Properties -> Java Build Path
# Eclipse: Project Properties -> Java Compiler
```

示例命令需要在独立演示工程中执行，路径和服务均由读者准备。操作前保留当前版本与输入，修改后对照原来的问题验证，而不是只证明新代码能够编译。

## 3. 用对照区分原因

下表列出需要主动改变的条件。预期行为来自机制分析，复现时还需记录运行环境和原始输出，不能将预期当作已经测得的结果。

| 改变的条件 | 需要验证的行为 |
| --- | --- |
| IDE 编译成功但服务器加载失败 | 先比较目标字节码与运行时版本 |
| 修改系统变量后工程没变化 | 工作区可能仍指向旧 JDK |
| 导入工程后缺依赖 | 需要核对构建配置而非复制随机 jar |

### 对照 1：IDE 编译成功但服务器加载失败

先比较目标字节码与运行时版本。观察时记录完整 UnsupportedClassVersionError。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 2：修改系统变量后工程没变化

工作区可能仍指向旧 JDK。观察时记录工程与服务器的显式配置。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 3：导入工程后缺依赖

需要核对构建配置而非复制随机 jar。观察时记录项目依赖来源与版本。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。

## 4. 适用条件与取舍

工作区个人设置不宜全部提交。可共享的是工程必要配置与构建描述，机器路径应通过环境或工具约定解决。

一次正常运行只覆盖了这组输入。继续扩展前，应把上面的异常对照保留下来，尤其关注“导入工程后缺依赖”这一分支。后续方案若改变了图中任意一处依赖，原来的判断就要重新验证，不能仅凭界面相似或返回值相同沿用结论。

## 同月延伸

- [Eclipse 调试：从一个断点还原请求状态](/tech/2014/03/15/eclipse-breakpoint-request/)
- [Maven 依赖冲突：为什么编译和运行用到不同的类](/tech/2014/03/25/maven-dependency-conflict/)

## 参考资料

1. [Maven 3.1.1 文档](https://maven.apache.org/ref/3.1.1/)
2. [Spring Framework 3.2.6 参考文档](https://docs.spring.io/spring-framework/docs/3.2.6.RELEASE/spring-framework-reference/htmlsingle/)
