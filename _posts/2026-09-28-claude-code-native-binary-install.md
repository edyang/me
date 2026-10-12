---
layout: post
title: Claude Code 安装失败：ENOTEMPTY 和 native binary 缺失分别处理
subtitle: 包目录重命名失败与原生二进制缺失，不应被笼统当成账号权限问题。
date: 2026-09-28 08:00:00 +0800
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
updated_at: '2026-10-12T12:51:43+08:00'
verification: partial
privacy_reviewed: true
permalink: /tech/2026/09/28/claude-code-native-binary-install/
excerpt: 包目录重命名失败与原生二进制缺失，不应被笼统当成账号权限问题。
---

一次全局安装维护中，npm 卸载报 `ENOTEMPTY`，随后启动命令提示 `claude native binary not installed`。当时使用 Node 22.22.2 和 npm 10.9.7。两条错误位于不同阶段。

## ENOTEMPTY 先检查安装目录与进程

这条错误发生在包目录重命名或清理阶段。先确认没有正在执行的安装或相关进程，再定位当前 Node 版本的全局安装目录。使用 NVM 时，多个版本可能各有一套全局包与命令。

```bash
command -v node
command -v claude
npm prefix -g
npm config get ignore-scripts
npm config get omit
```

检查输出时不要公开个人路径和配置中的凭据。清理前保留配置，且只处理明确属于故障包的目录，不使用大范围删除命令。

## 原生文件缺失再看 optional 与 postinstall

当前官方说明，npm 分发通过平台 optional dependency 获取原生二进制，并由 postinstall 链接。跳过 scripts 或省略 optional dependency，都可能导致主包存在但可执行文件缺失。

修复应按当前官方安装方式进行。保留 npm 方式时，要确认 optional dependency 和脚本能执行；选择原生安装器时，要清楚 PATH 指向哪套安装，避免多个入口互相覆盖。

## 验证不要只看 npm 成功退出

用 `claude --version` 验证可执行文件，再运行 `claude doctor` 检查安装健康。CLI 能运行以后，账号认证和 API 访问应另行检查。

原交流没有最终修复成功反馈，因此本文没有把重装命令写成已验证结果。

## 参考资料

- [Claude Code 官方安装说明](https://code.claude.com/docs/en/setup)
