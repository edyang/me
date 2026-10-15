---
layout: post
title: 深入 JavaScript：this 由调用方式决定什么
subtitle: 把对象方法赋给另一个变量后再调用，this 可能不再指向原来的对象。
date: 2016-03-25 08:00:00 +0800
author: edyang
header-style: text
catalog: true
tags:
- JavaScript
- 前端原理
tech_note: true
note_id: js-this-call-site
permalink: /tech/2016/03/25/js-this-call-site/
excerpt: 把对象方法赋给另一个变量后再调用，this 可能不再指向原来的对象。
privacy_reviewed: true
content_revision: 3
images:
- /img/tech-notes/js-this-call-site.svg
technology_since: '2011-06-01'
---

把对象方法赋给另一个变量后再调用，this 可能不再指向原来的对象。方法位置和调用方式并不相同。

本文使用ECMAScript 5.1 与浏览器 DOM，代码可放入独立演示页。JavaScript（脚本语言）的作用域、函数调用与事件调度，需要与浏览器提供的接口区分。本文主体使用当时已经可用的语法，不把语言版本和宿主环境混为一谈。

## 1. 从现象推到机制

普通函数的 this 与调用形式有关，对象点调用会提供相应接收者，独立调用则按严格模式等规则处理。call、apply 和 bind 可以显式建立调用上下文。闭包捕获变量与 this 绑定属于不同机制。

![深入 JavaScript：this 由调用方式决定什么的处理、反馈与观察关系](/img/tech-notes/js-this-call-site.svg)

图中的四个节点分别表示函数定义、调用位置、显式绑定、后续使用。顺着实线检查输入如何变成输出，再沿虚线核对反馈条件。图示表达的是本文讨论的关系，不是实测曲线或现场截图。

## 2. 最小实现与输入条件

比较点调用、独立调用和 bind 后调用。使用严格模式让隐式全局绑定问题更早暴露，不靠全局变量偶然存在掩盖错误。

```javascript
"use strict";
var counter = { value: 3, read: function() { return this.value; } };
var read = counter.read;
var bound = read.bind(counter);
console.log(bound());
```

先记录输入、调用位置与控制台结果，再逐个改变条件。事件和异步实验保留触发顺序，避免在生产页面执行带有未知副作用的调试代码。

## 3. 用对照区分原因

下表列出需要主动改变的条件。预期行为来自机制分析，复现时还需记录运行环境和原始输出，不能将预期当作已经测得的结果。

| 改变的条件 | 需要验证的行为 |
| --- | --- |
| 通过对象点调用 | this 对应调用接收者 |
| 方法脱离对象独立调用 | 上下文可能不再是原对象 |
| 使用 bind 固定接收者 | 后续调用使用绑定上下文 |

### 对照 1：通过对象点调用

this 对应调用接收者。观察时记录调用表达式的左侧对象。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 2：方法脱离对象独立调用

上下文可能不再是原对象。观察时记录严格模式下实际 this。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 3：使用 bind 固定接收者

后续调用使用绑定上下文。观察时记录绑定后的函数与原函数。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。

## 4. 适用条件与取舍

bind 产生新的函数引用，注册事件后解绑时需要保留这份引用。每次重新 bind 再移除事件，不会自动匹配原来的处理器。

一次正常运行只覆盖了这组输入。继续扩展前，应把上面的异常对照保留下来，尤其关注“使用 bind 固定接收者”这一分支。后续方案若改变了图中任意一处依赖，原来的判断就要重新验证，不能仅凭界面相似或返回值相同沿用结论。

## 同月延伸

- [深入 JavaScript：变量提升不会替你完成赋值](/tech/2016/03/05/js-scope-hoisting/)
- [深入 JavaScript：循环回调为什么都读到最后一个值](/tech/2016/03/15/js-closure-loop/)

## 参考资料

1. [ECMAScript 5.1 规范](https://262.ecma-international.org/5.1/)
2. [HTML5 浏览器处理模型](https://www.w3.org/TR/2014/REC-html5-20141028/)
