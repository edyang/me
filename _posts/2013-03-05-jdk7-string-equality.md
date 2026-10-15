---
layout: post
title: 透彻学习 JDK：String 相等与常量池
subtitle: String 看起来一样，引用却可能不同。
date: 2013-03-05 08:00:00 +0800
author: edyang
header-style: text
catalog: true
tags:
- Java
- JDK源码
tech_note: true
note_id: jdk7-string-equality
permalink: /tech/2013/03/05/jdk7-string-equality/
excerpt: String 看起来一样，引用却可能不同。
privacy_reviewed: true
content_revision: 3
images:
- /img/tech-notes/jdk7-string-equality.svg
technology_since: '2011-07-28'
---

String 看起来一样，引用却可能不同。判断业务文本相等时，需要先分清值相等与对象身份。

本文使用JDK 7，示例为方法体或类定义片段。源码学习需要区分语言规则、公共接口约定与某个版本的实现。本文把讨论范围固定在 Java 7，不把后续版本的集合结构或语法写进来。

## 1. 从现象推到机制

字符串字面量可进入常量池，new 创建的对象并不因此与字面量有相同引用。equals 比较字符内容，== 比较引用。不可变对象方便共享，不表示每个相同内容都只有一份实例。

![透彻学习 JDK：String 相等与常量池的处理、反馈与观察关系](/img/tech-notes/jdk7-string-equality.svg)

图中的四个节点分别表示文本输入、对象引用、内容比较、业务规则。顺着实线检查输入如何变成输出，再沿虚线核对反馈条件。图示表达的是本文讨论的关系，不是实测曲线或现场截图。

## 2. 最小实现与输入条件

把字面量、显式构造和运行期拼接放在同一个方法里，逐一输出 equals 与 ==，不要根据调试器显示的文本猜测对象身份。

```java
String a = "tea";
String b = new String("tea");
System.out.println(a == b);
System.out.println(a.equals(b));
```

将片段放入独立的小工程，补齐 imports（导入声明）和调用入口。观察返回值、异常类型及对象状态；并发实验需要重复交错，单次没有出错不能证明线程安全。

## 3. 用对照区分原因

下表列出需要主动改变的条件。预期行为来自机制分析，复现时还需记录运行环境和原始输出，不能将预期当作已经测得的结果。

| 改变的条件 | 需要验证的行为 |
| --- | --- |
| 显式创建相同文本 | 引用比较为假而内容比较为真 |
| 调用 intern 后比较 | 返回的规范表示可与池中引用相同 |
| 文本可能为 null | 直接调用实例方法会抛空指针异常 |

### 对照 1：显式创建相同文本

引用比较为假而内容比较为真。观察时记录两种比较运算的不同输出。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 2：调用 intern 后比较

返回的规范表示可与池中引用相同。观察时记录调用前后引用而非原变量文本。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 3：文本可能为 null

直接调用实例方法会抛空指针异常。观察时记录空值分支有没有先处理。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。

## 4. 适用条件与取舍

常量池是内存管理机制，不能作为业务身份模型。面向标识符时还要先定义大小写、空白与编码规则，equals 不会自动替业务做归一化。

一次正常运行只覆盖了这组输入。继续扩展前，应把上面的异常对照保留下来，尤其关注“文本可能为 null”这一分支。后续方案若改变了图中任意一处依赖，原来的判断就要重新验证，不能仅凭界面相似或返回值相同沿用结论。

## 同月延伸

- [透彻学习 JDK：equals 与 hashCode 必须一起设计](/tech/2013/03/15/jdk7-equals-hashcode/)
- [透彻学习 JDK：ArrayList 扩容与遍历删除](/tech/2013/03/25/jdk7-arraylist-growth/)

## 参考资料

1. [Java SE 7 API 文档](https://docs.oracle.com/javase/7/docs/api/)
2. [Java SE 7 语言规范](https://docs.oracle.com/javase/specs/jls/se7/html/index.html)
