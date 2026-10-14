---
layout: post
title: 用 systemd 管理后台服务：启动、退出和日志
subtitle: 终端里长期运行的程序，需要在主机启动后自动运行，并能保留退出原因。把命令追加一个 &，只解决当前终端阻塞，无法明确描述运行用户、工作目录和恢复条件。
date: 2020-02-03 08:00:00 +0800
author: edyang
header-style: text
catalog: true
tags:
- Linux
- 运维
tech_note: true
note_id: systemd-service-startup
permalink: /tech/2020/02/03/systemd-service-startup/
excerpt: 终端里长期运行的程序，需要在主机启动后自动运行，并能保留退出原因。把命令追加一个 &，只解决当前终端阻塞，无法明确描述运行用户、工作目录和恢复条件。
privacy_reviewed: true
content_revision: 3
images:
- /img/tech-notes/systemd-service-startup.svg
technology_since: '2019-01-01'
---

终端里长期运行的程序，需要在主机启动后自动运行，并能保留退出原因。把命令追加一个 &，只解决当前终端阻塞，无法明确描述运行用户、工作目录和恢复条件。

systemd 单元保存服务生命周期，Type=simple 的程序应在前台运行，由服务管理器跟踪主进程。WorkingDirectory、User、Environment 与 ExecStart 构成运行上下文；Restart 处理进程退出，不等于功能健康检查。

![用 systemd 管理后台服务：启动、退出和日志：处理路径与验证条件](/img/tech-notes/systemd-service-startup.svg)

## 一、问题的范围与前提

单台 Linux 主机上的进程、文件、网络和服务管理有各自边界。排查时先确认当前命令所处的用户、网络命名空间与工作目录，再把进程状态和实际业务请求对应起来。交互终端、系统服务和容器可能同时使用不同环境，即使执行文件名称一样，也不代表访问同一组资源。

## 二、技术分析与方案取舍

Type=simple 的入口通常不要再自行 daemonize，否则管理器跟踪的进程与实际服务可能分离。标准输出进入 journal 后，程序无需另开后台 shell 管理日志。User 和 WorkingDirectory 应先在本机验证存在且有相应权限；After=network.target 只是启动关系，不能证明数据库已经能连接。

若服务连续失败，应保留首个退出原因并限制重启频率，再从同一用户和目录复现。

变更应围绕已经定位的条件进行。先保存当前有效配置与一段故障日志，再修改一个变量，使用同一入口复测。服务重启只重新执行当前单元，单元文本改变后还需按管理器规则重新加载；网络配置改变也可能影响已有连接。每一步都应能说明它解决的是地址、权限、环境还是进程生命周期。

## 三、实现与排查的顺序

1. 先验证程序前台执行。
2. 显式指定工作目录和用户。
3. 配置适当的退出重启策略。
4. 用 journalctl 对齐开始与退出日志。

按这个顺序保留中间结果，可以区分输入条件、处理过程和最终输出。前一阶段的条件不成立时，先解释对应错误，再继续后面的试验；单次返回成功不足以覆盖整条链路。

### 最小示例

```ini
[Unit]
Description=Example application
After=network.target

[Service]
Type=simple
User=app
WorkingDirectory=/opt/example-app
ExecStart=/opt/example-app/bin/server
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
```

单元假定已存在 app 用户与相应程序路径，是结构示例。程序应在前台运行，network.target 不证明远端依赖已就绪。on-failure 处理异常退出，间隔控制重复失败频率；业务是否可用还需要独立请求验证。

## 四、验证和结果解释

进程 PID、监听地址、错误发生时间与退出状态适合形成一组关联证据。单次截图通常不足以解释间歇故障，持续观察可以发现状态转换和重复失败间隔。公开记录只保留必要错误类型与通用路径，认证信息、真实主机名和内部地址不进入文章。

| 需要验证的结果 | 保留的对照 | 不能由此推出的结论 |
| --- | --- | --- |
| 主机启动后仅有一个预期实例 | 固定输入与配置、对应输出 | 一次成功代表所有条件成功 |
| 权限与路径在服务环境中正确 | 中断前后状态与错误阶段 | 没有报错代表结果正确 |
| 连续失败能留下原因且不会无限高频重启 | 恢复后的同条件复测 | 临时恢复代表根因已经消失 |

故障复现时要区分稳定错误和偶发错误。稳定错误优先检查固定配置，偶发错误再看资源峰值、连接状态和时间变化。修复后既测正常路径，也验证启动失败、依赖不可达与重启条件，避免只在已有运行环境中成功。

## 五、适用边界与结论

需要图形会话的程序不宜直接套用系统级后台服务。密钥和密码不放进公开单元示例；依赖就绪仍应由程序或探针验证。

这条路径把“先验证程序前台执行”与“用 journalctl 对齐开始与退出日志”连在一起，中间保留可复查的条件。实施时优先确认“主机启动后仅有一个预期实例”，再检查“连续失败能留下原因且不会无限高频重启”；两者都满足，才能在当前样本与配置范围内评价方案。设备、数据或软件版本改变以后，相关假设需要重新验证。

## 参考资料

- [技术说明与实现资料 1](https://www.freedesktop.org/software/systemd/man/systemd.service.html)
