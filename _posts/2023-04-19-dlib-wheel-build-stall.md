---
layout: post
title: ARM Linux 安装 dlib：分析 Building wheel 停滞
subtitle: ARM Linux 安装 dlib 时，终端长时间停在 Building wheel。
date: 2023-04-19 08:00:00 +0800
author: edyang
header-style: text
catalog: true
tags:
- Python
- Linux
- 编译
tech_note: true
note_id: dlib-wheel-build-stall
source_date: '2026-05-22'
source_dates:
- '2026-05-22'
published_at: '2026-10-13T08:02:56+08:00'
updated_at: '2026-10-13T17:59:15+08:00'
verification: partial
privacy_reviewed: true
permalink: /tech/2026/05/22/dlib-wheel-build-stall/
excerpt: ARM Linux 安装 dlib 时，终端长时间停在 Building wheel。
archive_date: '2023-04-19'
date_basis: simulated_weekly_archive
content_revision: 2
images:
- /img/tech-notes/dlib-wheel-build-stall.svg
---

ARM Linux 安装 dlib 时，终端长时间停在 Building wheel。我想判断到底还在正常编译，还是下载、工具链或内存出了问题，避免仅凭等待时间就结束进程并重新安装。

## 研究与排查过程

排查先把下载源码、准备构建依赖、CMake 配置、C++ 编译与 wheel 安装分开。pip 可能使用隔离构建环境，因此到构建阶段仍可能下载依赖。只有看见具体的 CMake 或编译器日志，才能更明确地判断进度；ARM 缺少某个匹配 wheel 也需要核对实际版本与索引。

![ARM Linux 安装 dlib：分析 Building wheel 停滞研究路径示意](/img/tech-notes/dlib-wheel-build-stall.svg)

## 涉及的技术与取舍

技术检查包括 Python 与 pip 所属环境、uname 架构、CMake/C++ 工具是否可用、编译进程活动和内存占用。若编译进程持续有 CPU 活动，终端安静未必是卡死；若进程退出或内核出现 OOM，再研究资源限制。需要重试时使用 verbose 收集第一条有效错误，避免原构建仍运行时再开第二份。

### 辅助检查示例

以下为通用示例，用于理解上述检查；变量、设备和参数需对应实际环境。

```bash
python -V
python -m pip --version
uname -m
cmake --version
c++ --version
ps -eo pid,ppid,stat,etime,comm | rg 'python|cmake|make|ninja|cc1plus|g\+\+'
free -h
```

```bash
python -m pip install dlib --verbose
```

## 这轮研究的结论

这轮确认了长时间处于构建提示，没有完整进程采样和安装结果，因此不能把源码编译认作唯一原因。结论是先用阶段日志与进程活动判断，再处理相应问题；最终在同一解释器下验证导入，才算完成依赖安装。

## 参考资料

- [dlib 官方编译说明](https://dlib.net/compile.html)
- [pip 构建系统接口](https://pip.pypa.io/en/stable/reference/build-system/)
