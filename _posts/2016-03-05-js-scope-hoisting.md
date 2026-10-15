---
layout: post
title: 深入 JavaScript：变量提升不会替你完成赋值
subtitle: 在声明前读取变量得到 undefined，不代表那行赋值已经被执行。
date: 2016-03-05 08:00:00 +0800
author: edyang
header-style: text
catalog: true
tags:
- JavaScript
- 前端原理
tech_note: true
note_id: js-scope-hoisting
permalink: /tech/2016/03/05/js-scope-hoisting/
excerpt: 在声明前读取变量得到 undefined，不代表那行赋值已经被执行。
privacy_reviewed: true
content_revision: 3
images:
- /img/tech-notes/js-scope-hoisting.svg
technology_since: '2011-06-01'
---

在声明前读取变量得到 undefined，不代表那行赋值已经被执行。声明处理与执行顺序要分开。

本文使用ECMAScript 5.1 与浏览器 DOM，代码可放入独立演示页。JavaScript（脚本语言）的作用域、函数调用与事件调度，需要与浏览器提供的接口区分。本文主体使用当时已经可用的语法，不把语言版本和宿主环境混为一谈。

## 1. 从现象推到机制

函数作用域内的 var 声明在进入执行上下文时建立绑定，但赋值仍按语句顺序执行。局部同名变量会遮蔽外部变量，所以函数前半段读取到的可能是未赋值的局部绑定。

![深入 JavaScript：变量提升不会替你完成赋值的处理、反馈与观察关系](/img/tech-notes/js-scope-hoisting.svg)

图中的四个节点分别表示进入函数、名称解析、顺序执行、输出观察。顺着实线检查输入如何变成输出，再沿虚线核对反馈条件。图示表达的是本文讨论的关系，不是实测曲线或现场截图。

## 2. 最小实现与输入条件

在演示函数中分别打印赋值前后结果，再把局部变量改名比较。不要把 let 等不同声明规则直接混进这一组 ES5 实验。

```javascript
var value = "outer";
function demo() {
  console.log(value);
  var value = "inner";
  console.log(value);
}
demo();
```

先记录输入、调用位置与控制台结果，再逐个改变条件。事件和异步实验保留触发顺序，避免在生产页面执行带有未知副作用的调试代码。

## 3. 用对照区分原因

下表列出需要主动改变的条件。预期行为来自机制分析，复现时还需记录运行环境和原始输出，不能将预期当作已经测得的结果。

| 改变的条件 | 需要验证的行为 |
| --- | --- |
| 局部声明与外部同名 | 前一次读取指向局部绑定 |
| 赋值语句尚未执行 | 局部值仍为 undefined |
| 改成不存在的标识符 | 读取可能抛 ReferenceError |

### 对照 1：局部声明与外部同名

前一次读取指向局部绑定。观察时记录函数内部作用域解析。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 2：赋值语句尚未执行

局部值仍为 undefined。观察时记录实际语句执行顺序。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 3：改成不存在的标识符

读取可能抛 ReferenceError。观察时记录未声明与已声明未赋值区别。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。

## 4. 适用条件与取舍

理解提升有助阅读旧代码，但编写新代码仍应在清楚位置声明变量。避免依赖读者记忆隐式规则才能理解一段业务逻辑。

一次正常运行只覆盖了这组输入。继续扩展前，应把上面的异常对照保留下来，尤其关注“改成不存在的标识符”这一分支。后续方案若改变了图中任意一处依赖，原来的判断就要重新验证，不能仅凭界面相似或返回值相同沿用结论。

## 同月延伸

- [深入 JavaScript：循环回调为什么都读到最后一个值](/tech/2016/03/15/js-closure-loop/)
- [深入 JavaScript：this 由调用方式决定什么](/tech/2016/03/25/js-this-call-site/)

## 参考资料

1. [ECMAScript 5.1 规范](https://262.ecma-international.org/5.1/)
2. [HTML5 浏览器处理模型](https://www.w3.org/TR/2014/REC-html5-20141028/)
