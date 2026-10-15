---
layout: post
title: Node-RED 状态：context、flow 与 global 的归属
subtitle: 两个设备共用一个计数变量，会让状态互相串扰。
date: 2018-03-15 08:00:00 +0800
author: edyang
header-style: text
catalog: true
tags:
- Node-RED
- 物联网
tech_note: true
note_id: nodered-context-lifecycle
permalink: /tech/2018/03/15/nodered-context-lifecycle/
excerpt: 两个设备共用一个计数变量，会让状态互相串扰。
privacy_reviewed: true
content_revision: 3
images:
- /img/tech-notes/nodered-context-lifecycle.svg
technology_since: '2018-01-31'
---

两个设备共用一个计数变量，会让状态互相串扰。状态范围应该跟业务对象一致。

本文使用Node-RED 0.18、匹配的 Node.js 与演示消息。Node-RED（可视化流程工具）让接线与转换直观可见，但消息结构、状态归属和异常仍需要设计。连接线存在不说明传入字段符合下游要求。

## 1. 从现象推到机制

节点、流程和全局上下文有不同可见范围。扩大范围只是让更多节点能访问，不会自动按设备隔离。本文的 0.18 环境不假设内存上下文重启后持久保存，必要状态需独立存储。

![Node-RED 状态：context、flow 与 global 的归属的处理、反馈与观察关系](/img/tech-notes/nodered-context-lifecycle.svg)

图中的四个节点分别表示业务身份、上下文范围、存储能力、清理恢复。顺着实线检查输入如何变成输出，再沿虚线核对反馈条件。图示表达的是本文讨论的关系，不是实测曲线或现场截图。

## 2. 最小实现与输入条件

计数以设备号建立键，明确初始化和清理条件。把可重建缓存与必须保存的业务状态分开，不依赖运行内存当唯一账本。

```javascript
var key = "count:" + msg.device_id;
var value = context.get(key) || 0;
context.set(key, value + 1);
msg.count = value + 1;
return msg;
```

先用 Inject 和 Debug 节点检查消息，再连接模拟输入输出。部署前查看变更范围，避免把无关流程重启；账号和密钥通过凭据配置管理，不写进公开导出的流程。

## 3. 用对照区分原因

下表列出需要主动改变的条件。预期行为来自机制分析，复现时还需记录运行环境和原始输出，不能将预期当作已经测得的结果。

| 改变的条件 | 需要验证的行为 |
| --- | --- |
| 两个设备交替上报 | 计数需要各自独立 |
| 流程重新部署或进程重启 | 内存状态不能当持久保证 |
| 设备退役后状态仍在 | 需要有清理策略 |

### 对照 1：两个设备交替上报

计数需要各自独立。观察时记录上下文键是否包含设备身份。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 2：流程重新部署或进程重启

内存状态不能当持久保证。观察时记录上下文存储能力与生命周期。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 3：设备退役后状态仍在

需要有清理策略。观察时记录状态数量与最后使用时刻。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。

## 4. 适用条件与取舍

状态隔离不只靠加前缀。若多个异步路径共同修改一个业务对象，还应分析读改写竞争和持久一致性。

一次正常运行只覆盖了这组输入。继续扩展前，应把上面的异常对照保留下来，尤其关注“设备退役后状态仍在”这一分支。后续方案若改变了图中任意一处依赖，原来的判断就要重新验证，不能仅凭界面相似或返回值相同沿用结论。

## 同月延伸

- [Node-RED 入门：先看完整 msg，再接下一根线](/tech/2018/03/05/nodered018-message-schema/)
- [Node-RED 异常处理：重试应有边界和原始身份](/tech/2018/03/25/nodered-error-retry-branch/)

## 参考资料

1. [Node-RED 0.18 发布说明](https://nodered.org/blog/2018/01/31/version-0-18-released)
2. [Node-RED 0.18 源码](https://github.com/node-red/node-red/tree/0.18.0)
