---
layout: post
title: Node-RED 流程验证：用固定消息回放检查转换
subtitle: 节点分别能跑，串起来却字段丢失。
date: 2019-03-15 08:00:00 +0800
author: edyang
header-style: text
catalog: true
tags:
- Node-RED
- 边缘流程
tech_note: true
note_id: nodered-flow-replay-test
permalink: /tech/2019/03/15/nodered-flow-replay-test/
excerpt: 节点分别能跑，串起来却字段丢失。
privacy_reviewed: true
content_revision: 3
images:
- /img/tech-notes/nodered-flow-replay-test.svg
technology_since: '2018-08-14'
---

节点分别能跑，串起来却字段丢失。固定输入回放有助于验证整条数据契约。

本文使用Node-RED 0.19、文件上下文存储与独立流程目录。流程可视化之后，还需要清楚的版本、状态和测试输入。编辑器画面不是完整交付，运行配置、凭据与安装节点版本也影响行为。

## 1. 从现象推到机制

每个转换的输入输出应有明确结构与错误分支。把相同样本回放到新旧流程，可以定位字段变化。时间相关和随机行为需控制，外部写入节点在验证时替换为演示输出，避免回放重复触发动作。

![Node-RED 流程验证：用固定消息回放检查转换的处理、反馈与观察关系](/img/tech-notes/nodered-flow-replay-test.svg)

图中的四个节点分别表示固定样本、流程版本、隔离回放、差异核对。顺着实线检查输入如何变成输出，再沿虚线核对反馈条件。图示表达的是本文讨论的关系，不是实测曲线或现场截图。

## 2. 最小实现与输入条件

准备合法、缺字段、重复和超限消息，Debug 保存完整脱敏结果。把流程版本和依赖节点版本一并记录。

```text
fixtures -> valid, missing_field, duplicate, out_of_range
replay -> transformation-only demo flow
assert -> schema, identity, unit, quality
external effects -> stub output for review
```

先导出脱敏演示流程并记录依赖，使用固定消息回放。部署前核对变更范围，重启和异常退出分别验证；导出文件不能携带真实令牌或私人连接信息。

## 3. 用对照区分原因

下表列出需要主动改变的条件。预期行为来自机制分析，复现时还需记录运行环境和原始输出，不能将预期当作已经测得的结果。

| 改变的条件 | 需要验证的行为 |
| --- | --- |
| 输入缺少设备编号 | 应进入明确错误分支 |
| 新流程改变单位 | 需要同步契约而非静默替换 |
| 回放连接到真实控制节点 | 可能重复执行外部动作 |

### 对照 1：输入缺少设备编号

应进入明确错误分支。观察时记录完整输出是否仍有归属。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 2：新流程改变单位

需要同步契约而非静默替换。观察时记录单位字段与数值换算。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 3：回放连接到真实控制节点

可能重复执行外部动作。观察时记录测试出口是否被隔离。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。

## 4. 适用条件与取舍

回放覆盖的是给定样本，仍需实际协议与负载验证。新增故障证据应补入样本，避免同类回归反复出现。

一次正常运行只覆盖了这组输入。继续扩展前，应把上面的异常对照保留下来，尤其关注“回放连接到真实控制节点”这一分支。后续方案若改变了图中任意一处依赖，原来的判断就要重新验证，不能仅凭界面相似或返回值相同沿用结论。

## 同月延伸

- [Node-RED 0.19：文件上下文不等于每次写入立刻落盘](/tech/2019/03/05/nodered019-file-context-durability/)
- [Node-RED 工程化：流程文件之外还要保存什么](/tech/2019/03/25/nodered-flow-project-dependencies/)

## 参考资料

1. [Node-RED 0.19 发布说明](https://nodered.org/blog/2018/08/14/version-0-19-released)
2. [Node-RED 0.19 源码](https://github.com/node-red/node-red/tree/0.19.0)
