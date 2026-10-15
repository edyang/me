---
layout: post
title: 大众尚酷车灯研究：网关可能隔开诊断口与目标模块
subtitle: 诊断接口能看到一些车辆数据，不代表可以直接访问灯光模块所在的全部网段。
date: 2017-12-05 08:00:00 +0800
author: edyang
header-style: text
catalog: true
tags:
- 车联网
- CAN总线
tech_note: true
note_id: scirocco-can-gateway-topology
permalink: /tech/2017/12/05/scirocco-can-gateway-topology/
excerpt: 诊断接口能看到一些车辆数据，不代表可以直接访问灯光模块所在的全部网段。
privacy_reviewed: true
content_revision: 3
images:
- /img/tech-notes/scirocco-can-gateway-topology.svg
technology_since: '2013-01-01'
---

诊断接口能看到一些车辆数据，不代表可以直接访问灯光模块所在的全部网段。

本文使用Linux SocketCAN、can-utils 与隔离台架或 vcan 虚拟总线。CAN（控制器局域网）定义传输与仲裁，不提供通用的车型信号字典。大众尚酷的具体网段、信号位和校验方式必须靠对应资料与验证，本文不把演示标识符当成实车控制报文。

## 1. 从现象推到机制

车辆网络可能由多个速率与用途不同的网段组成，网关只转发允许的信息。诊断服务、状态广播与直接控制也有不同协议关系。看到灯状态可能是经过网关的反馈，并不证明同一路径接受控制请求。

![大众尚酷车灯研究：网关可能隔开诊断口与目标模块的处理、反馈与观察关系](/img/tech-notes/scirocco-can-gateway-topology.svg)

图中的四个节点分别表示接入位置、网关边界、目标模块、证据状态。顺着实线检查输入如何变成输出，再沿虚线核对反馈条件。图示表达的是本文讨论的关系，不是实测曲线或现场截图。

## 2. 最小实现与输入条件

先根据对应车辆资料画出接入点、网关和目标模块的关系，所有未知连线标为待核实。没有资料时只做观测，不通过未知引脚试错。

```text
observation point -> confirmed accessible bus
gateway -> documented forwarding / diagnostic behavior
target module -> model-specific interface
unknown path -> unresolved, no guessed control frame
```

默认先分析离线日志或使用 vcan。真实总线观测需确认适配器处于正确只听模式与电气接入条件；主动发送只在独立台架、已确认协议与可停止条件下讨论，不在行驶车辆试错。

## 3. 用对照区分原因

下表列出需要主动改变的条件。预期行为来自机制分析，复现时还需记录运行环境和原始输出，不能将预期当作已经测得的结果。

| 改变的条件 | 需要验证的行为 |
| --- | --- |
| 诊断口只出现部分状态 | 可能受网关与网段范围限制 |
| 能读取灯光反馈 | 不等于可沿同路由主动控制 |
| 换车型版本后行为不同 | 需重新核对模块与协议 |

### 对照 1：诊断口只出现部分状态

可能受网关与网段范围限制。观察时记录实际接入网段与资料。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 2：能读取灯光反馈

不等于可沿同路由主动控制。观察时记录信号方向与服务类型。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 3：换车型版本后行为不同

需重新核对模块与协议。观察时记录车辆版本和软件身份。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。

## 4. 适用条件与取舍

拓扑图应反映已知与未知，不用完整漂亮的连线掩盖缺证据。主动控制讨论必须建立在已确认的模块与协议上。

一次正常运行只覆盖了这组输入。继续扩展前，应把上面的异常对照保留下来，尤其关注“换车型版本后行为不同”这一分支。后续方案若改变了图中任意一处依赖，原来的判断就要重新验证，不能仅凭界面相似或返回值相同沿用结论。

## 同月延伸

- [车灯控制台架：先在 vcan 上验证左右灯状态机](/tech/2017/12/15/can-vcan-turn-signal-state/)
- [车灯控制研究：命令已发出与灯真正改变要分开验证](/tech/2017/12/25/can-control-feedback-stop/)

## 参考资料

1. [Linux SocketCAN 文档](https://www.kernel.org/doc/Documentation/networking/can.txt)
2. [linux-can/can-utils](https://github.com/linux-can/can-utils)
