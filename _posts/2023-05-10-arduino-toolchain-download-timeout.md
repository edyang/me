---
layout: post
title: ESP32 开发环境：排查 Arduino 工具链下载超时
subtitle: 在 macOS 安装 ESP32 开发板包时，失败发生在工具链下载阶段，代码还没有开始编译。
date: 2023-05-10 08:00:00 +0800
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
updated_at: '2026-10-13T17:59:15+08:00'
verification: partial
privacy_reviewed: true
permalink: /tech/2026/06/25/arduino-toolchain-download-timeout/
excerpt: 在 macOS 安装 ESP32 开发板包时，失败发生在工具链下载阶段，代码还没有开始编译。
archive_date: '2023-05-10'
date_basis: simulated_weekly_archive
content_revision: 2
images:
- /img/tech-notes/arduino-toolchain-download-timeout.svg
---

在 macOS 安装 ESP32 开发板包时，失败发生在工具链下载阶段，代码还没有开始编译。我需要先确认哪个资源失败，避免把网络问题当作示例代码或串口的问题。

## 研究与排查过程

讨论从错误资源地址、文件名、目标平台与失败阶段展开，区分连接超时、下载中断、校验失败和解压失败。随后核对 macOS 架构和工具包版本，再检查代理是否进入真正负责下载的 IDE 或 CLI 进程。浏览器能下载同一个文件，并不证明命令行使用了相同网络配置。

![ESP32 开发环境：排查 Arduino 工具链下载超时研究路径示意](/img/tech-notes/arduino-toolchain-download-timeout.svg)

## 涉及的技术与取舍

采用的技术包括 Arduino CLI 配置、版本固定和下载缓存检查。先验证小资源请求，再安装指定开发板包；只清理明确损坏的缓存，避免重建整套环境。安装完成后还需要编译最小示例，再确认串口与上传，三个阶段各自留结果，便于后来区分网络与硬件异常。

## 这轮研究的结论

这轮形成了代理、重试和指定版本的处理方案，没有安装完成的用户回执。结论是把下载和安装进度写清楚，先处理第一处失败；最终验收应覆盖编译与上传，而不是只看开发板包出现在列表里。

## 参考资料

- [Arduino CLI 配置](https://docs.arduino.cc/arduino-cli/configuration/)
