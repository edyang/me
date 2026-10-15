---
layout: post
title: 透彻学习 JDK：equals 与 hashCode 必须一起设计
subtitle: 把自定义对象放进 HashSet 后，明明相等却仍然重复，通常需要检查散列契约。
date: 2013-03-15 08:00:00 +0800
author: edyang
header-style: text
catalog: true
tags:
- Java
- JDK源码
tech_note: true
note_id: jdk7-equals-hashcode
permalink: /tech/2013/03/15/jdk7-equals-hashcode/
excerpt: 把自定义对象放进 HashSet 后，明明相等却仍然重复，通常需要检查散列契约。
privacy_reviewed: true
content_revision: 3
images:
- /img/tech-notes/jdk7-equals-hashcode.svg
technology_since: '2011-07-28'
---

把自定义对象放进 HashSet 后，明明相等却仍然重复，通常需要检查散列契约。

本文使用JDK 7，示例为方法体或类定义片段。源码学习需要区分语言规则、公共接口约定与某个版本的实现。本文把讨论范围固定在 Java 7，不把后续版本的集合结构或语法写进来。

## 1. 从现象推到机制

相等对象必须返回相同散列值，散列相同却不代表相等。容器先利用散列缩小查找范围，再用相等判断匹配；只覆盖 equals 会让逻辑相等对象落入不一致的查找路径。

![透彻学习 JDK：equals 与 hashCode 必须一起设计的处理、反馈与观察关系](/img/tech-notes/jdk7-equals-hashcode.svg)

图中的四个节点分别表示业务键、散列定位、相等判断、集合操作。顺着实线检查输入如何变成输出，再沿虚线核对反馈条件。图示表达的是本文讨论的关系，不是实测曲线或现场截图。

## 2. 最小实现与输入条件

先选一个不可变业务键，例如演示编号；排除展示名称等可变属性。下面是只含一个字段的结构示例，真实类还要明确继承关系。

```java
final class Key {
  final int id;
  Key(int id) { this.id = id; }
  public boolean equals(Object o) {
    return o instanceof Key && ((Key)o).id == id;
  }
  public int hashCode() { return id; }
}
```

将片段放入独立的小工程，补齐 imports（导入声明）和调用入口。观察返回值、异常类型及对象状态；并发实验需要重复交错，单次没有出错不能证明线程安全。

## 3. 用对照区分原因

下表列出需要主动改变的条件。预期行为来自机制分析，复现时还需记录运行环境和原始输出，不能将预期当作已经测得的结果。

| 改变的条件 | 需要验证的行为 |
| --- | --- |
| 编号相同而实例不同 | 集合应按相等语义去重 |
| 不同编号发生散列冲突 | 仍能靠 equals 区分对象 |
| 入集合后修改键字段 | 可能无法按原位置再找到元素 |

### 对照 1：编号相同而实例不同

集合应按相等语义去重。观察时记录equals 与 hashCode 的返回结果。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 2：不同编号发生散列冲突

仍能靠 equals 区分对象。观察时记录冲突桶中的实际匹配。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 3：入集合后修改键字段

可能无法按原位置再找到元素。观察时记录散列依据是否在生命周期内变化。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。

## 4. 适用条件与取舍

不要把数据库自增编号尚未生成的实体随意作为散列键。对象从临时态到持久态时若相等规则变化，集合语义也会变化。

一次正常运行只覆盖了这组输入。继续扩展前，应把上面的异常对照保留下来，尤其关注“入集合后修改键字段”这一分支。后续方案若改变了图中任意一处依赖，原来的判断就要重新验证，不能仅凭界面相似或返回值相同沿用结论。

## 同月延伸

- [透彻学习 JDK：String 相等与常量池](/tech/2013/03/05/jdk7-string-equality/)
- [透彻学习 JDK：ArrayList 扩容与遍历删除](/tech/2013/03/25/jdk7-arraylist-growth/)

## 参考资料

1. [Java SE 7 API 文档](https://docs.oracle.com/javase/7/docs/api/)
2. [Java SE 7 语言规范](https://docs.oracle.com/javase/specs/jls/se7/html/index.html)
