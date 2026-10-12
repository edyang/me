---
layout: post
title: Arduino 工具链下载超时：下载与安装分开检查
subtitle: 开发板包安装失败时，先找具体失败的下载资源，再确认代理和缓存状态。
date: 2026-06-25 08:00:00 +0800
author: edyang
header-style: text
catalog: true
tags:
- 嵌入式
- Arduino
- 故障排查
tech_note: true
note_id: arduino-toolchain-download-timeout
source_date: '2026-06-25'
source_dates:
- '2026-06-25'
published_at: '2026-10-12T12:51:43+08:00'
updated_at: '2026-10-12T12:51:43+08:00'
verification: partial
privacy_reviewed: true
permalink: /tech/2026/06/25/arduino-toolchain-download-timeout/
excerpt: 开发板包安装失败时，先找具体失败的下载资源，再确认代理和缓存状态。
---

在 macOS 上安装 ESP32 开发板支持包时，失败位置是工具链下载，而不是编译代码。重复点安装会增加等待，却不一定改变失败原因。

## 找到失败的文件和来源

保存完整错误中的资源地址、文件名、目标平台和连接阶段。区分连接超时、下载中断、校验失败和解压失败；它们的处理方式并不相同。macOS 的 CPU 架构也应与工具包匹配。

## 代理要进入实际下载进程

浏览器可以下载，不代表 Arduino CLI 或 IDE 使用了同样的代理。先用当前工具支持的配置方式设置代理，再验证一个小资源。公开排查记录只保留配置方法，代理认证信息和个人路径应去除。

## 缓存只清理明确出错的部分

如果下载中断留下不完整文件，可以检查对应缓存并重新下载。不要在没有证据时删除全部开发环境。为了可复现，应固定开发板包版本，记录 CLI/IDE 版本及平台架构。

最终检查应包含：开发板包安装成功、能编译一个最小示例、USB 串口可识别，再验证上传。工具链安装和上传成功是两个不同里程碑。

原交流提出过重试、代理和指定版本等方案，但没有用户确认安装完成。这篇记录的是定位下载问题的顺序，不把建议写成成功结果。

## 参考资料

- [Arduino CLI 配置](https://docs.arduino.cc/arduino-cli/configuration/)
