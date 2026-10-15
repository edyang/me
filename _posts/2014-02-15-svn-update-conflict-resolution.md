---
layout: post
title: SVN 冲突处理：先理解双方修改，再标记解决
subtitle: 更新后出现冲突文件，删除冲突标记只是文本清理。
date: 2014-02-15 08:00:00 +0800
author: edyang
header-style: text
catalog: true
tags:
- SVN
- 版本管理
tech_note: true
note_id: svn-update-conflict-resolution
permalink: /tech/2014/02/15/svn-update-conflict-resolution/
excerpt: 更新后出现冲突文件，删除冲突标记只是文本清理。
privacy_reviewed: true
content_revision: 3
images:
- /img/tech-notes/svn-update-conflict-resolution.svg
technology_since: '2013-01-01'
---

更新后出现冲突文件，删除冲突标记只是文本清理。真正的工作是确认双方意图如何合并。

本文使用Subversion 1.7 客户端与独立测试仓库。SVN（集中式版本管理）的工作副本保存本地修改和基准版本，仓库保存已提交历史。工作副本中的文件状态与仓库修订号需要分别理解。

## 1. 从现象推到机制

SVN 尝试把仓库新修订与本地修改合并，重叠编辑可能产生文本冲突。语义冲突则可能完全没有标记，例如两人分别改了调用参数与被调方法约定。标记 resolved 不会验证程序正确。

![SVN 冲突处理：先理解双方修改，再标记解决的处理、反馈与观察关系](/img/tech-notes/svn-update-conflict-resolution.svg)

图中的四个节点分别表示更新请求、三方比较、人工合并、验证解决。顺着实线检查输入如何变成输出，再沿虚线核对反馈条件。图示表达的是本文讨论的关系，不是实测曲线或现场截图。

## 2. 最小实现与输入条件

先备份本地修改，比较基准、本地和远端三个版本。合并后编译并执行相关场景，再把路径标记为已经解决。

```bash
svn diff > local-change.patch
svn update
svn status
# 人工合并并验证后
svn resolve --accept working src/OrderService.java
```

以下命令应在专用工作副本执行。先运行 status 和 diff 看清变化，再做更新、合并与提交；不要为了清除冲突标记而放弃尚未理解的双方修改。

## 3. 用对照区分原因

下表列出需要主动改变的条件。预期行为来自机制分析，复现时还需记录运行环境和原始输出，不能将预期当作已经测得的结果。

| 改变的条件 | 需要验证的行为 |
| --- | --- |
| 双方改不同的行 | 文本合并成功仍可能语义不兼容 |
| 双方改同一段规则 | 需要人工选择或重构共同逻辑 |
| 仅标记解决未编译 | 仍可能留下语法或规则错误 |

### 对照 1：双方改不同的行

文本合并成功仍可能语义不兼容。观察时记录调用契约与相关行为。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 2：双方改同一段规则

需要人工选择或重构共同逻辑。观察时记录三个版本各自的业务意图。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 3：仅标记解决未编译

仍可能留下语法或规则错误。观察时记录构建结果与业务对照。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。

## 4. 适用条件与取舍

不要为尽快提交而整体选择 mine 或 theirs。确需保留某一方时，也要确认另一方的改动已通过其他位置保留或被明确放弃。

一次正常运行只覆盖了这组输入。继续扩展前，应把上面的异常对照保留下来，尤其关注“仅标记解决未编译”这一分支。后续方案若改变了图中任意一处依赖，原来的判断就要重新验证，不能仅凭界面相似或返回值相同沿用结论。

## 同月延伸

- [SVN 入门：工作副本、状态和提交范围](/tech/2014/02/05/svn-working-copy-status/)
- [SVN 分支与标签：复制便宜，合并仍要有依据](/tech/2014/02/25/svn-branch-tag-merge/)

## 参考资料

1. [Version Control with Subversion 1.7](https://svnbook.red-bean.com/en/1.7/)
2. [Apache Subversion 文档](https://subversion.apache.org/docs/)
