---
layout: post
title: Node-RED 工程化：流程文件之外还要保存什么
subtitle: 导入 flows.json 后缺节点，说明交付遗漏了运行依赖。
date: 2019-03-25 08:00:00 +0800
author: edyang
header-style: text
catalog: true
tags:
- Node-RED
- 边缘流程
tech_note: true
note_id: nodered-flow-project-dependencies
permalink: /tech/2019/03/25/nodered-flow-project-dependencies/
excerpt: 导入 flows.json 后缺节点，说明交付遗漏了运行依赖。
privacy_reviewed: true
content_revision: 3
images:
- /img/tech-notes/nodered-flow-project-dependencies.svg
technology_since: '2018-08-14'
---

导入 flows.json 后缺节点，说明交付遗漏了运行依赖。可视化流程也需要工程清单。

本文使用Node-RED 0.19、文件上下文存储与独立流程目录。流程可视化之后，还需要清楚的版本、状态和测试输入。编辑器画面不是完整交付，运行配置、凭据与安装节点版本也影响行为。

## 1. 从现象推到机制

流程、凭据配置、settings、依赖节点和运行时版本共同构成环境。导出的公开流程不应含真实账号与地址。依赖升级可能改变节点行为，不能把编辑器能打开等同于运行兼容。

![Node-RED 工程化：流程文件之外还要保存什么的处理、反馈与观察关系](/img/tech-notes/nodered-flow-project-dependencies.svg)

图中的四个节点分别表示流程结构、运行依赖、凭据配置、独立恢复。顺着实线检查输入如何变成输出，再沿虚线核对反馈条件。图示表达的是本文讨论的关系，不是实测曲线或现场截图。

## 2. 最小实现与输入条件

建立最小 package 清单与部署说明，先在干净演示目录恢复。凭据通过受控步骤重新配置，不把原环境密钥复制到公开文件。

```text
bundle -> sanitized flow + dependency versions
runtime -> Node.js and Node-RED version
settings -> non-secret required options
credentials -> separately provisioned
verification -> fixed replay fixtures
```

先导出脱敏演示流程并记录依赖，使用固定消息回放。部署前核对变更范围，重启和异常退出分别验证；导出文件不能携带真实令牌或私人连接信息。

## 3. 用对照区分原因

下表列出需要主动改变的条件。预期行为来自机制分析，复现时还需记录运行环境和原始输出，不能将预期当作已经测得的结果。

| 改变的条件 | 需要验证的行为 |
| --- | --- |
| 只导入流程但未装依赖 | 会出现未知节点或运行失败 |
| 升级节点后输出改变 | 需要契约回放验证 |
| 把凭据直接写进函数节点 | 公开导出会暴露秘密 |

### 对照 1：只导入流程但未装依赖

会出现未知节点或运行失败。观察时记录缺失节点类型与安装版本。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 2：升级节点后输出改变

需要契约回放验证。观察时记录新旧字段与错误行为。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 3：把凭据直接写进函数节点

公开导出会暴露秘密。观察时记录最终流程文本与配置边界。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。

## 4. 适用条件与取舍

备份应能恢复到独立环境并验证关键路径。只有一个导出文件而没有恢复演练，不能宣称完成可恢复交付。

一次正常运行只覆盖了这组输入。继续扩展前，应把上面的异常对照保留下来，尤其关注“把凭据直接写进函数节点”这一分支。后续方案若改变了图中任意一处依赖，原来的判断就要重新验证，不能仅凭界面相似或返回值相同沿用结论。

## 同月延伸

- [Node-RED 0.19：文件上下文不等于每次写入立刻落盘](/tech/2019/03/05/nodered019-file-context-durability/)
- [Node-RED 流程验证：用固定消息回放检查转换](/tech/2019/03/15/nodered-flow-replay-test/)

## 参考资料

1. [Node-RED 0.19 发布说明](https://nodered.org/blog/2018/08/14/version-0-19-released)
2. [Node-RED 0.19 源码](https://github.com/node-red/node-red/tree/0.19.0)
