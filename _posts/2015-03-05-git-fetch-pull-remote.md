---
layout: post
title: 研究 Git：fetch、pull 与远端跟踪分支
subtitle: 看到 origin/master 有新提交，不代表本地 master 已经包含这些变化。
date: 2015-03-05 08:00:00 +0800
author: edyang
header-style: text
catalog: true
tags:
- Git
- 版本管理
tech_note: true
note_id: git-fetch-pull-remote
permalink: /tech/2015/03/05/git-fetch-pull-remote/
excerpt: 看到 origin/master 有新提交，不代表本地 master 已经包含这些变化。
privacy_reviewed: true
content_revision: 3
images:
- /img/tech-notes/git-fetch-pull-remote.svg
technology_since: '2014-10-01'
---

看到 origin/master 有新提交，不代表本地 master 已经包含这些变化。两者是不同引用。

本文使用Git 2.x 与独立演示仓库。Git（分布式版本管理）保存提交对象和引用，工作区、暂存区与提交历史不是同一份状态。每次操作先判断它改变哪个区域，再决定是否适合当前协作情境。

## 1. 从现象推到机制

fetch 获取远端对象并更新远端跟踪引用，通常不会替你整合当前分支。pull 在获取后继续执行配置决定的整合动作。先 fetch 再比较，可以在合并或变基前看清双方差异。

![研究 Git：fetch、pull 与远端跟踪分支的处理、反馈与观察关系](/img/tech-notes/git-fetch-pull-remote.svg)

图中的四个节点分别表示远端仓库、获取对象、跟踪引用、显式整合。顺着实线检查输入如何变成输出，再沿虚线核对反馈条件。图示表达的是本文讨论的关系，不是实测曲线或现场截图。

## 2. 最小实现与输入条件

在演示仓库获取远端后，分别查看当前分支领先和落后的提交。执行整合前先检查工作区，避免把未完成修改与集成冲突混在一起。

```bash
git fetch origin
git log --oneline HEAD..origin/master
git log --oneline origin/master..HEAD
git status
```

示例在没有私人资料的临时仓库执行。先看 status、diff 与 log，再运行改变状态的命令；共享历史优先新增提交表达修复，不用改写历史掩盖已经发生的变化。

## 3. 用对照区分原因

下表列出需要主动改变的条件。预期行为来自机制分析，复现时还需记录运行环境和原始输出，不能将预期当作已经测得的结果。

| 改变的条件 | 需要验证的行为 |
| --- | --- |
| 远端新增而本地未整合 | 本地文件可以暂时保持不变 |
| 双方都产生新提交 | 需要明确选择整合方式 |
| 工作区仍有未提交修改 | 先保护当前工作再整合 |

### 对照 1：远端新增而本地未整合

本地文件可以暂时保持不变。观察时记录当前 HEAD 与远端跟踪引用。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 2：双方都产生新提交

需要明确选择整合方式。观察时记录两边独有提交与共同祖先。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 3：工作区仍有未提交修改

先保护当前工作再整合。观察时记录status 与本地差异。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。

## 4. 适用条件与取舍

远端跟踪引用是最近一次获取到的认知，不是实时远端状态。准备推送或发布时仍要重新确认当前远端头。

一次正常运行只覆盖了这组输入。继续扩展前，应把上面的异常对照保留下来，尤其关注“工作区仍有未提交修改”这一分支。后续方案若改变了图中任意一处依赖，原来的判断就要重新验证，不能仅凭界面相似或返回值相同沿用结论。

## 同月延伸

- [研究 Git：用二分查找定位回归提交](/tech/2015/03/15/git-bisect-regression/)
- [研究 Git：小提交应该按业务意图拆分](/tech/2015/03/25/git-small-commits-review/)

## 参考资料

1. [Pro Git 第二版](https://git-scm.com/book/en/v2)
2. [Git 2.2.0 版本说明](https://github.com/git/git/blob/v2.2.0/Documentation/RelNotes/2.2.0.txt)
