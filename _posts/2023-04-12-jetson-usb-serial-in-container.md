---
layout: post
title: Jetson 串口接入 Node-RED 容器的排查过程
subtitle: USB 转串口插到 Jetson 后，宿主机已经出现设备节点，Node-RED 的串口列表却没有它。
date: 2023-04-12 08:00:00 +0800
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
updated_at: '2026-10-13T17:59:15+08:00'
verification: partial
privacy_reviewed: true
permalink: /tech/2026/05/15/jetson-usb-serial-in-container/
excerpt: USB 转串口插到 Jetson 后，宿主机已经出现设备节点，Node-RED 的串口列表却没有它。
archive_date: '2023-04-12'
date_basis: simulated_weekly_archive
content_revision: 2
images:
- /img/tech-notes/jetson-usb-serial-in-container.svg
---

USB 转串口插到 Jetson 后，宿主机已经出现设备节点，Node-RED 的串口列表却没有它。这个现象让我把排查重点从反复刷新页面，移到宿主机与容器之间的设备访问边界。

## 研究与排查过程

第一步查看 lsusb、内核日志和设备节点，确认 USB 枚举、驱动绑定与持续连接。接下来进入容器核对相同路径是否存在、运行用户是否有访问权限。宿主机识别成功只能证明前一层可用；容器不具备对应设备映射时，上层串口节点不会凭刷新获得访问能力。

![Jetson 串口接入 Node-RED 容器的排查过程研究路径示意](/img/tech-notes/jetson-usb-serial-in-container.svg)

## 涉及的技术与取舍

方案采用 Docker devices 映射，并对照串口组权限与容器运行用户。Compose 修改后需要重建相关容器，使设备配置生效。多适配器场景还讨论了 udev 稳定名称，避免热插拔改变临时编号；但稳定命名不会修复驱动或权限问题，热插拔后的实际访问仍要测试。

### 辅助检查示例

以下为通用示例，用于理解上述检查；变量、设备和参数需对应实际环境。

```bash
lsusb
sudo dmesg --ctime | tail -n 60
ls -l /dev/ttyUSB* /dev/ttyCH341USB* /dev/ttyACM* 2>/dev/null
```

```yaml
services:
  nodered:
    devices:
      - /dev/ttyUSB0:/dev/ttyUSB0
```

## 这轮研究的结论

原记录确认宿主机识别而容器不可见，没有随后映射成功的回执。结论是按 USB、驱动、设备节点、容器权限和业务通信逐层验证。先打通设备访问，再读一个已知寄存器，才能确认串口接入不只是界面上出现了一个名称。

## 参考资料

- [Docker 设备访问与运行参数](https://docs.docker.com/reference/cli/docker/container/run/#device)
- [Node-RED Docker 文档](https://nodered.org/docs/getting-started/docker)
