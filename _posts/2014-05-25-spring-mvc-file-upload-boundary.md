---
layout: post
title: Spring MVC：文件上传先划清存储和访问边界
subtitle: 上传成功不只是收到一个文件。
date: 2014-05-25 08:00:00 +0800
author: edyang
header-style: text
catalog: true
tags:
- Spring
- Java Web
tech_note: true
note_id: spring-mvc-file-upload-boundary
permalink: /tech/2014/05/25/spring-mvc-file-upload-boundary/
excerpt: 上传成功不只是收到一个文件。
privacy_reviewed: true
content_revision: 3
images:
- /img/tech-notes/spring-mvc-file-upload-boundary.svg
technology_since: '2013-12-12'
---

上传成功不只是收到一个文件。还要决定文件放在哪里、谁能访问，以及错误中断后留下什么。

本文使用JDK 7、Spring Framework 3.2.6 与 Servlet 容器，代码为结构片段。把请求入口、业务服务和数据访问拆开，是为了明确依赖与事务归属。容器能够装配对象，但应用仍须负责业务规则、异常含义和外部资源生命周期。

## 1. 从现象推到机制

浏览器提供的文件名和类型不能直接信任。服务器应限制体积、生成独立存储名，必要时检查实际内容。将文件直接写入可执行的 Web 目录，会把内容上传和程序部署混为一谈。

![Spring MVC：文件上传先划清存储和访问边界的处理、反馈与观察关系](/img/tech-notes/spring-mvc-file-upload-boundary.svg)

图中的四个节点分别表示上传入口、临时存储、附件登记、受控下载。顺着实线检查输入如何变成输出，再沿虚线核对反馈条件。图示表达的是本文讨论的关系，不是实测曲线或现场截图。

## 2. 最小实现与输入条件

先接收至受控临时区，校验后再登记业务附件。数据库记录与文件移动不是同一事务，需要补偿清理与失败状态。

```text
receive -> bounded temporary file
validate -> generated storage key
persist metadata -> controlled storage
download -> authorization check
```

将片段放入匹配版本的 Maven 工程，补齐组件扫描、数据库连接及依赖。验证时通过容器取得对象，区分普通对象调用和代理调用，避免绕过要研究的机制。

## 3. 用对照区分原因

下表列出需要主动改变的条件。预期行为来自机制分析，复现时还需记录运行环境和原始输出，不能将预期当作已经测得的结果。

| 改变的条件 | 需要验证的行为 |
| --- | --- |
| 文件名包含路径分隔符 | 不应控制服务器存储位置 |
| 上传中途断开 | 临时文件需要有清理策略 |
| 猜到另一个附件地址 | 下载仍应验证访问权限 |

### 对照 1：文件名包含路径分隔符

不应控制服务器存储位置。观察时记录实际解析后的目标路径。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 2：上传中途断开

临时文件需要有清理策略。观察时记录未完成记录与临时文件数量。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 3：猜到另一个附件地址

下载仍应验证访问权限。观察时记录文件记录关联的业务权限。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。

## 4. 适用条件与取舍

文件后缀、声明类型和实际格式需要分别判断。图片处理和解压还会消耗额外资源，容量限制应覆盖后续处理成本。

一次正常运行只覆盖了这组输入。继续扩展前，应把上面的异常对照保留下来，尤其关注“猜到另一个附件地址”这一分支。后续方案若改变了图中任意一处依赖，原来的判断就要重新验证，不能仅凭界面相似或返回值相同沿用结论。

## 同月延伸

- [Spring MVC：参数绑定成功不代表输入合法](/tech/2014/05/05/spring-mvc-binding-validation/)
- [Spring MVC：统一异常响应要保留错误含义](/tech/2014/05/15/spring-mvc-exception-contract/)

## 参考资料

1. [Spring Framework 3.2.6 参考文档](https://docs.spring.io/spring-framework/docs/3.2.6.RELEASE/spring-framework-reference/htmlsingle/)
2. [Servlet 3.0 规范](https://jcp.org/en/jsr/detail?id=315)
