---
layout: post
title: Node-RED 异常处理：重试应有边界和原始身份
subtitle: 异常节点接回输入口，看起来实现了自动恢复，也可能形成无限循环与消息洪峰。
date: 2018-03-25 08:00:00 +0800
author: edyang
header-style: text
catalog: true
tags:
- Node-RED
- 物联网
tech_note: true
note_id: nodered-error-retry-branch
permalink: /tech/2018/03/25/nodered-error-retry-branch/
excerpt: 异常节点接回输入口，看起来实现了自动恢复，也可能形成无限循环与消息洪峰。
privacy_reviewed: true
content_revision: 3
images:
- /img/tech-notes/nodered-error-retry-branch.svg
technology_since: '2018-01-31'
---

异常节点接回输入口，看起来实现了自动恢复，也可能形成无限循环与消息洪峰。

本文使用Node-RED 0.18、匹配的 Node.js 与演示消息。Node-RED（可视化流程工具）让接线与转换直观可见，但消息结构、状态归属和异常仍需要设计。连接线存在不说明传入字段符合下游要求。

## 1. 从现象推到机制

错误恢复需要区分临时故障、非法输入和已经执行但结果未知。重试消息保留业务身份并增加尝试次数，等待采用退避。不能把每次失败都改成新命令，否则会绕过下游幂等。

![Node-RED 异常处理：重试应有边界和原始身份的处理、反馈与观察关系](/img/tech-notes/nodered-error-retry-branch.svg)

图中的四个节点分别表示错误来源、原因分类、有限重试、人工复核。顺着实线检查输入如何变成输出，再沿虚线核对反馈条件。图示表达的是本文讨论的关系，不是实测曲线或现场截图。

## 2. 最小实现与输入条件

Catch 节点收集支持的错误，结合明确分支处理。设置最大次数并转入待人工查看队列，日志保留最初错误而不只显示最后一次。

```text
failure -> classify
transient and retryable -> delayed bounded retry
invalid input -> reject with reason
unknown side effect -> query existing result
exhausted -> review record
```

先用 Inject 和 Debug 节点检查消息，再连接模拟输入输出。部署前查看变更范围，避免把无关流程重启；账号和密钥通过凭据配置管理，不写进公开导出的流程。

## 3. 用对照区分原因

下表列出需要主动改变的条件。预期行为来自机制分析，复现时还需记录运行环境和原始输出，不能将预期当作已经测得的结果。

| 改变的条件 | 需要验证的行为 |
| --- | --- |
| 无效字段导致失败 | 不应重复尝试相同非法输入 |
| 临时网络断开 | 可以在预算内延后重试 |
| 设备可能已执行命令 | 先查询结果而非生成新命令 |

### 对照 1：无效字段导致失败

不应重复尝试相同非法输入。观察时记录错误类别与字段问题。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 2：临时网络断开

可以在预算内延后重试。观察时记录尝试次数与退避间隔。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 3：设备可能已执行命令

先查询结果而非生成新命令。观察时记录稳定业务身份与状态反馈。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。

## 4. 适用条件与取舍

不是所有节点错误都会以相同方式进入 Catch。需要核对节点实现和状态输出，不能只画一条错误线就认定覆盖全部故障。

一次正常运行只覆盖了这组输入。继续扩展前，应把上面的异常对照保留下来，尤其关注“设备可能已执行命令”这一分支。后续方案若改变了图中任意一处依赖，原来的判断就要重新验证，不能仅凭界面相似或返回值相同沿用结论。

## 同月延伸

- [Node-RED 入门：先看完整 msg，再接下一根线](/tech/2018/03/05/nodered018-message-schema/)
- [Node-RED 状态：context、flow 与 global 的归属](/tech/2018/03/15/nodered-context-lifecycle/)

## 参考资料

1. [Node-RED 0.18 发布说明](https://nodered.org/blog/2018/01/31/version-0-18-released)
2. [Node-RED 0.18 源码](https://github.com/node-red/node-red/tree/0.18.0)
