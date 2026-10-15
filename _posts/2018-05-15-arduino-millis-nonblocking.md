---
layout: post
title: Arduino 编程：用 millis 替代长时间 delay
subtitle: 长时间 delay 让灯按计划闪，却也让按键与通信处理暂停。
date: 2018-05-15 08:00:00 +0800
author: edyang
header-style: text
catalog: true
tags:
- Arduino
- 嵌入式
tech_note: true
note_id: arduino-millis-nonblocking
permalink: /tech/2018/05/15/arduino-millis-nonblocking/
excerpt: 长时间 delay 让灯按计划闪，却也让按键与通信处理暂停。
privacy_reviewed: true
content_revision: 3
images:
- /img/tech-notes/arduino-millis-nonblocking.svg
technology_since: '2017-09-28'
---

长时间 delay 让灯按计划闪，却也让按键与通信处理暂停。多个任务需要协作式安排。

本文使用Arduino IDE 1.8.5、Uno 级演示板与该版本配套核心库。Arduino（开源微控制器平台）简化编译和烧录，仍需要理解循环、计时与硬件状态。不同板卡的电压、编号和库支持不能互相默认兼容。

## 1. 从现象推到机制

loop 持续检查当前时间与上次执行时间，让每个短任务按条件运行。millis 使用无符号计数，差值比较可以在合理间隔内处理回绕，不应简单判断 now 是否大于 last 加 interval。

![Arduino 编程：用 millis 替代长时间 delay的处理、反馈与观察关系](/img/tech-notes/arduino-millis-nonblocking.svg)

图中的四个节点分别表示当前时间、间隔判断、短任务执行、其他任务。顺着实线检查输入如何变成输出，再沿虚线核对反馈条件。图示表达的是本文讨论的关系，不是实测曲线或现场截图。

## 2. 最小实现与输入条件

把灯闪烁与串口读取放到同一循环，限制每次处理工作量。下面为非阻塞计时片段，last 在外部初始化。

```cpp
unsigned long now = millis();
if ((unsigned long)(now - last) >= interval) {
  last = now;
  ledState = !ledState;
  digitalWrite(LED_BUILTIN, ledState);
}
// 继续处理短小的串口或按键任务
```

从串口输出和板载灯开始，外部电路先确认限流与供电。示例避免市电负载；库版本、板卡选项与编译输出需要一起保留，方便换电脑后复现。

## 3. 用对照区分原因

下表列出需要主动改变的条件。预期行为来自机制分析，复现时还需记录运行环境和原始输出，不能将预期当作已经测得的结果。

| 改变的条件 | 需要验证的行为 |
| --- | --- |
| 把 delay 改成时间条件 | 循环能继续响应其他短任务 |
| 计数接近无符号回绕 | 差值法在约定间隔内仍可判断 |
| 某任务自身阻塞很久 | 其他任务仍会延迟 |

### 对照 1：把 delay 改成时间条件

循环能继续响应其他短任务。观察时记录按键响应与循环周期。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 2：计数接近无符号回绕

差值法在约定间隔内仍可判断。观察时记录变量类型与间隔上限。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 3：某任务自身阻塞很久

其他任务仍会延迟。观察时记录每段实际执行时长。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。

## 4. 适用条件与取舍

这种方式不是抢占式实时调度。严格时序或中断任务需要另行设计，不能把忙循环当成所有硬实时控制的通用方案。

一次正常运行只覆盖了这组输入。继续扩展前，应把上面的异常对照保留下来，尤其关注“某任务自身阻塞很久”这一分支。后续方案若改变了图中任意一处依赖，原来的判断就要重新验证，不能仅凭界面相似或返回值相同沿用结论。

## 同月延伸

- [Arduino 环境：板卡核心与库版本怎样共同影响编译](/tech/2018/05/05/arduino18-board-library-version/)
- [Arduino 串口：先定义一条命令怎样结束](/tech/2018/05/25/arduino-serial-command-framing/)

## 参考资料

1. [Arduino IDE 1.8.5 历史源码](https://github.com/arduino/Arduino/tree/1.8.5)
2. [Arduino 内置示例](https://docs.arduino.cc/built-in-examples/)
