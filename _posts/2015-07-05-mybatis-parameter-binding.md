---
layout: post
title: MyBatis：占位参数与字符串替换的边界
subtitle: 把用户输入直接拼入 SQL，即使页面限制了输入，也会把数据与语法混在一起。
date: 2015-07-05 08:00:00 +0800
author: edyang
header-style: text
catalog: true
tags:
- MyBatis
- SQL
tech_note: true
note_id: mybatis-parameter-binding
permalink: /tech/2015/07/05/mybatis-parameter-binding/
excerpt: 把用户输入直接拼入 SQL，即使页面限制了输入，也会把数据与语法混在一起。
privacy_reviewed: true
content_revision: 3
images:
- /img/tech-notes/mybatis-parameter-binding.svg
technology_since: '2015-01-01'
---

把用户输入直接拼入 SQL，即使页面限制了输入，也会把数据与语法混在一起。

本文使用MyBatis 3.2 系列、Java 7 与 JDBC 数据源，XML 为 Mapper 片段。MyBatis（SQL 映射框架）让查询显式可见，也要求开发者对参数、结果结构和执行成本负责。映射成功不代表查询满足权限与业务约束。

## 1. 从现象推到机制

#{value} 通常通过预处理参数绑定值，${value} 则进行文本替换。列名、表名和排序方向不能像普通值一样绑定，应从服务端白名单选择。字符转义不是任意动态 SQL 的安全替代品。

![MyBatis：占位参数与字符串替换的边界的处理、反馈与观察关系](/img/tech-notes/mybatis-parameter-binding.svg)

图中的四个节点分别表示用户输入、值绑定、结构选择、执行审查。顺着实线检查输入如何变成输出，再沿虚线核对反馈条件。图示表达的是本文讨论的关系，不是实测曲线或现场截图。

## 2. 最小实现与输入条件

演示查询使用命名参数；排序列通过枚举映射固定字符串，不接受前端原样传入。XML 片段需放在完整 mapper 中。

```xml
<select id="findByStatus" resultType="demo.Order">
  SELECT id, status FROM orders
  WHERE status = #{status}
  ORDER BY id DESC
</select>
```

先准备两三条能区分边界的数据，输出参数化 SQL 与映射结果。会话与事务由明确的管理方式维护；使用 Spring 集成时，不再手工提交同一受管事务。

## 3. 用对照区分原因

下表列出需要主动改变的条件。预期行为来自机制分析，复现时还需记录运行环境和原始输出，不能将预期当作已经测得的结果。

| 改变的条件 | 需要验证的行为 |
| --- | --- |
| 输入包含引号字符 | 仍应被作为值处理 |
| 用户请求任意排序列 | 只能选择白名单中的列 |
| 使用文本替换处理普通条件 | 会扩大语法注入风险 |

### 对照 1：输入包含引号字符

仍应被作为值处理。观察时记录最终预处理参数而非拼接 SQL。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 2：用户请求任意排序列

只能选择白名单中的列。观察时记录服务端映射出的固定片段。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 3：使用文本替换处理普通条件

会扩大语法注入风险。观察时记录替换内容能否改变 SQL 结构。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。

## 4. 适用条件与取舍

参数绑定防护不了越权查询。租户或用户范围等条件仍应由可信身份构造，不能仅由客户端传一个 owner 字段决定。

一次正常运行只覆盖了这组输入。继续扩展前，应把上面的异常对照保留下来，尤其关注“使用文本替换处理普通条件”这一分支。后续方案若改变了图中任意一处依赖，原来的判断就要重新验证，不能仅凭界面相似或返回值相同沿用结论。

## 同月延伸

- [MyBatis：动态 where 与空条件的业务风险](/tech/2015/07/15/mybatis-dynamic-where/)
- [MyBatis：联表结果的别名与 resultMap](/tech/2015/07/25/mybatis-resultmap-alias/)

## 参考资料

1. [MyBatis 3 SQL 映射文档](https://mybatis.org/mybatis-3/sqlmap-xml.html)
2. [MyBatis 3.2.8 源码](https://github.com/mybatis/mybatis-3/tree/mybatis-3.2.8)
