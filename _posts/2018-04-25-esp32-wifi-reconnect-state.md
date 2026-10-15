---
layout: post
title: ESP32 联网：连接、取地址与业务上线分开
subtitle: Wi-Fi 连接事件出现，不表示设备已经拿到地址，更不表示 MQTT 业务已经恢复。
date: 2018-04-25 08:00:00 +0800
author: edyang
header-style: text
catalog: true
tags:
- ESP32
- 嵌入式
tech_note: true
note_id: esp32-wifi-reconnect-state
permalink: /tech/2018/04/25/esp32-wifi-reconnect-state/
excerpt: Wi-Fi 连接事件出现，不表示设备已经拿到地址，更不表示 MQTT 业务已经恢复。
privacy_reviewed: true
content_revision: 3
images:
- /img/tech-notes/esp32-wifi-reconnect-state.svg
technology_since: '2017-09-01'
---

Wi-Fi 连接事件出现，不表示设备已经拿到地址，更不表示 MQTT 业务已经恢复。

本文使用经典 ESP32、ESP-IDF v2.1 与隔离低压演示电路。ESP-IDF（乐鑫开发框架）版本会改变接口与工具链。本文固定早期开发环境，GPIO 编号、电压和外设复用按具体开发板原理图核对，不把板子排针顺序当芯片引脚编号。

## 1. 从现象推到机制

无线关联、地址获取、路由和业务会话有不同状态。重连应有退避，恢复后要重新建立依赖连接与订阅。把所有失败都直接复位，会丢掉定位证据并可能形成循环。

![ESP32 联网：连接、取地址与业务上线分开的处理、反馈与观察关系](/img/tech-notes/esp32-wifi-reconnect-state.svg)

图中的四个节点分别表示无线关联、地址获取、业务会话、健康报告。顺着实线检查输入如何变成输出，再沿虚线核对反馈条件。图示表达的是本文讨论的关系，不是实测曲线或现场截图。

## 2. 最小实现与输入条件

按 v2.1 的事件回调建立状态机，具体事件名以固定源码为准。断开演示热点，观察地址与业务连接分别如何恢复。

```text
DISCONNECTED -> ASSOCIATING -> WAIT_IP -> NETWORK_READY
NETWORK_READY -> MQTT_CONNECTING -> SUBSCRIBED
on failure -> bounded delay and retry
record last cause before recovery action
```

先检查供电与串口，再在独立工程验证。仅使用额定范围内的低压信号，输入不能因为“只是测试”越过芯片限制；烧录成功与外设运行需要分别记录。

## 3. 用对照区分原因

下表列出需要主动改变的条件。预期行为来自机制分析，复现时还需记录运行环境和原始输出，不能将预期当作已经测得的结果。

| 改变的条件 | 需要验证的行为 |
| --- | --- |
| 无线关联成功但未取地址 | 业务连接不应提前认定就绪 |
| 网络恢复但订阅未重建 | 命令通道仍可能不可用 |
| 反复快速重连 | 可能增加功耗并挤压其他任务 |

### 对照 1：无线关联成功但未取地址

业务连接不应提前认定就绪。观察时记录地址事件与接口状态。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 2：网络恢复但订阅未重建

命令通道仍可能不可用。观察时记录代理会话与订阅结果。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 3：反复快速重连

可能增加功耗并挤压其他任务。观察时记录重试间隔和失败原因。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。

## 4. 适用条件与取舍

连接状态不能替代数据新鲜度。设备即使在线，传感器采样失败也应报告独立质量问题。

一次正常运行只覆盖了这组输入。继续扩展前，应把上面的异常对照保留下来，尤其关注“反复快速重连”这一分支。后续方案若改变了图中任意一处依赖，原来的判断就要重新验证，不能仅凭界面相似或返回值相同沿用结论。

## 同月延伸

- [ESP32 入门：先打通编译、烧录和串口监视](/tech/2018/04/05/esp32-idf21-flash-monitor/)
- [ESP32 采样：ADC 原始值不能直接当电压](/tech/2018/04/15/esp32-adc-raw-calibration/)

## 参考资料

1. [ESP-IDF v2.1 源码与文档](https://github.com/espressif/esp-idf/tree/v2.1)
2. [ESP32 数据手册](https://www.espressif.com/sites/default/files/documentation/esp32_datasheet_en.pdf)
