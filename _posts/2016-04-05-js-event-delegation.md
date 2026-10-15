---
layout: post
title: 深入 JavaScript：事件委托为何适合动态列表
subtitle: 列表不断添加新行，为每行单独绑定处理器会增加管理成本。
date: 2016-04-05 08:00:00 +0800
author: edyang
header-style: text
catalog: true
tags:
- JavaScript
- 前端原理
tech_note: true
note_id: js-event-delegation
permalink: /tech/2016/04/05/js-event-delegation/
excerpt: 列表不断添加新行，为每行单独绑定处理器会增加管理成本。
privacy_reviewed: true
content_revision: 3
images:
- /img/tech-notes/js-event-delegation.svg
technology_since: '2011-06-01'
---

列表不断添加新行，为每行单独绑定处理器会增加管理成本。事件委托利用传播关系统一处理。

本文使用ECMAScript 5.1 与浏览器 DOM，代码可放入独立演示页。JavaScript（脚本语言）的作用域、函数调用与事件调度，需要与浏览器提供的接口区分。本文主体使用当时已经可用的语法，不把语言版本和宿主环境混为一谈。

## 1. 从现象推到机制

事件目标是最初触发的元素，当前处理元素则是绑定监听器的节点。点击行内图标时，target 可能不是按钮本身，因此需要向上寻找符合条件的元素，并限制在委托容器范围。

![深入 JavaScript：事件委托为何适合动态列表的处理、反馈与观察关系](/img/tech-notes/js-event-delegation.svg)

图中的四个节点分别表示原始目标、传播路径、匹配动作、统一处理。顺着实线检查输入如何变成输出，再沿虚线核对反馈条件。图示表达的是本文讨论的关系，不是实测曲线或现场截图。

## 2. 最小实现与输入条件

在固定列表容器上监听点击，用 data 属性判断动作。动态新增行时不再单独绑定，删除容器时也统一释放监听。

```javascript
list.addEventListener("click", function(event) {
  var node = event.target;
  while (node && node !== list) {
    if (node.getAttribute("data-action") === "open") {
      openItem(node.getAttribute("data-id")); return;
    }
    node = node.parentNode;
  }
});
```

先记录输入、调用位置与控制台结果，再逐个改变条件。事件和异步实验保留触发顺序，避免在生产页面执行带有未知副作用的调试代码。

## 3. 用对照区分原因

下表列出需要主动改变的条件。预期行为来自机制分析，复现时还需记录运行环境和原始输出，不能将预期当作已经测得的结果。

| 改变的条件 | 需要验证的行为 |
| --- | --- |
| 点击按钮内部图标 | 仍应定位到正确动作元素 |
| 动态添加新行 | 已有容器监听可处理传播事件 |
| 子元素停止传播 | 容器可能收不到事件 |

### 对照 1：点击按钮内部图标

仍应定位到正确动作元素。观察时记录target 与匹配节点。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 2：动态添加新行

已有容器监听可处理传播事件。观察时记录是否无需重复注册。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 3：子元素停止传播

容器可能收不到事件。观察时记录实际传播路径与拦截位置。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。

## 4. 适用条件与取舍

不是所有事件都以相同方式冒泡。焦点、进入离开等事件要按浏览器与事件类型核对，不能把点击委托规则套到全部交互。

一次正常运行只覆盖了这组输入。继续扩展前，应把上面的异常对照保留下来，尤其关注“子元素停止传播”这一分支。后续方案若改变了图中任意一处依赖，原来的判断就要重新验证，不能仅凭界面相似或返回值相同沿用结论。

## 同月延伸

- [深入 JavaScript：setTimeout 的零毫秒不是立即执行](/tech/2016/04/15/js-timer-event-loop/)
- [深入 JavaScript：搜索请求返回乱序怎样处理](/tech/2016/04/25/js-xhr-stale-response/)

## 参考资料

1. [ECMAScript 5.1 规范](https://262.ecma-international.org/5.1/)
2. [HTML5 浏览器处理模型](https://www.w3.org/TR/2014/REC-html5-20141028/)
