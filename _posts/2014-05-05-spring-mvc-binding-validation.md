---
layout: post
title: Spring MVC：参数绑定成功不代表输入合法
subtitle: 请求参数能转成对象，只说明完成了类型绑定。
date: 2014-05-05 08:00:00 +0800
author: edyang
header-style: text
catalog: true
tags:
- Spring
- Java Web
tech_note: true
note_id: spring-mvc-binding-validation
permalink: /tech/2014/05/05/spring-mvc-binding-validation/
excerpt: 请求参数能转成对象，只说明完成了类型绑定。
privacy_reviewed: true
content_revision: 3
images:
- /img/tech-notes/spring-mvc-binding-validation.svg
technology_since: '2013-12-12'
---

请求参数能转成对象，只说明完成了类型绑定。业务有效性和权限还需要单独检查。

本文使用JDK 7、Spring Framework 3.2.6 与 Servlet 容器，代码为结构片段。把请求入口、业务服务和数据访问拆开，是为了明确依赖与事务归属。容器能够装配对象，但应用仍须负责业务规则、异常含义和外部资源生命周期。

## 1. 从现象推到机制

绑定负责把字符串转换为字段类型，格式错误应反馈为输入问题。数值范围、字段组合和对象归属属于校验。直接把整个持久化实体暴露给绑定，会让不应由用户设置的字段进入写入路径。

![Spring MVC：参数绑定成功不代表输入合法的处理、反馈与观察关系](/img/tech-notes/spring-mvc-binding-validation.svg)

图中的四个节点分别表示请求字符串、表单绑定、规则校验、业务写入。顺着实线检查输入如何变成输出，再沿虚线核对反馈条件。图示表达的是本文讨论的关系，不是实测曲线或现场截图。

## 2. 最小实现与输入条件

定义专用表单对象，只保留可编辑字段；在校验失败时返回具体字段错误。服务层仍要验证当前用户是否有权操作目标订单。

```java
public class OrderForm {
    @NotNull
    @Min(1)
    private Integer quantity;
    // getters / setters
}
```

将片段放入匹配版本的 Maven 工程，补齐组件扫描、数据库连接及依赖。验证时通过容器取得对象，区分普通对象调用和代理调用，避免绕过要研究的机制。

## 3. 用对照区分原因

下表列出需要主动改变的条件。预期行为来自机制分析，复现时还需记录运行环境和原始输出，不能将预期当作已经测得的结果。

| 改变的条件 | 需要验证的行为 |
| --- | --- |
| 数量填写非数字 | 应在类型绑定阶段报错 |
| 数量填写零 | 类型正确但范围不合法 |
| 提交额外的管理员字段 | 不应进入业务实体修改 |

### 对照 1：数量填写非数字

应在类型绑定阶段报错。观察时记录字段绑定错误而非数据库异常。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 2：数量填写零

类型正确但范围不合法。观察时记录校验器返回的字段错误。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 3：提交额外的管理员字段

不应进入业务实体修改。观察时记录专用表单允许绑定的字段。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。

## 4. 适用条件与取舍

浏览器校验能改善体验，但无法形成信任边界。服务端应在任何调用入口保持相同规则，不能假设请求只能来自本页面。

一次正常运行只覆盖了这组输入。继续扩展前，应把上面的异常对照保留下来，尤其关注“提交额外的管理员字段”这一分支。后续方案若改变了图中任意一处依赖，原来的判断就要重新验证，不能仅凭界面相似或返回值相同沿用结论。

## 同月延伸

- [Spring MVC：统一异常响应要保留错误含义](/tech/2014/05/15/spring-mvc-exception-contract/)
- [Spring MVC：文件上传先划清存储和访问边界](/tech/2014/05/25/spring-mvc-file-upload-boundary/)

## 参考资料

1. [Spring Framework 3.2.6 参考文档](https://docs.spring.io/spring-framework/docs/3.2.6.RELEASE/spring-framework-reference/htmlsingle/)
2. [Servlet 3.0 规范](https://jcp.org/en/jsr/detail?id=315)
