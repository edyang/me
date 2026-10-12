---
layout: post
title: Jetson 已识别 USB 串口，Node-RED 容器为什么看不到
subtitle: 宿主机识别设备，与容器拥有设备访问权限，是两层不同的问题。
date: 2026-05-15 08:00:00 +0800
author: edyang
header-style: text
catalog: true
tags:
- Jetson
- Docker
- Node-RED
- 串口
tech_note: true
note_id: jetson-usb-serial-in-container
source_date: '2026-05-15'
source_dates:
- '2026-05-15'
- '2026-07-03'
published_at: '2026-10-12T12:51:43+08:00'
updated_at: '2026-10-12T12:51:43+08:00'
verification: partial
privacy_reviewed: true
permalink: /tech/2026/05/15/jetson-usb-serial-in-container/
excerpt: 宿主机识别设备，与容器拥有设备访问权限，是两层不同的问题。
---

一次 USB 转 RS485 排查中，Jetson 已经出现串口设备节点，Node-RED 的串口列表却没有新增设备。继续在 Node-RED 里反复刷新，不能补上容器缺失的设备映射。

## 先确认宿主机这一层

先通过 `lsusb`、内核日志和 `/dev` 节点确认 USB 枚举与驱动绑定。日志中若明确显示其它服务抢占设备，应针对那条证据处理；不要把停用服务当成所有 CH340/CH341 设备的通用步骤。

```bash
lsusb
sudo dmesg --ctime | tail -n 60
ls -l /dev/ttyUSB* /dev/ttyCH341USB* /dev/ttyACM* 2>/dev/null
```

![USB、宿主机与容器访问分层](/img/tech-notes/serial.svg)

## 然后检查容器设备映射

设备路径、权限和运行用户都要在容器内再次确认。一个最小 Compose 片段如下，实际设备节点以宿主机识别结果为准：

```yaml
services:
  nodered:
    devices:
      - /dev/ttyUSB0:/dev/ttyUSB0
```

修改设备配置后，需要重建相关容器。仅重启页面不会改变容器创建时的设备配置。串口组权限也要检查，不应直接用全局特权模式掩盖缺失映射。

## 换设备后不要依赖临时编号

多个 USB 串口的编号可能变化。可以依据设备序列号和接口号建立稳定名称，但要确认不同适配器真的具有可区分的属性。USB 热插拔后映射是否继续有效，也必须按实际运行方式验证。

当时用户确认宿主机识别成功，容器仍不可见；历史记录没有随后容器映射成功的回执。这篇保留的是清晰的分层检查路径。

## 参考资料

- [Docker 设备访问与运行参数](https://docs.docker.com/reference/cli/docker/container/run/#device)
- [Node-RED Docker 文档](https://nodered.org/docs/getting-started/docker)
