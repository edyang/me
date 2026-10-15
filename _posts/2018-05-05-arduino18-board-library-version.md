---
layout: post
title: Arduino 环境：板卡核心与库版本怎样共同影响编译
subtitle: 同一份 sketch 换电脑后不能编译，可能是板卡核心或库版本变化，而不是源码突然出错。
date: 2018-05-05 08:00:00 +0800
author: edyang
header-style: text
catalog: true
tags:
- Arduino
- 嵌入式
tech_note: true
note_id: arduino18-board-library-version
permalink: /tech/2018/05/05/arduino18-board-library-version/
excerpt: 同一份 sketch 换电脑后不能编译，可能是板卡核心或库版本变化，而不是源码突然出错。
privacy_reviewed: true
content_revision: 3
images:
- /img/tech-notes/arduino18-board-library-version.svg
technology_since: '2017-09-28'
---

同一份 sketch 换电脑后不能编译，可能是板卡核心或库版本变化，而不是源码突然出错。

本文使用Arduino IDE 1.8.5、Uno 级演示板与该版本配套核心库。Arduino（开源微控制器平台）简化编译和烧录，仍需要理解循环、计时与硬件状态。不同板卡的电压、编号和库支持不能互相默认兼容。

## 1. 从现象推到机制

板卡选择决定编译器、引脚定义和上传方式，库提供外设接口。多个同名库同时安装时，构建可能选择意料之外的路径。例程成功也要确认用的是哪块板和哪一份库。

![Arduino 环境：板卡核心与库版本怎样共同影响编译的处理、反馈与观察关系](/img/tech-notes/arduino18-board-library-version.svg)

图中的四个节点分别表示板卡目标、核心库、外设依赖、构建日志。顺着实线检查输入如何变成输出，再沿虚线核对反馈条件。图示表达的是本文讨论的关系，不是实测曲线或现场截图。

## 2. 最小实现与输入条件

先运行最小 Blink，再添加一个外设库，打开详细编译日志查看选中的文件来源。依赖一次只增加一个，保留版本清单。

```text
board: Uno demonstration target
core: explicit AVR core version
library: name + version + source
port: confirmed device
artifact: compilation log and sketch revision
```

从串口输出和板载灯开始，外部电路先确认限流与供电。示例避免市电负载；库版本、板卡选项与编译输出需要一起保留，方便换电脑后复现。

## 3. 用对照区分原因

下表列出需要主动改变的条件。预期行为来自机制分析，复现时还需记录运行环境和原始输出，不能将预期当作已经测得的结果。

| 改变的条件 | 需要验证的行为 |
| --- | --- |
| 选择了另一种板卡 | 可用 API 与编号可能不同 |
| 安装两个同名库 | 可能产生选择歧义 |
| 上传失败但编译正常 | 继续检查端口与下载模式 |

### 对照 1：选择了另一种板卡

可用 API 与编号可能不同。观察时记录实际编译目标和核心路径。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 2：安装两个同名库

可能产生选择歧义。观察时记录编译日志中的使用路径。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 3：上传失败但编译正常

继续检查端口与下载模式。观察时记录构建和烧录错误分开。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。

## 4. 适用条件与取舍

库示例不一定涵盖断线和异常。接入真实设备前还要核对电气条件、阻塞时长与失败返回值。

一次正常运行只覆盖了这组输入。继续扩展前，应把上面的异常对照保留下来，尤其关注“上传失败但编译正常”这一分支。后续方案若改变了图中任意一处依赖，原来的判断就要重新验证，不能仅凭界面相似或返回值相同沿用结论。

## 同月延伸

- [Arduino 编程：用 millis 替代长时间 delay](/tech/2018/05/15/arduino-millis-nonblocking/)
- [Arduino 串口：先定义一条命令怎样结束](/tech/2018/05/25/arduino-serial-command-framing/)

## 参考资料

1. [Arduino IDE 1.8.5 历史源码](https://github.com/arduino/Arduino/tree/1.8.5)
2. [Arduino 内置示例](https://docs.arduino.cc/built-in-examples/)
