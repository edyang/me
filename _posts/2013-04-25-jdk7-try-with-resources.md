---
layout: post
title: 透彻学习 JDK：try-with-resources 怎样处理两个异常
subtitle: 读取文件失败时，关闭资源也可能失败。
date: 2013-04-25 08:00:00 +0800
author: edyang
header-style: text
catalog: true
tags:
- Java
- JDK源码
tech_note: true
note_id: jdk7-try-with-resources
permalink: /tech/2013/04/25/jdk7-try-with-resources/
excerpt: 读取文件失败时，关闭资源也可能失败。
privacy_reviewed: true
content_revision: 3
images:
- /img/tech-notes/jdk7-try-with-resources.svg
technology_since: '2011-07-28'
---

读取文件失败时，关闭资源也可能失败。异常处理需要保留主要故障，而不是让关闭异常覆盖它。

本文使用JDK 7，示例为方法体或类定义片段。源码学习需要区分语言规则、公共接口约定与某个版本的实现。本文把讨论范围固定在 Java 7，不把后续版本的集合结构或语法写进来。

## 1. 从现象推到机制

Java 7 的自动资源管理要求资源实现 AutoCloseable。多个资源按声明的反序关闭，主体异常仍作为主要异常，关闭时的异常可以进入 suppressed（被抑制异常）列表。资源关闭发生在正常与异常退出路径上。

![透彻学习 JDK：try-with-resources 怎样处理两个异常的处理、反馈与观察关系](/img/tech-notes/jdk7-try-with-resources.svg)

图中的四个节点分别表示资源创建、主体执行、反序关闭、异常保留。顺着实线检查输入如何变成输出，再沿虚线核对反馈条件。图示表达的是本文讨论的关系，不是实测曲线或现场截图。

## 2. 最小实现与输入条件

用一个演示资源同时模拟读取和关闭错误，输出主异常以及 getSuppressed 的内容。不要用真实生产文件制造故障。

```java
try (InputStream in = new FileInputStream("sample.txt")) {
    System.out.println(in.read());
} catch (IOException e) {
    for (Throwable s : e.getSuppressed()) {
        System.err.println(s.getClass().getName());
    }
}
```

将片段放入独立的小工程，补齐 imports（导入声明）和调用入口。观察返回值、异常类型及对象状态；并发实验需要重复交错，单次没有出错不能证明线程安全。

## 3. 用对照区分原因

下表列出需要主动改变的条件。预期行为来自机制分析，复现时还需记录运行环境和原始输出，不能将预期当作已经测得的结果。

| 改变的条件 | 需要验证的行为 |
| --- | --- |
| 读取正常而关闭失败 | 关闭异常需要向外传播 |
| 读取和关闭同时失败 | 读取异常保留为主要异常 |
| 先后声明两个资源 | 按相反顺序尝试关闭 |

### 对照 1：读取正常而关闭失败

关闭异常需要向外传播。观察时记录主体和关闭阶段各自的结果。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 2：读取和关闭同时失败

读取异常保留为主要异常。观察时记录被抑制异常列表。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 3：先后声明两个资源

按相反顺序尝试关闭。观察时记录每个 close 的调用顺序。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。

## 4. 适用条件与取舍

自动关闭资源不等于自动提交事务。连接、事务和业务成功之间仍需定义提交与回滚规则，close 的语义必须查具体实现。

一次正常运行只覆盖了这组输入。继续扩展前，应把上面的异常对照保留下来，尤其关注“先后声明两个资源”这一分支。后续方案若改变了图中任意一处依赖，原来的判断就要重新验证，不能仅凭界面相似或返回值相同沿用结论。

## 同月延伸

- [透彻学习 JDK 7：HashMap 的桶、冲突与扩容](/tech/2013/04/05/jdk7-hashmap-buckets/)
- [透彻学习 JDK：泛型擦除为何仍会出现类型转换错误](/tech/2013/04/15/jdk7-generic-erasure/)

## 参考资料

1. [Java SE 7 API 文档](https://docs.oracle.com/javase/7/docs/api/)
2. [Java SE 7 语言规范](https://docs.oracle.com/javase/specs/jls/se7/html/index.html)
