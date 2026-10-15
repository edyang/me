---
layout: post
title: Node-RED 入门：先看完整 msg，再接下一根线
subtitle: Debug 面板里只有一个数字，很难知道下游期待的 topic、时间和设备身份是否还在。
date: 2018-03-05 08:00:00 +0800
author: edyang
header-style: text
catalog: true
tags:
- Node-RED
- 物联网
tech_note: true
note_id: nodered018-message-schema
permalink: /tech/2018/03/05/nodered018-message-schema/
excerpt: Debug 面板里只有一个数字，很难知道下游期待的 topic、时间和设备身份是否还在。
privacy_reviewed: true
content_revision: 3
images:
- /img/tech-notes/nodered018-message-schema.svg
technology_since: '2018-01-31'
---

Debug 面板里只有一个数字，很难知道下游期待的 topic、时间和设备身份是否还在。

本文使用Node-RED 0.18、匹配的 Node.js 与演示消息。Node-RED（可视化流程工具）让接线与转换直观可见，但消息结构、状态归属和异常仍需要设计。连接线存在不说明传入字段符合下游要求。

## 1. 从现象推到机制

msg 是沿流程传递的对象，payload 只是其中一个字段。节点可能重写字段或产生新对象，转换时若只返回 payload，就可能丢掉设备身份与关联号。消息结构应该像接口一样有约定。

![Node-RED 入门：先看完整 msg，再接下一根线的处理、反馈与观察关系](/img/tech-notes/nodered018-message-schema.svg)

图中的四个节点分别表示输入节点、字段转换、结构校验、下游输出。顺着实线检查输入如何变成输出，再沿虚线核对反馈条件。图示表达的是本文讨论的关系，不是实测曲线或现场截图。

## 2. 最小实现与输入条件

使用完整消息 Debug，给合成数据添加 schema_version。转换只改需要字段，异常数据送到明确分支而不是继续下传。

```javascript
var value = Number(msg.payload);
if (!isFinite(value)) {
  node.error("invalid demo value", msg);
  return null;
}
msg.payload = { value: value, unit: "degC", schema_version: 1 };
return msg;
```

先用 Inject 和 Debug 节点检查消息，再连接模拟输入输出。部署前查看变更范围，避免把无关流程重启；账号和密钥通过凭据配置管理，不写进公开导出的流程。

## 3. 用对照区分原因

下表列出需要主动改变的条件。预期行为来自机制分析，复现时还需记录运行环境和原始输出，不能将预期当作已经测得的结果。

| 改变的条件 | 需要验证的行为 |
| --- | --- |
| 载荷是非数字字符串 | 应进入异常路径而不是生成 NaN |
| 节点新建对象但漏设备号 | 下游可能失去数据归属 |
| 多个来源接入同一流程 | 需要统一契约再处理 |

### 对照 1：载荷是非数字字符串

应进入异常路径而不是生成 NaN。观察时记录转换前后的类型与输出。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 2：节点新建对象但漏设备号

下游可能失去数据归属。观察时记录完整 msg 的字段变化。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 3：多个来源接入同一流程

需要统一契约再处理。观察时记录各来源类型与版本。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。

## 4. 适用条件与取舍

消息调试应使用演示或脱敏内容。完整消息可能包含凭据与私人字段，公共分享前必须删除无关数据。

一次正常运行只覆盖了这组输入。继续扩展前，应把上面的异常对照保留下来，尤其关注“多个来源接入同一流程”这一分支。后续方案若改变了图中任意一处依赖，原来的判断就要重新验证，不能仅凭界面相似或返回值相同沿用结论。

## 同月延伸

- [Node-RED 状态：context、flow 与 global 的归属](/tech/2018/03/15/nodered-context-lifecycle/)
- [Node-RED 异常处理：重试应有边界和原始身份](/tech/2018/03/25/nodered-error-retry-branch/)

## 参考资料

1. [Node-RED 0.18 发布说明](https://nodered.org/blog/2018/01/31/version-0-18-released)
2. [Node-RED 0.18 源码](https://github.com/node-red/node-red/tree/0.18.0)
