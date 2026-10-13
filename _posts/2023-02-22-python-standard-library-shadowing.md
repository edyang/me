---
layout: post
title: Python 同名模块遮蔽标准库的排查记录
subtitle: 安装依赖的排查中，我想用 platform.machine() 查看机器架构，却碰到导入异常。
date: 2023-02-22 08:00:00 +0800
author: edyang
header-style: text
catalog: true
tags:
- Python
- 故障排查
tech_note: true
note_id: python-standard-library-shadowing
source_date: '2026-04-03'
source_dates:
- '2026-04-03'
published_at: '2026-10-12T12:51:43+08:00'
updated_at: '2026-10-13T17:59:15+08:00'
verification: partial
privacy_reviewed: true
permalink: /tech/2026/04/03/python-standard-library-shadowing/
excerpt: 安装依赖的排查中，我想用 platform.machine() 查看机器架构，却碰到导入异常。
archive_date: '2023-02-22'
date_basis: simulated_weekly_archive
content_revision: 2
images:
- /img/tech-notes/python-standard-library-shadowing.svg
---

安装依赖的排查中，我想用 platform.machine() 查看机器架构，却碰到导入异常。项目里恰好有一个叫 platform 的模块，而同一时间 pip 又在超时。这两个问题一起出现，很容易让人误以为都是环境损坏。

## 研究与排查过程

处理思路先转向模块来源：打印解释器路径、platform.__file__ 和 sys.path 的前几项，再离开项目目录，用同一解释器重新测试。若来源随当前目录变化，就应检查本地同名文件或包。这样可以先回答“导入了哪个模块”，再讨论为什么该模块没有预期函数。

![Python 同名模块遮蔽标准库的排查记录研究路径示意](/img/tech-notes/python-standard-library-shadowing.svg)

## 涉及的技术与取舍

这里用到 Python 的模块搜索路径和导入机制。业务文件与标准库同名时，会在特定搜索顺序下遮蔽标准模块。拟采取的修正包括为业务包改名、同步导入引用并重启解释器。安装动作则通过 python -m pip 绑定当前解释器，避免一个环境里查导入、另一个环境里装依赖。

### 辅助检查示例

以下为通用示例，用于理解上述检查；变量、设备和参数需对应实际环境。

```python
import sys
import platform

print(sys.executable)
print(platform.__file__)
print(sys.path[:3])
```

## 这轮研究的结论

这轮发现了同名遮蔽的明确线索，也提出了改名和独立网络排查方法；没有最终安装回执。可复用的结论是把导入异常与下载失败拆开验证：前者查模块来源，后者查连接、索引和构建阶段，不能凭一次架构检测异常判断平台不受支持。

## 参考资料

- [Python 模块搜索路径](https://docs.python.org/3/tutorial/modules.html#the-module-search-path)
