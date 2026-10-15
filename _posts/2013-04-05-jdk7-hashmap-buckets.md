---
layout: post
title: 透彻学习 JDK 7：HashMap 的桶、冲突与扩容
subtitle: 研究 HashMap 要固定版本。
date: 2013-04-05 08:00:00 +0800
author: edyang
header-style: text
catalog: true
tags:
- Java
- JDK源码
tech_note: true
note_id: jdk7-hashmap-buckets
permalink: /tech/2013/04/05/jdk7-hashmap-buckets/
excerpt: 研究 HashMap 要固定版本。
privacy_reviewed: true
content_revision: 3
images:
- /img/tech-notes/jdk7-hashmap-buckets.svg
technology_since: '2011-07-28'
---

研究 HashMap 要固定版本。Java 7 的冲突处理不能直接套用后续版本的树化机制。

本文使用JDK 7，示例为方法体或类定义片段。源码学习需要区分语言规则、公共接口约定与某个版本的实现。本文把讨论范围固定在 Java 7，不把后续版本的集合结构或语法写进来。

## 1. 从现象推到机制

键的散列值参与桶下标计算，同桶多个元素还需要逐个比较键。负载因子决定触发扩容的阈值，容量与元素数是两回事。低冲突时平均访问较快，但坏散列函数会拉长桶内查找路径。

![透彻学习 JDK 7：HashMap 的桶、冲突与扩容的处理、反馈与观察关系](/img/tech-notes/jdk7-hashmap-buckets.svg)

图中的四个节点分别表示键的散列、桶下标、冲突查找、阈值判断。顺着实线检查输入如何变成输出，再沿虚线核对反馈条件。图示表达的是本文讨论的关系，不是实测曲线或现场截图。

## 2. 最小实现与输入条件

定义一个所有键都返回相同散列值的小类，观察集合仍能保存不同键。把实验限定在单线程，避免把并发修改缺陷混进散列分析。

```java
Map<String,Integer> counts = new HashMap<String,Integer>(16);
counts.put("a", 1);
counts.put("b", 2);
System.out.println(counts.get("a"));
```

将片段放入独立的小工程，补齐 imports（导入声明）和调用入口。观察返回值、异常类型及对象状态；并发实验需要重复交错，单次没有出错不能证明线程安全。

## 3. 用对照区分原因

下表列出需要主动改变的条件。预期行为来自机制分析，复现时还需记录运行环境和原始输出，不能将预期当作已经测得的结果。

| 改变的条件 | 需要验证的行为 |
| --- | --- |
| 两个不同键散列相同 | 不同键值仍应分别保存 |
| 元素数超过扩容阈值 | 需要重新分配并迁移条目 |
| 多个线程共同写入 | 普通 HashMap 没有线程安全保证 |

### 对照 1：两个不同键散列相同

不同键值仍应分别保存。观察时记录桶内 equals 判断。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 2：元素数超过扩容阈值

需要重新分配并迁移条目。观察时记录旧容量阈值与新容量。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 3：多个线程共同写入

普通 HashMap 没有线程安全保证。观察时记录读写交错而非单次输出。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。

## 4. 适用条件与取舍

初始容量配置要考虑负载因子及实际数量。HashMap 不保证遍历顺序，若业务要求稳定顺序，应明确选择相应的数据结构。

一次正常运行只覆盖了这组输入。继续扩展前，应把上面的异常对照保留下来，尤其关注“多个线程共同写入”这一分支。后续方案若改变了图中任意一处依赖，原来的判断就要重新验证，不能仅凭界面相似或返回值相同沿用结论。

## 同月延伸

- [透彻学习 JDK：泛型擦除为何仍会出现类型转换错误](/tech/2013/04/15/jdk7-generic-erasure/)
- [透彻学习 JDK：try-with-resources 怎样处理两个异常](/tech/2013/04/25/jdk7-try-with-resources/)

## 参考资料

1. [Java SE 7 API 文档](https://docs.oracle.com/javase/7/docs/api/)
2. [Java SE 7 语言规范](https://docs.oracle.com/javase/specs/jls/se7/html/index.html)
