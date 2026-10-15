---
layout: post
title: 透彻学习 JDK：反射调用失败要看哪一层异常
subtitle: 反射方法存在，却仍然调用失败，可能是查找参数错误、访问限制，也可能是目标方法自身抛错。
date: 2013-05-15 08:00:00 +0800
author: edyang
header-style: text
catalog: true
tags:
- Java
- JDK源码
tech_note: true
note_id: jdk7-reflection-invocation
permalink: /tech/2013/05/15/jdk7-reflection-invocation/
excerpt: 反射方法存在，却仍然调用失败，可能是查找参数错误、访问限制，也可能是目标方法自身抛错。
privacy_reviewed: true
content_revision: 3
images:
- /img/tech-notes/jdk7-reflection-invocation.svg
technology_since: '2011-07-28'
---

反射方法存在，却仍然调用失败，可能是查找参数错误、访问限制，也可能是目标方法自身抛错。

本文使用JDK 7，示例为方法体或类定义片段。源码学习需要区分语言规则、公共接口约定与某个版本的实现。本文把讨论范围固定在 Java 7，不把后续版本的集合结构或语法写进来。

## 1. 从现象推到机制

getMethod 按方法名和参数类型匹配公共方法，不会凭运行时值替你猜测签名。invoke 把目标方法抛出的异常包进 InvocationTargetException；若只打印包装异常，就容易丢掉业务失败的原因。

![透彻学习 JDK：反射调用失败要看哪一层异常的处理、反馈与观察关系](/img/tech-notes/jdk7-reflection-invocation.svg)

图中的四个节点分别表示方法签名、访问检查、目标执行、异常拆解。顺着实线检查输入如何变成输出，再沿虚线核对反馈条件。图示表达的是本文讨论的关系，不是实测曲线或现场截图。

## 2. 最小实现与输入条件

先用没有副作用的公开方法做实验。参数类型数组要与声明匹配，基本类型和包装类型在查找签名时不能随意互换。

```java
Method m = String.class.getMethod("substring", int.class);
try {
    System.out.println(m.invoke("sample", 2));
} catch (InvocationTargetException e) {
    throw new RuntimeException(e.getCause());
}
```

将片段放入独立的小工程，补齐 imports（导入声明）和调用入口。观察返回值、异常类型及对象状态；并发实验需要重复交错，单次没有出错不能证明线程安全。

## 3. 用对照区分原因

下表列出需要主动改变的条件。预期行为来自机制分析，复现时还需记录运行环境和原始输出，不能将预期当作已经测得的结果。

| 改变的条件 | 需要验证的行为 |
| --- | --- |
| 查找时使用错误参数类型 | 在方法查找阶段失败 |
| 索引超出字符串范围 | 目标异常由调用包装 |
| 调用非公开成员 | 可能受到访问检查限制 |

### 对照 1：查找时使用错误参数类型

在方法查找阶段失败。观察时记录异常是否为 NoSuchMethodException。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 2：索引超出字符串范围

目标异常由调用包装。观察时记录getCause 返回的真实异常。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 3：调用非公开成员

可能受到访问检查限制。观察时记录成员修饰符与调用环境。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。

## 4. 适用条件与取舍

反射适合框架适配和工具，不应替代所有正常方法调用。访问开放也不是权限设计，应避免让外部输入任意决定类名与方法名。

一次正常运行只覆盖了这组输入。继续扩展前，应把上面的异常对照保留下来，尤其关注“调用非公开成员”这一分支。后续方案若改变了图中任意一处依赖，原来的判断就要重新验证，不能仅凭界面相似或返回值相同沿用结论。

## 同月延伸

- [透彻学习 JDK：类加载器也参与类型身份](/tech/2013/05/05/jdk7-classloader-identity/)
- [透彻学习 JDK：字节流、字符流与乱码定位](/tech/2013/05/25/jdk7-io-charset/)

## 参考资料

1. [Java SE 7 API 文档](https://docs.oracle.com/javase/7/docs/api/)
2. [Java SE 7 语言规范](https://docs.oracle.com/javase/specs/jls/se7/html/index.html)
