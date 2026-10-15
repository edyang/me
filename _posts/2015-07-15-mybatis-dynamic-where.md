---
layout: post
title: MyBatis：动态 where 与空条件的业务风险
subtitle: 动态查询没有语法错误，却可能在条件为空时查出全表。
date: 2015-07-15 08:00:00 +0800
author: edyang
header-style: text
catalog: true
tags:
- MyBatis
- SQL
tech_note: true
note_id: mybatis-dynamic-where
permalink: /tech/2015/07/15/mybatis-dynamic-where/
excerpt: 动态查询没有语法错误，却可能在条件为空时查出全表。
privacy_reviewed: true
content_revision: 3
images:
- /img/tech-notes/mybatis-dynamic-where.svg
technology_since: '2015-01-01'
---

动态查询没有语法错误，却可能在条件为空时查出全表。语法拼接和业务范围需要分别控制。

本文使用MyBatis 3.2 系列、Java 7 与 JDBC 数据源，XML 为 Mapper 片段。MyBatis（SQL 映射框架）让查询显式可见，也要求开发者对参数、结果结构和执行成本负责。映射成功不代表查询满足权限与业务约束。

## 1. 从现象推到机制

where、if、trim 等标签帮助处理连接词，不会替应用判断哪些过滤条件是必需的。空集合、空字符串和 null 有不同含义。更新语句若动态遗漏主键条件，风险远高于返回空结果。

![MyBatis：动态 where 与空条件的业务风险的处理、反馈与观察关系](/img/tech-notes/mybatis-dynamic-where.svg)

图中的四个节点分别表示可信范围、可选参数、动态拼接、最终语句。顺着实线检查输入如何变成输出，再沿虚线核对反馈条件。图示表达的是本文讨论的关系，不是实测曲线或现场截图。

## 2. 最小实现与输入条件

固定权限条件始终存在，可选筛选才放进 if。批量查询空 id 列表时直接返回空结果，避免退化成没有过滤的查询。

```xml
<where>
  owner_id = #{ownerId}
  <if test="status != null">
    AND status = #{status}
  </if>
</where>
```

先准备两三条能区分边界的数据，输出参数化 SQL 与映射结果。会话与事务由明确的管理方式维护；使用 Spring 集成时，不再手工提交同一受管事务。

## 3. 用对照区分原因

下表列出需要主动改变的条件。预期行为来自机制分析，复现时还需记录运行环境和原始输出，不能将预期当作已经测得的结果。

| 改变的条件 | 需要验证的行为 |
| --- | --- |
| 所有可选过滤为空 | 仍必须保留数据权限范围 |
| id 列表为空 | 应按接口约定返回空而非全表 |
| 更新主键缺失 | 应拒绝执行而不是省略条件 |

### 对照 1：所有可选过滤为空

仍必须保留数据权限范围。观察时记录最终 SQL 的固定条件。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 2：id 列表为空

应按接口约定返回空而非全表。观察时记录进入 mapper 前的参数判断。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 3：更新主键缺失

应拒绝执行而不是省略条件。观察时记录最终 UPDATE 是否仍有限定。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。

## 4. 适用条件与取舍

动态 SQL 越复杂，越需要对参数组合做代表性检查。不能只检查最完整的一组条件，因为危险分支通常发生在条件缺失时。

一次正常运行只覆盖了这组输入。继续扩展前，应把上面的异常对照保留下来，尤其关注“更新主键缺失”这一分支。后续方案若改变了图中任意一处依赖，原来的判断就要重新验证，不能仅凭界面相似或返回值相同沿用结论。

## 同月延伸

- [MyBatis：占位参数与字符串替换的边界](/tech/2015/07/05/mybatis-parameter-binding/)
- [MyBatis：联表结果的别名与 resultMap](/tech/2015/07/25/mybatis-resultmap-alias/)

## 参考资料

1. [MyBatis 3 SQL 映射文档](https://mybatis.org/mybatis-3/sqlmap-xml.html)
2. [MyBatis 3.2.8 源码](https://github.com/mybatis/mybatis-3/tree/mybatis-3.2.8)
