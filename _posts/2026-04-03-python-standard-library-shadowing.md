---
layout: post
title: Python 项目叫 platform，为什么会影响 pip 排查
subtitle: 同名模块可能遮蔽标准库。排查安装问题时，应先确认实际加载的模块文件。
date: 2026-04-03 08:00:00 +0800
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
updated_at: '2026-10-12T12:51:43+08:00'
verification: partial
privacy_reviewed: true
permalink: /tech/2026/04/03/python-standard-library-shadowing/
excerpt: 同名模块可能遮蔽标准库。排查安装问题时，应先确认实际加载的模块文件。
---

一次 Python 安装排查中，本来想用 `platform.machine()` 确认架构，却得到异常。项目目录里恰好存在一个名为 `platform` 的模块。安装超时和标准库导入异常同时出现，很容易被误判成同一个问题。

## 先看模块从哪里加载

Python 查找模块时会考虑当前执行环境的搜索路径。如果本地模块与标准库同名，导入到的内容可能不是预期的库。检查 `__file__` 比反复重装依赖更直接。

```python
import sys
import platform

print(sys.executable)
print(platform.__file__)
print(sys.path[:3])
```

可以离开项目目录后，用相同解释器再执行一次。若模块来源随目录变化，就应检查本地的同名文件或包。除了 `platform`，`json.py`、`logging.py`、`socket.py` 等名字也常引起类似问题。

## 导入问题和下载问题分别验证

模块遮蔽会影响环境检测或程序运行，下载超时则要检查网络、索引和连接过程。先恢复正确的导入，再观察 pip 真正报的是超时、版本不存在，还是构建失败。不要因为一个架构检查函数坏了，就判断机器架构不支持。

## 改名之后仍要核对引用

把业务模块改成明确的名称后，更新代码中的导入并重启解释器或开发服务。记录当前虚拟环境路径，使用 `python -m pip` 保证安装动作属于同一个解释器。

当时定位到了同名遮蔽的线索，也提出了改名与网络检查方案；没有最终修复回执。这条笔记保留的是诊断方法，而不是一次已验证完成的安装记录。

## 参考资料

- [Python 模块搜索路径](https://docs.python.org/3/tutorial/modules.html#the-module-search-path)
