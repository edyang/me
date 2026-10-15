---
layout: post
title: 车灯控制研究：命令已发出与灯真正改变要分开验证
subtitle: 发送函数返回成功，只说明数据进入某层发送流程，不能直接作为物理动作完成证据。
date: 2017-12-25 08:00:00 +0800
author: edyang
header-style: text
catalog: true
tags:
- 车联网
- CAN总线
tech_note: true
note_id: can-control-feedback-stop
permalink: /tech/2017/12/25/can-control-feedback-stop/
excerpt: 发送函数返回成功，只说明数据进入某层发送流程，不能直接作为物理动作完成证据。
privacy_reviewed: true
content_revision: 3
images:
- /img/tech-notes/can-control-feedback-stop.svg
technology_since: '2013-01-01'
---

发送函数返回成功，只说明数据进入某层发送流程，不能直接作为物理动作完成证据。

本文使用Linux SocketCAN、can-utils 与隔离台架或 vcan 虚拟总线。CAN（控制器局域网）定义传输与仲裁，不提供通用的车型信号字典。大众尚酷的具体网段、信号位和校验方式必须靠对应资料与验证，本文不把演示标识符当成实车控制报文。

## 1. 从现象推到机制

台架控制要定义命令、接收确认、模块状态和独立物理观察。四者可能分别成功或失败。停止策略也需要独立设计，通信中断后不能无条件保持上次测试意图；具体默认状态由硬件与已确认协议决定。

![车灯控制研究：命令已发出与灯真正改变要分开验证的处理、反馈与观察关系](/img/tech-notes/can-control-feedback-stop.svg)

图中的四个节点分别表示控制意图、传输结果、模块反馈、物理观察。顺着实线检查输入如何变成输出，再沿虚线核对反馈条件。图示表达的是本文讨论的关系，不是实测曲线或现场截图。

## 2. 最小实现与输入条件

以独立指示灯台架记录请求编号、发送时刻、反馈与观察结果。先验证人工停止和断链处理，再开展重复动作，不使用未经确认的尚酷控制报文。

```text
request -> encoded command -> transport acceptance
module feedback -> reported state
independent observation -> actual lamp state
stop path -> explicit timeout and operator stop condition
```

默认先分析离线日志或使用 vcan。真实总线观测需确认适配器处于正确只听模式与电气接入条件；主动发送只在独立台架、已确认协议与可停止条件下讨论，不在行驶车辆试错。

## 3. 用对照区分原因

下表列出需要主动改变的条件。预期行为来自机制分析，复现时还需记录运行环境和原始输出，不能将预期当作已经测得的结果。

| 改变的条件 | 需要验证的行为 |
| --- | --- |
| 发送成功但没有状态反馈 | 任务不能标为物理完成 |
| 模块报告状态但灯未变化 | 需要继续查执行与观测链路 |
| 通信中途断开 | 按台架规则进入可停止状态 |

### 对照 1：发送成功但没有状态反馈

任务不能标为物理完成。观察时记录发送返回与反馈证据。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 2：模块报告状态但灯未变化

需要继续查执行与观测链路。观察时记录独立光电或人工观察。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 3：通信中途断开

按台架规则进入可停止状态。观察时记录超时策略和人工停止是否有效。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。

## 4. 适用条件与取舍

进入实车阶段前仍需对应资料、适配器条件与静止验证方案。本文建立验收方法，不声称完成了真实车辆控制或道路测试。

一次正常运行只覆盖了这组输入。继续扩展前，应把上面的异常对照保留下来，尤其关注“通信中途断开”这一分支。后续方案若改变了图中任意一处依赖，原来的判断就要重新验证，不能仅凭界面相似或返回值相同沿用结论。

## 同月延伸

- [大众尚酷车灯研究：网关可能隔开诊断口与目标模块](/tech/2017/12/05/scirocco-can-gateway-topology/)
- [车灯控制台架：先在 vcan 上验证左右灯状态机](/tech/2017/12/15/can-vcan-turn-signal-state/)

## 参考资料

1. [Linux SocketCAN 文档](https://www.kernel.org/doc/Documentation/networking/can.txt)
2. [linux-can/can-utils](https://github.com/linux-can/can-utils)
