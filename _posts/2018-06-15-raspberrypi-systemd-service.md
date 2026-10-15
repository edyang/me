---
layout: post
title: 树莓派研究：把采集脚本交给 systemd 管理
subtitle: SSH 断开后采集停止，说明脚本仍依赖终端会话。
date: 2018-06-15 08:00:00 +0800
author: edyang
header-style: text
catalog: true
tags:
- 树莓派
- Linux
tech_note: true
note_id: raspberrypi-systemd-service
permalink: /tech/2018/06/15/raspberrypi-systemd-service/
excerpt: SSH 断开后采集停止，说明脚本仍依赖终端会话。
privacy_reviewed: true
content_revision: 3
images:
- /img/tech-notes/raspberrypi-systemd-service.svg
technology_since: '2016-02-29'
---

SSH 断开后采集停止，说明脚本仍依赖终端会话。长期服务需要明确启动与退出管理。

本文使用树莓派 3 Model B 与 Raspbian，使用独立测试存储卡。树莓派把 Linux 软件环境与实际供电、存储和接口连接起来。命令执行成功不证明电气连接正确，服务运行也不代表采集数据具有正确单位。

## 1. 从现象推到机制

systemd（服务管理器）按单元配置运行身份、工作目录、重启和日志。network.target 不等于外部服务已经可用，脚本仍需处理连接失败。不断重启也不能修复永久配置错误。

![树莓派研究：把采集脚本交给 systemd 管理的处理、反馈与观察关系](/img/tech-notes/raspberrypi-systemd-service.svg)

图中的四个节点分别表示单元配置、前台进程、错误退出、业务就绪。顺着实线检查输入如何变成输出，再沿虚线核对反馈条件。图示表达的是本文讨论的关系，不是实测曲线或现场截图。

## 2. 最小实现与输入条件

在已创建演示账号和目录后写单元片段。脚本前台运行，标准输出进入日志，不把后台化和服务管理混用。

```ini
[Service]
User=demo
WorkingDirectory=/opt/demo-sampler
ExecStart=/usr/bin/python3 /opt/demo-sampler/main.py
Restart=on-failure
RestartSec=5
```

记录板型、系统镜像和外设连接，先做单层验证再组合。操作使用有相应权限的普通账号，系统级调整才提升权限；不要把临时调试账户长期暴露在公共网络。

## 3. 用对照区分原因

下表列出需要主动改变的条件。预期行为来自机制分析，复现时还需记录运行环境和原始输出，不能将预期当作已经测得的结果。

| 改变的条件 | 需要验证的行为 |
| --- | --- |
| 终端断开 | 受管服务不依赖该会话存活 |
| 外部网络尚未就绪 | 脚本需要有界重连 |
| 配置错误反复退出 | 应定位原因而非无限加速重启 |

### 对照 1：终端断开

受管服务不依赖该会话存活。观察时记录服务主进程与日志。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 2：外部网络尚未就绪

脚本需要有界重连。观察时记录启动顺序与实际连接结果。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 3：配置错误反复退出

应定位原因而非无限加速重启。观察时记录退出码和首条错误。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。

## 4. 适用条件与取舍

实际账号和目录要由部署过程创建并设定权限。服务运行不应默认使用 root，只有必要设备权限按范围授予。

一次正常运行只覆盖了这组输入。继续扩展前，应把上面的异常对照保留下来，尤其关注“配置错误反复退出”这一分支。后续方案若改变了图中任意一处依赖，原来的判断就要重新验证，不能仅凭界面相似或返回值相同沿用结论。

## 同月延伸

- [树莓派研究：随机重启先查供电与存储](/tech/2018/06/05/raspberrypi3-power-sd-reliability/)
- [树莓派研究：UART 能接上软件之前先确认电平](/tech/2018/06/25/raspberrypi-uart-voltage/)

## 参考资料

1. [树莓派 3 发布说明](https://www.raspberrypi.com/news/raspberry-pi-3-on-sale/)
2. [Raspberry Pi 官方文档](https://www.raspberrypi.com/documentation/)
