---
layout: post
title: 研究多入口文章发布的一致性与核验
subtitle: 一篇文章同时进入网站和多个发布渠道时，分别维护正文容易漏同步。
date: 2023-09-06 08:00:00 +0800
author: edyang
header-style: text
catalog: true
tags:
- Agent
- 自动化
- GitHub
tech_note: true
note_id: article-publishing-package-hash
source_date: '2026-09-23'
source_dates:
- '2026-09-23'
- '2026-10-09'
published_at: '2026-10-12T12:51:43+08:00'
updated_at: '2026-10-13T17:59:15+08:00'
verification: notes
privacy_reviewed: true
permalink: /tech/2026/09/23/article-publishing-package-hash/
excerpt: 一篇文章同时进入网站和多个发布渠道时，分别维护正文容易漏同步。
archive_date: '2023-09-06'
date_basis: simulated_weekly_archive
content_revision: 2
images:
- /img/tech-notes/article-publishing-package-hash.svg
---

一篇文章同时进入网站和多个发布渠道时，分别维护正文容易漏同步。我研究如何保留唯一内容源，追踪页面、素材与投递结果，避免仓库已有文件就被误报为上线。

## 研究与排查过程

过程先区分稿件完成、构建完成、提交、远端草稿、公开发布和线上验证。页面最终构建后再计算摘要，素材检查真实格式与完整解码。每个阶段保存回执，同题更新继续使用稳定标识与 URL，未知状态先查询，避免失败重试不断创建重复文章。

![研究多入口文章发布的一致性与核验研究路径示意](/img/tech-notes/article-publishing-package-hash.svg)

## 涉及的技术与取舍

技术涉及唯一内容源、SHA256 文件摘要、稳定内容 ID、构建校验与幂等发布。摘要可以识别绑定内容是否改变，不能替代语义审查；图片扩展名同样不能证明文件完整。适配层处理平台格式差异，公共正文与实际素材保持对应，状态记录体现每一步真实完成情况。

## 这轮研究的结论

结论是内容生成、提交与部署必须分别可观察。线上检查核对标题、日期、正文和图片，页面可打开而素材丢失仍不完整。这篇整理通用发布工程方法，未公开账号和内部接口；后续自动任务也应按同一套完成标准汇报。

## 参考资料

- [GitHub Pages 与 Jekyll](https://docs.github.com/en/pages/setting-up-a-github-pages-site-with-jekyll/about-github-pages-and-jekyll)
