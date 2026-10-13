---
layout: post
title: systemd 服务连不上网络：研究环境变量差异
subtitle: 命令在终端能访问网络，交给 systemd 服务运行却失败。
date: 2023-07-19 08:00:00 +0800
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
updated_at: '2026-10-13T17:59:15+08:00'
verification: observed
privacy_reviewed: true
permalink: /tech/2026/08/28/systemd-proxy-environment/
excerpt: 命令在终端能访问网络，交给 systemd 服务运行却失败。
archive_date: '2023-07-19'
date_basis: simulated_weekly_archive
content_revision: 2
images:
- /img/tech-notes/systemd-proxy-environment.svg
---

命令在终端能访问网络，交给 systemd 服务运行却失败。我想先确认两次执行是否使用相同代理与环境，而不是立即重装应用或把问题归给远端服务。

## 研究与排查过程

研究从进程启动环境展开：交互 shell 配置可能提供代理，systemd 不会自动继承当前终端状态。方案对照服务用户、环境变量、执行路径、工作目录和日志，再用服务所处环境访问同一目标。浏览器或个人终端成功，不能替代后台进程的测试。

![systemd 服务连不上网络：研究环境变量差异研究路径示意](/img/tech-notes/systemd-proxy-environment.svg)

## 涉及的技术与取舍

采用 systemd 单元的 Environment 或 EnvironmentFile 明确服务需要的配置，并核对文件权限与加载时机。代理的协议、认证和实际端口应适合应用使用的网络库，配置更新后重新加载单元并重启相关服务。敏感认证数据不进入公开脚本，日志仅保留连接阶段和错误类别。

### 辅助检查示例

以下为通用示例，用于理解上述检查；变量、设备和参数需对应实际环境。

```ini
[Service]
Environment="HTTP_PROXY=http://127.0.0.1:PORT"
Environment="HTTPS_PROXY=http://127.0.0.1:PORT"
Environment="NO_PROXY=localhost,127.0.0.1"
```

## 这轮研究的结论

结论是对照终端与服务环境，可以快速识别运行上下文差异；配置代理后仍需独立验证 DNS、证书和目标协议。现有记录讨论了方法，未提供完整服务恢复结果，因此这篇不把环境变量方案写成已确认的唯一修复。

## 参考资料

- [systemd.exec 环境配置](https://www.freedesktop.org/software/systemd/man/latest/systemd.exec.html)
