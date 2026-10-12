---
layout: post
title: 终端能访问、systemd 服务却卡住：代理环境没有自动继承
subtitle: 交互式 Shell 中的代理变量，不一定存在于 systemd 服务进程里。
date: 2026-08-28 08:00:00 +0800
author: edyang
header-style: text
catalog: true
tags:
- Linux
- systemd
- 网络
tech_note: true
note_id: systemd-proxy-environment
source_date: '2026-08-28'
source_dates:
- '2026-08-28'
published_at: '2026-10-12T12:51:43+08:00'
updated_at: '2026-10-12T12:51:43+08:00'
verification: observed
privacy_reviewed: true
permalink: /tech/2026/08/28/systemd-proxy-environment/
excerpt: 交互式 Shell 中的代理变量，不一定存在于 systemd 服务进程里。
---

一次排查中，同一个 CLI 在终端可用，作为 systemd 服务执行却一直卡住。最终补上服务环境中的代理变量后，最小请求能够返回。这里最值得复用的是检查方法，而不是某个具体代理端口。

## 两个进程的环境并不相同

终端可能从 Shell 配置读取代理；systemd 启动服务时，不会简单复制当前终端的全部变量。工作目录、PATH、HOME、代理和证书设置都可能不同。

## 用 override 明确服务配置

```ini
[Service]
Environment="HTTP_PROXY=http://127.0.0.1:PORT"
Environment="HTTPS_PROXY=http://127.0.0.1:PORT"
Environment="NO_PROXY=localhost,127.0.0.1"
```

`PORT` 是需要替换的示例占位符。还要确认当前 CLI 实际支持哪些代理变量，是否需要小写形式，以及服务所在网络命名空间能否访问这个地址。若服务在容器里，127.0.0.1 指向的是容器自身。

更改配置后执行 daemon-reload 并重启该服务，再用与业务相同的用户和服务环境做最小请求。日志中保留开始、超时和完成时间，避免只凭“没有报错”认定成功。

## NO_PROXY 要匹配实际内部访问需求

本机、局域网服务或服务发现地址不应误走代理。配置应由网络需求决定，不能把所有流量全部塞进一个代理，也不要将带认证信息的代理地址写进公开文章。

这次历史反馈确认：补齐环境后，最小请求返回了结果。但其它业务请求是否稳定，仍应独立测试。把终端环境和服务环境做一次对照，通常可以省下大量盲目重装。

## 参考资料

- [systemd.exec 环境配置](https://www.freedesktop.org/software/systemd/man/latest/systemd.exec.html)
