---
layout: post
title: ESP32 OTA：下载完成之前先设计失败恢复
subtitle: 无线升级不只是把固件下载到设备。
date: 2019-02-15 08:00:00 +0800
author: edyang
header-style: text
catalog: true
tags:
- ESP32
- 设备管理
tech_note: true
note_id: esp32-ota-partition-recovery
permalink: /tech/2019/02/15/esp32-ota-partition-recovery/
excerpt: 无线升级不只是把固件下载到设备。
privacy_reviewed: true
content_revision: 3
images:
- /img/tech-notes/esp32-ota-partition-recovery.svg
technology_since: '2018-09-01'
---

无线升级不只是把固件下载到设备。分区、校验、启动选择与恢复入口共同决定能否安全更新。

本文使用经典 ESP32 与 ESP-IDF v3.1，使用独立测试分区和低压台架。固件状态、持久配置与远端目标需要分别管理。本文按早期 ESP-IDF 版本讨论，不默认后续框架的自动回滚和安全功能已经配置完成。

## 1. 从现象推到机制

OTA（空中升级）通常写入非当前运行的应用分区，再验证并切换启动目标。早期框架能力需要按实际配置核对，不能假设自动回滚已经可用。新固件能启动也可能无法联网，需要单独设计健康确认与恢复策略。

![ESP32 OTA：下载完成之前先设计失败恢复的处理、反馈与观察关系](/img/tech-notes/esp32-ota-partition-recovery.svg)

图中的四个节点分别表示运行分区、候选下载、校验切换、恢复入口。顺着实线检查输入如何变成输出，再沿虚线核对反馈条件。图示表达的是本文讨论的关系，不是实测曲线或现场截图。

## 2. 最小实现与输入条件

先在测试板准备双应用分区和串口恢复，使用无业务数据固件。比较下载中断、校验失败和启动后依赖失败。

```text
running partition -> keep intact during download
new partition -> bounded download and image validation
boot selection -> only after verified image
recovery -> documented serial or verified fallback procedure
```

先备份演示配置并准备串口恢复入口，再在独立开发板验证。记录固件、分区表与启动日志，主动断电实验只用于可恢复的台架，不能在唯一在用设备上试错。

## 3. 用对照区分原因

下表列出需要主动改变的条件。预期行为来自机制分析，复现时还需记录运行环境和原始输出，不能将预期当作已经测得的结果。

| 改变的条件 | 需要验证的行为 |
| --- | --- |
| 下载途中断开 | 当前运行分区应保持可用 |
| 镜像校验失败 | 不能切换到无效镜像 |
| 新镜像启动但联网失败 | 需要业务健康与恢复条件 |

### 对照 1：下载途中断开

当前运行分区应保持可用。观察时记录分区写入目标与启动选择。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 2：镜像校验失败

不能切换到无效镜像。观察时记录校验返回与分区状态。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 3：新镜像启动但联网失败

需要业务健康与恢复条件。观察时记录启动成功与服务可用分别判断。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。

## 4. 适用条件与取舍

镜像摘要只能证明内容一致，来源认证还需可信传输与签名等机制。具体安全与回滚能力以该版本实现和配置为准。

一次正常运行只覆盖了这组输入。继续扩展前，应把上面的异常对照保留下来，尤其关注“新镜像启动但联网失败”这一分支。后续方案若改变了图中任意一处依赖，原来的判断就要重新验证，不能仅凭界面相似或返回值相同沿用结论。

## 同月延伸

- [ESP32 配置持久化：NVS 键值也需要版本](/tech/2019/02/05/esp32-nvs-config-version/)
- [ESP32 看门狗：喂狗要反映真实进度](/tech/2019/02/25/esp32-watchdog-task-health/)

## 参考资料

1. [ESP-IDF v3.1 历史源码](https://github.com/espressif/esp-idf/tree/v3.1)
2. [ESP-IDF v3.1 分区文档](https://github.com/espressif/esp-idf/blob/v3.1/docs/en/api-guides/partition-tables.rst)
