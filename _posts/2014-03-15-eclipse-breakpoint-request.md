---
layout: post
title: Eclipse 调试：从一个断点还原请求状态
subtitle: 断点停住以后看所有变量，很容易被框架对象淹没。
date: 2014-03-15 08:00:00 +0800
author: edyang
header-style: text
catalog: true
tags:
- 软件工程
- 职场笔记
tech_note: true
note_id: eclipse-breakpoint-request
permalink: /tech/2014/03/15/eclipse-breakpoint-request/
excerpt: 断点停住以后看所有变量，很容易被框架对象淹没。
privacy_reviewed: true
content_revision: 3
images:
- /img/tech-notes/eclipse-breakpoint-request.svg
technology_since: '2013-01-01'
---

断点停住以后看所有变量，很容易被框架对象淹没。调试应围绕一个具体假设收集证据。

本文使用Java Web 小项目的演示工程与协作场景。初入团队时，重要的不只是写出功能，还包括让别人能够复现、审查和接手。本文使用匿名任务说明工作方法，不指代某家公司的内部流程或真实交付成绩。

## 1. 从现象推到机制

先确定错误输入在哪一层首次出现，再从控制器参数、服务条件和 SQL 参数逐段比较。单步进入不总是必要，调用栈与条件断点可以缩小范围。暂停线程还会改变时序，因此并发缺陷不能只靠单步判断。

![Eclipse 调试：从一个断点还原请求状态的处理、反馈与观察关系](/img/tech-notes/eclipse-breakpoint-request.svg)

图中的四个节点分别表示问题假设、条件断点、调用栈、差异定位。顺着实线检查输入如何变成输出，再沿虚线核对反馈条件。图示表达的是本文讨论的关系，不是实测曲线或现场截图。

## 2. 最小实现与输入条件

对演示订单号设置条件断点，观察筛选条件是否在传递中丢失。不要在 getter 或表达式求值中调用有写入副作用的方法。

```text
breakpoint: OrderController.list
condition: "DEMO-7".equals(query.getNumber())
watch: query.status
compare: service argument -> mapper parameter
```

示例命令需要在独立演示工程中执行，路径和服务均由读者准备。操作前保留当前版本与输入，修改后对照原来的问题验证，而不是只证明新代码能够编译。

## 3. 用对照区分原因

下表列出需要主动改变的条件。预期行为来自机制分析，复现时还需记录运行环境和原始输出，不能将预期当作已经测得的结果。

| 改变的条件 | 需要验证的行为 |
| --- | --- |
| 入口参数已经错误 | 优先检查请求绑定或调用方 |
| 入口正确而 SQL 参数错误 | 问题在中间转换或默认值 |
| 单步后并发问题消失 | 暂停可能改变线程交错 |

### 对照 1：入口参数已经错误

优先检查请求绑定或调用方。观察时记录原始请求与绑定对象。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 2：入口正确而 SQL 参数错误

问题在中间转换或默认值。观察时记录各层第一次出现差异的位置。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 3：单步后并发问题消失

暂停可能改变线程交错。观察时记录非暂停环境的关联日志。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。

## 4. 适用条件与取舍

调试器可以观察局部状态，但不能代替可重复验证。修复后应撤掉临时断点与调试输出，保留最小复现输入。

一次正常运行只覆盖了这组输入。继续扩展前，应把上面的异常对照保留下来，尤其关注“单步后并发问题消失”这一分支。后续方案若改变了图中任意一处依赖，原来的判断就要重新验证，不能仅凭界面相似或返回值相同沿用结论。

## 同月延伸

- [Eclipse 配置：工程 JDK、编译级别和运行时分开检查](/tech/2014/03/05/eclipse-jdk-workspace/)
- [Maven 依赖冲突：为什么编译和运行用到不同的类](/tech/2014/03/25/maven-dependency-conflict/)

## 参考资料

1. [Maven 3.1.1 文档](https://maven.apache.org/ref/3.1.1/)
2. [Spring Framework 3.2.6 参考文档](https://docs.spring.io/spring-framework/docs/3.2.6.RELEASE/spring-framework-reference/htmlsingle/)
