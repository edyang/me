---
layout: post
title: RS485 connected 与 timeout 循环：把四层问题分开查
subtitle: 串口打开成功不代表设备响应成功。USB、权限、协议和业务解析要逐层确认。
date: 2026-06-10 08:00:00 +0800
author: edyang
header-style: text
catalog: true
tags:
- 串口
- Modbus
- Node-RED
tech_note: true
note_id: modbus-timeout-layered-debug
source_date: '2026-06-10'
source_dates:
- '2026-06-10'
- '2026-07-03'
published_at: '2026-10-12T12:51:43+08:00'
updated_at: '2026-10-12T12:51:43+08:00'
verification: partial
privacy_reviewed: true
permalink: /tech/2026/06/10/modbus-timeout-layered-debug/
excerpt: 串口打开成功不代表设备响应成功。USB、权限、协议和业务解析要逐层确认。
---

Node-RED 显示 connected，过一会儿又 timeout，容易让人以为通信偶尔正常。实际上，connected 往往只意味着串口打开成功，设备有没有返回正确的 Modbus 帧还需要另查。

## 四层检查各自看什么

| 层次 | 证据 |
| --- | --- |
| USB 与驱动 | 是否持续枚举，是否有 disconnect 日志 |
| 设备访问 | 路径是否正确，运行用户能否打开端口 |
| Modbus 通信 | 地址、波特率、校验、功能码、寄存器与 CRC |
| 业务解释 | 数据类型、字节序、比例、单位与有效值 |

那次记录既出现过 USB 断开日志，也出现过命令行 `Permission denied`。后续观察又发现 USB 不再掉线，但业务仍重连。说明排查结论必须随着证据更新，不能一直套用第一次怀疑。

## 用一个读取工具验证协议

先停止其它轮询程序，用单个工具只读一个文档明确支持的寄存器，保留请求与原始回包。地址、功能码和寄存器起点按厂家手册核对；不要把一个模块的命令复制给另一个模块。

如果能够持续读到回包，再回到 Node-RED 配置轮询间隔和超时。一个串口总线通常应由一个通信主站协调访问，避免多个程序同时读写。

## 稳定名称解决的是路径，不是协议

udev 名称能减少设备编号变化造成的故障，但不会修复接线、地址或波特率错误。建立软链接后，宿主机和容器仍要分别确认链接最终指向以及访问权限。

历史对话没有完整的最终成功回执。因此这篇不提供“万能修复命令”，而是保留逐层排除的检查顺序。

## 参考资料

- [Modbus 官方规范](https://www.modbus.org/specs.php)
