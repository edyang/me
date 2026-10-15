---
layout: post
title: ESP32 配置持久化：NVS 键值也需要版本
subtitle: 固件升级后读取旧配置失败，可能是字段类型和配置结构已经改变。
date: 2019-02-05 08:00:00 +0800
author: edyang
header-style: text
catalog: true
tags:
- ESP32
- 设备管理
tech_note: true
note_id: esp32-nvs-config-version
permalink: /tech/2019/02/05/esp32-nvs-config-version/
excerpt: 固件升级后读取旧配置失败，可能是字段类型和配置结构已经改变。
privacy_reviewed: true
content_revision: 3
images:
- /img/tech-notes/esp32-nvs-config-version.svg
technology_since: '2018-09-01'
---

固件升级后读取旧配置失败，可能是字段类型和配置结构已经改变。持久值需要迁移规则。

本文使用经典 ESP32 与 ESP-IDF v3.1，使用独立测试分区和低压台架。固件状态、持久配置与远端目标需要分别管理。本文按早期 ESP-IDF 版本讨论，不默认后续框架的自动回滚和安全功能已经配置完成。

## 1. 从现象推到机制

NVS（非易失键值存储）保存命名空间与键值，应用仍需处理缺键、类型变化和写入失败。把配置写进存储不代表已经提交完成，默认值也应区分首次使用与损坏恢复。

![ESP32 配置持久化：NVS 键值也需要版本的处理、反馈与观察关系](/img/tech-notes/esp32-nvs-config-version.svg)

图中的四个节点分别表示配置读取、兼容迁移、受控提交、重启验证。顺着实线检查输入如何变成输出，再沿虚线核对反馈条件。图示表达的是本文讨论的关系，不是实测曲线或现场截图。

## 2. 最小实现与输入条件

用演示计数和配置版本检查读取结果，写后执行提交并检查返回。下列片段放入返回 esp_err_t 的函数，真实网络凭据不出现在代码与串口日志。

```c
nvs_handle handle;
esp_err_t result = nvs_open("demo", NVS_READWRITE, &handle);
if (result != ESP_OK) return result;
result = nvs_set_u32(handle, "cfg_version", 1);
if (result == ESP_OK) result = nvs_commit(handle);
nvs_close(handle);
return result; // 只有 ESP_OK 才报告持久保存成功
```

先备份演示配置并准备串口恢复入口，再在独立开发板验证。记录固件、分区表与启动日志，主动断电实验只用于可恢复的台架，不能在唯一在用设备上试错。

## 3. 用对照区分原因

下表列出需要主动改变的条件。预期行为来自机制分析，复现时还需记录运行环境和原始输出，不能将预期当作已经测得的结果。

| 改变的条件 | 需要验证的行为 |
| --- | --- |
| 配置键不存在 | 按首次初始化规则处理 |
| 写入后未成功提交 | 不能向用户报告已经持久保存 |
| 新固件字段类型变化 | 需要明确迁移或拒绝旧结构 |

### 对照 1：配置键不存在

按首次初始化规则处理。观察时记录错误码与默认值来源。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 2：写入后未成功提交

不能向用户报告已经持久保存。观察时记录提交返回值与重启读取。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 3：新固件字段类型变化

需要明确迁移或拒绝旧结构。观察时记录存储版本与目标结构。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。

## 4. 适用条件与取舍

高频采样不适合逐条写配置存储。写入频率、耐久性和数据量应按介质能力设计，配置与时间序列分开保存。

一次正常运行只覆盖了这组输入。继续扩展前，应把上面的异常对照保留下来，尤其关注“新固件字段类型变化”这一分支。后续方案若改变了图中任意一处依赖，原来的判断就要重新验证，不能仅凭界面相似或返回值相同沿用结论。

## 同月延伸

- [ESP32 OTA：下载完成之前先设计失败恢复](/tech/2019/02/15/esp32-ota-partition-recovery/)
- [ESP32 看门狗：喂狗要反映真实进度](/tech/2019/02/25/esp32-watchdog-task-health/)

## 参考资料

1. [ESP-IDF v3.1 历史源码](https://github.com/espressif/esp-idf/tree/v3.1)
2. [ESP-IDF v3.1 分区文档](https://github.com/espressif/esp-idf/blob/v3.1/docs/en/api-guides/partition-tables.rst)
