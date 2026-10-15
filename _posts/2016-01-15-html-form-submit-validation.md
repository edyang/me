---
layout: post
title: 深入 HTML：表单提交的默认行为与校验
subtitle: 点击按钮突然刷新页面，有时不是 JavaScript 失效，而是按钮处在表单内并触发默认提交。
date: 2016-01-15 08:00:00 +0800
author: edyang
header-style: text
catalog: true
tags:
- 前端
- HTML
- CSS
tech_note: true
note_id: html-form-submit-validation
permalink: /tech/2016/01/15/html-form-submit-validation/
excerpt: 点击按钮突然刷新页面，有时不是 JavaScript 失效，而是按钮处在表单内并触发默认提交。
privacy_reviewed: true
content_revision: 3
images:
- /img/tech-notes/html-form-submit-validation.svg
technology_since: '2014-10-28'
---

点击按钮突然刷新页面，有时不是 JavaScript 失效，而是按钮处在表单内并触发默认提交。

本文使用HTML5、CSS 与当时浏览器可支持的布局能力，示例为局部页面。页面表现由文档结构、布局规则和浏览器环境共同决定。本文以可核对的 DOM（文档对象模型）和样式计算为起点，不使用后续才普及的布局属性。

## 1. 从现象推到机制

表单的 action、method 和控件 name 决定提交方式与字段。button 未明确 type 时可能承担提交角色；前端拦截提交需要清楚处理默认行为。浏览器 required 等约束只改善交互，服务器仍需验证。

![深入 HTML：表单提交的默认行为与校验的处理、反馈与观察关系](/img/tech-notes/html-form-submit-validation.svg)

图中的四个节点分别表示控件定义、浏览器约束、提交动作、服务端校验。顺着实线检查输入如何变成输出，再沿虚线核对反馈条件。图示表达的是本文讨论的关系，不是实测曲线或现场截图。

## 2. 最小实现与输入条件

使用演示查询表单分别观察 GET 参数与提交事件。非提交按钮显式写 type，错误提示与字段关联。

```html
<form action="/demo/search" method="get">
  <label for="q">关键词</label>
  <input id="q" name="q" required>
  <button type="submit">查询</button>
  <button type="button">清空条件</button>
</form>
```

将片段放进带 UTF-8 声明和 viewport 设置的演示页。使用开发者工具检查实际盒尺寸、计算样式与请求；多浏览器或移动端结论需要在相应环境重新验证。

## 3. 用对照区分原因

下表列出需要主动改变的条件。预期行为来自机制分析，复现时还需记录运行环境和原始输出，不能将预期当作已经测得的结果。

| 改变的条件 | 需要验证的行为 |
| --- | --- |
| 输入框没有 name | 可能不会作为命名字段提交 |
| 非提交按钮漏写类型 | 可能触发表单提交 |
| 绕过浏览器约束发请求 | 服务端仍必须拒绝非法输入 |

### 对照 1：输入框没有 name

可能不会作为命名字段提交。观察时记录实际请求参数。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 2：非提交按钮漏写类型

可能触发表单提交。观察时记录按钮默认类型与所在表单。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 3：绕过浏览器约束发请求

服务端仍必须拒绝非法输入。观察时记录服务端校验与错误响应。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。

## 4. 适用条件与取舍

GET 适合不会改变状态的读取，不应用于删除与付款。字段出现在地址中时还会进入历史和日志，敏感内容不能随意放入查询参数。

一次正常运行只覆盖了这组输入。继续扩展前，应把上面的异常对照保留下来，尤其关注“绕过浏览器约束发请求”这一分支。后续方案若改变了图中任意一处依赖，原来的判断就要重新验证，不能仅凭界面相似或返回值相同沿用结论。

## 同月延伸

- [深入 HTML：语义结构比 div 数量更重要](/tech/2016/01/05/html5-semantic-document/)
- [深入 HTML：图片尺寸、比例与页面跳动](/tech/2016/01/25/html-image-responsive-dimensions/)

## 参考资料

1. [HTML5 2014 推荐标准](https://www.w3.org/TR/2014/REC-html5-20141028/)
2. [CSS 2.1 标准](https://www.w3.org/TR/CSS21/)
