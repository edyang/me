---
layout: post
title: 树莓派研究：UART 能接上软件之前先确认电平
subtitle: 串口编号、TX/RX 和电平都正确，才有机会讨论协议。
date: 2018-06-25 08:00:00 +0800
author: edyang
header-style: text
catalog: true
tags:
- 树莓派
- Linux
tech_note: true
note_id: raspberrypi-uart-voltage
permalink: /tech/2018/06/25/raspberrypi-uart-voltage/
excerpt: 串口编号、TX/RX 和电平都正确，才有机会讨论协议。
privacy_reviewed: true
content_revision: 3
images:
- /img/tech-notes/raspberrypi-uart-voltage.svg
technology_since: '2016-02-29'
---

串口编号、TX/RX 和电平都正确，才有机会讨论协议。GPIO 不能因为接口长得像就直接连接。

本文使用树莓派 3 Model B 与 Raspbian，使用独立测试存储卡。树莓派把 Linux 软件环境与实际供电、存储和接口连接起来。命令执行成功不证明电气连接正确，服务运行也不代表采集数据具有正确单位。

## 1. 从现象推到机制

UART（异步串行接口）定义收发时序，TTL 电平、RS-232 和 RS-485 并不是同一种电气接口。树莓派 GPIO 的电压限制需要遵守，外设供电与信号地关系也要按手册确认。

![树莓派研究：UART 能接上软件之前先确认电平的处理、反馈与观察关系](/img/tech-notes/raspberrypi-uart-voltage.svg)

图中的四个节点分别表示电气规格、线序关系、串口参数、协议解析。顺着实线检查输入如何变成输出，再沿虚线核对反馈条件。图示表达的是本文讨论的关系，不是实测曲线或现场截图。

## 2. 最小实现与输入条件

先使用已知兼容的 USB 串口适配器做回环，再接隔离的演示外设。核对波特率、数据位、校验位和停止位，保留原始字节。

```text
electrical compatibility -> verified adapter
TX -> peer RX, RX -> peer TX, reference ground by design
serial settings -> baud, data bits, parity, stop bits
raw bytes -> protocol decoder
```

记录板型、系统镜像和外设连接，先做单层验证再组合。操作使用有相应权限的普通账号，系统级调整才提升权限；不要把临时调试账户长期暴露在公共网络。

## 3. 用对照区分原因

下表列出需要主动改变的条件。预期行为来自机制分析，复现时还需记录运行环境和原始输出，不能将预期当作已经测得的结果。

| 改变的条件 | 需要验证的行为 |
| --- | --- |
| 参数相同但电平不同 | 不能靠软件设置解决电气不兼容 |
| 收到乱码但有字节 | 先检查串口参数与实际编码 |
| 设备名变化 | 应用需要稳定识别或受控配置 |

### 对照 1：参数相同但电平不同

不能靠软件设置解决电气不兼容。观察时记录适配器与外设规格。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 2：收到乱码但有字节

先检查串口参数与实际编码。观察时记录原始字节和帧格式。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 3：设备名变化

应用需要稳定识别或受控配置。观察时记录实际端口身份与权限。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。

## 4. 适用条件与取舍

未知接口不做直接短接试验。硬件确认之后再处理协议，避免把设备损坏风险当成调试成本。

一次正常运行只覆盖了这组输入。继续扩展前，应把上面的异常对照保留下来，尤其关注“设备名变化”这一分支。后续方案若改变了图中任意一处依赖，原来的判断就要重新验证，不能仅凭界面相似或返回值相同沿用结论。

## 同月延伸

- [树莓派研究：随机重启先查供电与存储](/tech/2018/06/05/raspberrypi3-power-sd-reliability/)
- [树莓派研究：把采集脚本交给 systemd 管理](/tech/2018/06/15/raspberrypi-systemd-service/)

## 参考资料

1. [树莓派 3 发布说明](https://www.raspberrypi.com/news/raspberry-pi-3-on-sale/)
2. [Raspberry Pi 官方文档](https://www.raspberrypi.com/documentation/)
