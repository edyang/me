---
layout: post
title: SVN 入门：工作副本、状态和提交范围
subtitle: 文件保存在本地，不代表已经进入 SVN 历史。
date: 2014-02-05 08:00:00 +0800
author: edyang
header-style: text
catalog: true
tags:
- SVN
- 版本管理
tech_note: true
note_id: svn-working-copy-status
permalink: /tech/2014/02/05/svn-working-copy-status/
excerpt: 文件保存在本地，不代表已经进入 SVN 历史。
privacy_reviewed: true
content_revision: 3
images:
- /img/tech-notes/svn-working-copy-status.svg
technology_since: '2013-01-01'
---

文件保存在本地，不代表已经进入 SVN 历史。提交前先理解工作副本的几种状态。

本文使用Subversion 1.7 客户端与独立测试仓库。SVN（集中式版本管理）的工作副本保存本地修改和基准版本，仓库保存已提交历史。工作副本中的文件状态与仓库修订号需要分别理解。

## 1. 从现象推到机制

未跟踪文件、已修改文件、计划添加与计划删除分别需要不同操作。修订号属于仓库提交历史，而一个工作副本可能混合多个修订的文件。盲目提交整个目录，容易带上生成文件和临时配置。

![SVN 入门：工作副本、状态和提交范围的处理、反馈与观察关系](/img/tech-notes/svn-working-copy-status.svg)

图中的四个节点分别表示本地文件、状态检查、差异审查、仓库历史。顺着实线检查输入如何变成输出，再沿虚线核对反馈条件。图示表达的是本文讨论的关系，不是实测曲线或现场截图。

## 2. 最小实现与输入条件

先查看 status，再逐文件检查 diff。新增源码先 add，生成目录用忽略规则处理，演示提交只包含一个完整的小改动。

```bash
svn status
svn diff
svn add src/NewService.java
svn commit src/NewService.java -m "Add demo service"
```

以下命令应在专用工作副本执行。先运行 status 和 diff 看清变化，再做更新、合并与提交；不要为了清除冲突标记而放弃尚未理解的双方修改。

## 3. 用对照区分原因

下表列出需要主动改变的条件。预期行为来自机制分析，复现时还需记录运行环境和原始输出，不能将预期当作已经测得的结果。

| 改变的条件 | 需要验证的行为 |
| --- | --- |
| 出现问号文件 | 文件尚未纳入版本管理 |
| 已保存代码但未提交 | 其他工作副本仍看不到修改 |
| 工作副本修订号不一致 | 不必然表示仓库损坏 |

### 对照 1：出现问号文件

文件尚未纳入版本管理。观察时记录status 显示的状态列。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 2：已保存代码但未提交

其他工作副本仍看不到修改。观察时记录仓库日志与本地 diff。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 3：工作副本修订号不一致

不必然表示仓库损坏。观察时记录各路径的更新与提交历史。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。

## 4. 适用条件与取舍

忽略规则不等于删除已经跟踪的文件。配置中若曾提交敏感内容，需要按专门流程处理历史暴露，不能只加入忽略列表。

一次正常运行只覆盖了这组输入。继续扩展前，应把上面的异常对照保留下来，尤其关注“工作副本修订号不一致”这一分支。后续方案若改变了图中任意一处依赖，原来的判断就要重新验证，不能仅凭界面相似或返回值相同沿用结论。

## 同月延伸

- [SVN 冲突处理：先理解双方修改，再标记解决](/tech/2014/02/15/svn-update-conflict-resolution/)
- [SVN 分支与标签：复制便宜，合并仍要有依据](/tech/2014/02/25/svn-branch-tag-merge/)

## 参考资料

1. [Version Control with Subversion 1.7](https://svnbook.red-bean.com/en/1.7/)
2. [Apache Subversion 文档](https://subversion.apache.org/docs/)
