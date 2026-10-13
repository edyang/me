---
layout: post
title: Claude Code 安装异常：研究 npm 与原生文件
subtitle: 全局卸载出现 ENOTEMPTY，随后启动又提示 claude native binary not installed。
date: 2023-09-13 08:00:00 +0800
author: edyang
header-style: text
catalog: true
tags:
- 开发工具
- Node.js
- 故障排查
tech_note: true
note_id: claude-code-native-binary-install
source_date: '2026-09-28'
source_dates:
- '2026-09-28'
published_at: '2026-10-12T12:51:43+08:00'
updated_at: '2026-10-13T17:59:15+08:00'
verification: partial
privacy_reviewed: true
permalink: /tech/2026/09/28/claude-code-native-binary-install/
excerpt: 全局卸载出现 ENOTEMPTY，随后启动又提示 claude native binary not installed。
archive_date: '2023-09-13'
date_basis: simulated_weekly_archive
content_revision: 2
images:
- /img/tech-notes/claude-code-native-binary-install.svg
---

全局卸载出现 ENOTEMPTY，随后启动又提示 claude native binary not installed。当时环境为 Node 22.22.2 与 npm 10.9.7，我需要先分清包目录清理问题与原生可执行文件缺失，避免一次重装掩盖两处失败。

## 研究与排查过程

先定位当前 node、claude 与 npm prefix，确认 NVM 所选版本对应哪套全局包。ENOTEMPTY 所处的重命名或清理阶段，需要核对正在运行的安装进程和具体目录。接下来检查 ignore-scripts 与 omit，判断可选依赖和 postinstall 是否被跳过，保留配置再处理明确故障目录。

![Claude Code 安装异常：研究 npm 与原生文件研究路径示意](/img/tech-notes/claude-code-native-binary-install.svg)

## 涉及的技术与取舍

技术路径包括 npm 平台可选依赖、postinstall 链接与 PATH 选择。当前官方安装说明描述了原生文件分发机制，保留 npm 方式时要检查依赖下载与脚本执行；若选择其它官方安装入口，也要确认命令最终指向哪一套安装。修复后先运行版本与 doctor，再另查认证和 API。

### 辅助检查示例

以下为通用示例，用于理解上述检查；变量、设备和参数需对应实际环境。

```bash
command -v node
command -v claude
npm prefix -g
npm config get ignore-scripts
npm config get omit
```

## 这轮研究的结论

记录提供了两处真实报错，没有最终修复回执。结论是包安装成功不等于命令可用，命令可用也不等于账号访问正常。排查应沿目录、依赖、可执行文件和运行健康逐段核验，不对未确认目录做大范围删除。

## 参考资料

- [Claude Code 官方安装说明](https://code.claude.com/docs/en/setup)
