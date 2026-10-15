---
layout: post
title: ESP32 看门狗：喂狗要反映真实进度
subtitle: 独立定时器一直喂狗，业务线程即使卡死也可能不重启。
date: 2019-02-25 08:00:00 +0800
author: edyang
header-style: text
catalog: true
tags:
- ESP32
- 设备管理
tech_note: true
note_id: esp32-watchdog-task-health
permalink: /tech/2019/02/25/esp32-watchdog-task-health/
excerpt: 独立定时器一直喂狗，业务线程即使卡死也可能不重启。
privacy_reviewed: true
content_revision: 3
images:
- /img/tech-notes/esp32-watchdog-task-health.svg
technology_since: '2018-09-01'
---

独立定时器一直喂狗，业务线程即使卡死也可能不重启。健康信号需要来自真正工作。

本文使用经典 ESP32 与 ESP-IDF v3.1，使用独立测试分区和低压台架。固件状态、持久配置与远端目标需要分别管理。本文按早期 ESP-IDF 版本讨论，不默认后续框架的自动回滚和安全功能已经配置完成。

## 1. 从现象推到机制

看门狗监测指定时间内是否收到服务信号，但信号含义由应用决定。任务活着、循环在跑和采样成功是不同状态。长阻塞需要限制等待，不能简单放宽全部超时把问题隐藏。

![ESP32 看门狗：喂狗要反映真实进度的处理、反馈与观察关系](/img/tech-notes/esp32-watchdog-task-health.svg)

图中的四个节点分别表示真实工作、有限等待、监督判断、恢复记录。顺着实线检查输入如何变成输出，再沿虚线核对反馈条件。图示表达的是本文讨论的关系，不是实测曲线或现场截图。

## 2. 最小实现与输入条件

为采样与网络任务分别记录进度计数，在监督任务中检查更新。复位前尽量保留有限故障原因，避免循环重启后完全失去证据。

```text
sampler_progress -> advances after valid sampling step
network_progress -> advances after bounded state transition
supervisor -> verify required progress windows
recovery -> record reason, then use documented watchdog policy
```

先备份演示配置并准备串口恢复入口，再在独立开发板验证。记录固件、分区表与启动日志，主动断电实验只用于可恢复的台架，不能在唯一在用设备上试错。

## 3. 用对照区分原因

下表列出需要主动改变的条件。预期行为来自机制分析，复现时还需记录运行环境和原始输出，不能将预期当作已经测得的结果。

| 改变的条件 | 需要验证的行为 |
| --- | --- |
| 喂狗线程正常但采样卡住 | 不能据此认定业务健康 |
| 网络短时断开 | 应按设计重连而非立即重启 |
| 连续重启仍不能恢复 | 需要保留原因并限制重启循环 |

### 对照 1：喂狗线程正常但采样卡住

不能据此认定业务健康。观察时记录各关键任务进度而非统一心跳。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 2：网络短时断开

应按设计重连而非立即重启。观察时记录故障时长与恢复预算。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 3：连续重启仍不能恢复

需要保留原因并限制重启循环。观察时记录启动次数与最后错误。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。

## 4. 适用条件与取舍

看门狗是最后一道恢复机制之一，不替代资源释放和错误处理。恢复后的状态与未完成命令也需要重新核对。

一次正常运行只覆盖了这组输入。继续扩展前，应把上面的异常对照保留下来，尤其关注“连续重启仍不能恢复”这一分支。后续方案若改变了图中任意一处依赖，原来的判断就要重新验证，不能仅凭界面相似或返回值相同沿用结论。

## 同月延伸

- [ESP32 配置持久化：NVS 键值也需要版本](/tech/2019/02/05/esp32-nvs-config-version/)
- [ESP32 OTA：下载完成之前先设计失败恢复](/tech/2019/02/15/esp32-ota-partition-recovery/)

## 参考资料

1. [ESP-IDF v3.1 历史源码](https://github.com/espressif/esp-idf/tree/v3.1)
2. [ESP-IDF v3.1 分区文档](https://github.com/espressif/esp-idf/blob/v3.1/docs/en/api-guides/partition-tables.rst)
