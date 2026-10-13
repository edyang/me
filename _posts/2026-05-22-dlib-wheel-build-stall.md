---
layout: post
title: dlib 安装停在 Building wheel：先确认编译是否仍在运行
subtitle: 下载超时、本地编译和内存不足，处理方式不同；仅凭长时间无新输出不能定性。
date: 2026-05-22 08:00:00 +0800
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
updated_at: '2026-10-13T08:02:56+08:00'
verification: partial
privacy_reviewed: true
permalink: /tech/2026/05/22/dlib-wheel-build-stall/
excerpt: 下载超时、本地编译和内存不足，处理方式不同；仅凭长时间无新输出不能定性。
---

在 ARM Linux 环境安装 dlib 时，我遇到终端长时间停在 `Building wheel` 的情况。这个提示已经提供了一个排查入口：pip 正在构建安装包，但还不能据此断定是网络卡住、编译器挂起，或者没有可用的预编译包。

## 先记录安装所处的阶段

下载源码、准备构建依赖、编译 C++ 扩展和安装 wheel 是不同阶段。pip 的构建过程还可能创建隔离环境并下载构建依赖，所以不能认为看到 wheel 字样以后就完全不涉及网络。

dlib 官方说明 Python 构建需要 CMake 和可用的 C++ 编译器。如果实际日志已经出现 CMake 配置或 C++ 编译行，才有更强证据表明本地编译已经开始。ARM 环境缺少匹配 wheel 是一种可能解释；要结合 Python 版本、架构、所用索引和具体版本确认，不能写成所有 ARM 平台都没有 wheel。

## 用进程活动判断，不靠等待时长猜测

```bash
python -V
python -m pip --version
uname -m
cmake --version
c++ --version
ps -eo pid,ppid,stat,etime,comm | rg 'python|cmake|make|ninja|cc1plus|g\+\+'
free -h
```

这些是通用的只读检查。先在本机观察编译进程的 CPU 使用和日志变化；持续有编译活动、没有错误时，安静的终端可能只是输出较少。如果内存不足、进程消失或系统记录 OOM，再按资源问题处理。资源紧张时应按构建工具实际支持的方式限制并行，不能随意给 pip 添加一个通用“线程数”参数。

需要重新安装以收集日志时，可以使用详细输出：

```bash
python -m pip install dlib --verbose
```

这会执行安装，应在预期的虚拟环境中运行。不要在原安装仍在进行时再启动第二份构建。若是 CMake 或编译器缺失，补齐工具；若是依赖下载超时，检查相应下载步骤；若已有编译错误，则从第一条有效错误定位，而不是反复清缓存。

## 验证边界

原交流确认了长时间停在构建提示，未提供完整日志、进程采样和最终安装结果。源码编译是当时的解释方向，不是已经证实的唯一原因。安装完成后还应在同一个解释器下验证导入，不能以另一环境的成功代替本环境结果。

## 参考资料

- [dlib 官方编译说明](https://dlib.net/compile.html)
- [pip 构建系统接口](https://pip.pypa.io/en/stable/reference/build-system/)
