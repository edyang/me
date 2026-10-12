---
layout: post
title: Mac 上分开使用两个 Chrome 空间，并放到 Dock
subtitle: Profile 适合日常账号分开，独立 user-data-dir 可以进一步分开浏览器数据目录。
date: 2026-09-28 08:00:00 +0800
author: edyang
header-style: text
catalog: true
tags:
- macOS
- Chrome
- 效率工具
tech_note: true
note_id: mac-chrome-independent-profiles
source_date: '2026-09-28'
source_dates:
- '2026-09-28'
published_at: '2026-10-12T12:51:43+08:00'
updated_at: '2026-10-12T12:51:43+08:00'
verification: proposal
privacy_reviewed: true
permalink: /tech/2026/09/28/mac-chrome-independent-profiles/
excerpt: Profile 适合日常账号分开，独立 user-data-dir 可以进一步分开浏览器数据目录。
---

工作和个人账号都需要常驻时，反复退出登录并不方便。Chrome 的 Profile 可以分别保存浏览历史、扩展和登录状态；如果希望有两个独立启动入口，也可以使用不同的数据目录。

## 先选择需要的隔离程度

日常使用可以在 Chrome 头像菜单添加两个 Profile，并使用不同名称和主题色。若希望目录、配置和启动过程也明确分开，再使用不同的 `--user-data-dir`。

```bash
open -na "Google Chrome" --args --user-data-dir="$HOME/ChromeSpaces/work"
open -na "Google Chrome" --args --user-data-dir="$HOME/ChromeSpaces/personal"
```

这里仅读取 HOME 来构造用户目录，不修改系统变量。两个进程不要使用同一个数据目录。

## 做成可以点击的应用入口

在“脚本编辑器”中创建两个简单脚本，分别执行对应的启动命令，导出为应用程序，再拖到 Dock。实际脚本要正确处理路径中的空格；第一次启动时确认打开的是对应空间。

## 核对已有数据再迁移

不要直接复制正在运行的 Chrome 数据目录。先关闭浏览器并保存必要资料，再决定使用同步或导出。两套本地目录只是浏览器数据分开，不等于操作系统层的安全隔离。

原交流给出了方案，但没有两个快捷方式实际完成的回执。这篇保留可操作路径，账号名称和个人数据不在公开内容中展示。

## 参考资料

- [Chrome Profile 帮助](https://support.google.com/chrome/answer/2364824)
